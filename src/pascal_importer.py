import os

import numpy as np
import supervisely as sly
from supervisely.io.fs import get_file_name, get_file_name_with_ext
import xml.etree.ElementTree as ET

import globals as g
import init_ui_progress


# returns mapping: (r, g, b) color -> some (row, col) for each unique color except black
def get_col2coord(img):
    img = img.astype(np.int32)
    h, w = img.shape[:2]
    colhash = img[:, :, 0] * 256 * 256 + img[:, :, 1] * 256 + img[:, :, 2]
    unq, unq_inv, unq_cnt = np.unique(colhash, return_inverse=True, return_counts=True)
    indxs = np.split(np.argsort(unq_inv), np.cumsum(unq_cnt[:-1]))
    col2indx = {unq[i]: indxs[i][0] for i in range(len(unq))}
    return {
        (col // (256 ** 2), (col // 256) % 256, col % 256): (indx // w, indx % w)
        for col, indx in col2indx.items()
        if col != 0
    }


default_classes_colors = {
    "neutral": (224, 224, 192),
    "aeroplane": (128, 0, 0),
    "bicycle": (0, 128, 0),
    "bird": (128, 128, 0),
    "boat": (0, 0, 128),
    "bottle": (128, 0, 128),
    "bus": (0, 128, 128),
    "car": (128, 128, 128),
    "cat": (64, 0, 0),
    "chair": (192, 0, 0),
    "cow": (64, 128, 0),
    "diningtable": (192, 128, 0),
    "dog": (64, 0, 128),
    "horse": (192, 0, 128),
    "motorbike": (64, 128, 128),
    "person": (192, 128, 128),
    "pottedplant": (0, 64, 0),
    "sheep": (128, 64, 0),
    "sofa": (0, 192, 0),
    "train": (128, 192, 0),
    "tvmonitor": (0, 64, 128),
}

MASKS_EXTENSION = ".png"


class ImporterPascalVOCSegm:
    def __init__(self):
        self.lists_dir = os.path.join(
            g.storage_dir, "VOCdevkit", "VOC2012", "ImageSets", "Segmentation"
        )
        self.imgs_dir = os.path.join(
            g.storage_dir, "VOCdevkit", "VOC2012", "JPEGImages"
        )
        self.anns_dir = os.path.join(
            g.storage_dir, "VOCdevkit", "VOC2012", "Annotations"
        )
        self.segm_dir = os.path.join(
            g.storage_dir, "VOCdevkit", "VOC2012", "SegmentationClass"
        )
        self.inst_dir = os.path.join(
            g.storage_dir, "VOCdevkit", "VOC2012", "SegmentationObject"
        )
        self.colors_file = os.path.join(
            g.storage_dir, "VOCdevkit", "VOC2012", "colors.txt"
        )
        self.with_instances = os.path.isdir(self.inst_dir)
        sly.logger.info(
            f'Will import data {"with" if self.with_instances else "without"} instance info.'
        )

        self.obj_classes = sly.ObjClassCollection()
        self._read_datasets()
        self._read_colors()

    def _read_datasets(self):
        self.src_datasets = {}
        if not os.path.isdir(self.lists_dir):
            raise RuntimeError(
                f"There is no directory {self.lists_dir}, but it is necessary"
            )

        for filename in os.listdir(self.lists_dir):
            if filename.endswith(".txt"):
                ds_name = os.path.splitext(filename)[0]
                file_path = os.path.join(self.lists_dir, filename)
                sample_names = list(
                    filter(None, map(str.strip, open(file_path, "r").readlines()))
                )
                self.src_datasets[ds_name] = sample_names
                sly.logger.info(
                    f'Found source dataset "{ds_name}" with {len(sample_names)} sample(s).'
                )

    def _read_colors(self):
        if os.path.isfile(self.colors_file):
            sly.logger.info("Will try to read segmentation colors from provided file.")
            in_lines = filter(
                None, map(str.strip, open(self.colors_file, "r").readlines())
            )
            in_splitted = (x.split() for x in in_lines)
            # Format: {name: (R, G, B)}, values [0; 255]
            self.cls2col = {
                x[0]: (int(x[1]), int(x[2]), int(x[3])) for x in in_splitted
            }
        else:
            sly.logger.info("Will use default PascalVOC color mapping.")
            self.cls2col = default_classes_colors

        obj_classes_list = [
            sly.ObjClass(name=class_name, geometry_type=sly.AnyGeometry, color=color)
            for class_name, color in self.cls2col.items()
        ]
        self.obj_classes = self.obj_classes.add_items(obj_classes_list)

        sly.logger.info(
            f"Determined {len(self.cls2col)} class(es).",
            extra={"classes": list(self.cls2col.keys())},
        )

        self.color2class_name = {v: k for k, v in self.cls2col.items()}

    def _get_ann(self, img_path, ann_path, segm_path, inst_path, state):

        segmentation_img = sly.image.read(segm_path)

        if inst_path is not None:
            instance_img = sly.image.read(inst_path)
            colored_img = instance_img
            instance_img16 = instance_img.astype(np.uint16)
            col2coord = get_col2coord(instance_img16)
            curr_col2cls = (
                (col, self.color2class_name.get(tuple(segmentation_img[coord])))
                for col, coord in col2coord.items()
            )
            curr_col2cls = {
                k: v for k, v in curr_col2cls if v is not None
            }  # _instance_ color -> class name
        else:
            colored_img = segmentation_img
            segmentation_img = segmentation_img.astype(np.uint16)
            colors = list(get_col2coord(segmentation_img).keys())
            curr_col2cls = {
                curr_col: self.color2class_name[curr_col] for curr_col in colors
            }

        ann = sly.Annotation.from_img_path(img_path)

        for color, class_name in curr_col2cls.items():
            mask = np.all(
                colored_img == color, axis=2
            )  # exact match (3-channel img & rgb color)
            bitmap = sly.Bitmap(data=mask)
            obj_class = sly.ObjClass(name=class_name, geometry_type=sly.AnyGeometry)
            if state["needBboxes"]:
                ann = read_bbox(ann, ann_path, obj_class)
            ann = ann.add_label(sly.Label(bitmap, obj_class))
            #  clear used pixels in mask to check missing colors, see below
            colored_img[mask] = (0, 0, 0)

        if np.sum(colored_img) > 0:
            sly.logger.warn(
                "Not all objects or classes are captured from source segmentation."
            )

        return ann

    def convert(self, state):
        out_project = sly.Project(
            os.path.join(g.storage_dir, "SLY_PASCAL"), sly.OpenMode.CREATE
        )

        images_filenames = {}
        for image_path in sly.fs.list_files(self.imgs_dir):
            image_name_noext = sly.fs.get_file_name(image_path)
            if image_name_noext in images_filenames:
                raise RuntimeError(
                    "Multiple image with the same base name {!r} exist.".format(
                        image_name_noext
                    )
                )
            images_filenames[image_name_noext] = image_path

        for ds_name, sample_names in self.src_datasets.items():
            if len(sample_names) == 0:
                continue
            if state["mode"] == "public":
                if ds_name == "trainval" and state["trainval"] is False:
                    continue
                if ds_name == "train" and state["train"] is False:
                    continue
                if ds_name == "val" and state["val"] is False:
                    continue
                if ds_name == "test" and state["test"] is False:
                    continue
            ds = out_project.create_dataset(ds_name)
            percent_counter = 0
            if state["mode"] == "custom":
                state["samplePercent"] = 100
            sample_percent = int(len(sample_names) * (state["samplePercent"] / 100))
            progress_items_cb = init_ui_progress.get_progress_cb(
                g.api, g.task_id, f'Converting dataset: "{ds_name}"', sample_percent
            )
            for sample_name in sample_names:
                percent_counter += 1
                try:
                    src_img_path = images_filenames[get_file_name(sample_name)]
                except:
                    src_img_path = images_filenames[sample_name]
                src_img_filename = os.path.basename(src_img_path)
                ann_path = os.path.join(self.anns_dir, f"{get_file_name_with_ext(src_img_path)}.xml")
                if not os.path.exists(ann_path):
                    ann_path = os.path.join(self.anns_dir, f"{get_file_name(src_img_path)}.xml")
                segm_path = os.path.join(self.segm_dir, sample_name + MASKS_EXTENSION)

                inst_path = None
                if self.with_instances:
                    inst_path = os.path.join(
                        self.inst_dir, sample_name + MASKS_EXTENSION
                    )

                if all(
                        (x is None) or os.path.isfile(x)
                        for x in [src_img_path, segm_path, inst_path]
                ) and state["needMasks"]:
                    try:
                        ann = self._get_ann(src_img_path, ann_path, segm_path, inst_path, state)
                        ds.add_item_file(src_img_filename, src_img_path, ann=ann)
                    except Exception as e:
                        exc_str = str(e)
                        sly.logger.warn(
                            f"Input sample skipped due to error: {exc_str}",
                            exc_info=True,
                            extra={
                                "exc_str": exc_str,
                                "dataset_name": ds_name,
                                "image": src_img_path,
                            },
                        )
                elif state["needBboxes"] and os.path.exists(ann_path):
                    ann = sly.Annotation.from_img_path(src_img_path)
                    ann = read_bbox(ann, ann_path)
                    ds.add_item_file(src_img_filename, src_img_path, ann=ann)
                else:
                    ds.add_item_file(src_img_filename, src_img_path, ann=None)
                    # sly.logger.warning("Processing '{}' skipped because no corresponding mask found."
                    #                   .format(src_img_filename))

                progress_items_cb(1)
                if percent_counter == sample_percent:
                    break
            sly.logger.info(f'Dataset "{ds_name}" samples processing is done.', extra={})

        out_meta = sly.ProjectMeta(obj_classes=self.obj_classes)
        out_project.set_meta(out_meta)
        sly.logger.info("Pascal VOC samples processing is done.", extra={})


def start(state):
    importer = ImporterPascalVOCSegm()
    importer.convert(state)
    sly.report_import_finished()


def read_bbox(sly_ann, ann_path, obj_class=None):
    tree = ET.parse(ann_path)
    root = tree.getroot()
    for boxes in root.iter('object'):
        ymin, xmin, ymax, xmax = None, None, None, None
        ymin = int(boxes.find("bndbox/ymin").text)
        xmin = int(boxes.find("bndbox/xmin").text)
        ymax = int(boxes.find("bndbox/ymax").text)
        xmax = int(boxes.find("bndbox/xmax").text)
        if obj_class is None:
            obj_class_name = str(boxes.find("name").text)
            obj_class = sly.ObjClass(obj_class_name, sly.AnyGeometry)

        rectangle = sly.Rectangle(ymin, xmin, ymax, xmax)
        sly_ann = sly_ann.add_label(sly.Label(rectangle, obj_class))
    return sly_ann