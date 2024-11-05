import asyncio
import os
import random
import shutil
from os.path import basename, isdir, isfile, join, normpath

import requests
import supervisely as sly
from supervisely.io.fs import (
    download,
    file_exists,
    get_file_name,
    get_subdirs,
    remove_dir,
    silent_remove,
    unpack_archive,
)

import globals as g
import init_ui
import init_ui_progress
import pascal_importer


def download_from_link(link: str, save_path: str, file_name: str, app_logger, use_cache):
    sly.logger.info(f"Downloading from link: {link} to {save_path}")
    response = requests.head(link, allow_redirects=True)
    sizeb = int(response.headers.get("content-length", 0))
    progress_cb = init_ui_progress.get_progress_cb(
        g.api, g.task_id, f"Download {file_name}", sizeb, is_size=True
    )
    cache = g.my_app.cache if use_cache else None
    if not file_exists(save_path):
        sly.logger.info(f"File {file_name} does not exist. Will download it again.")
        headers = {"User-Agent": random.choice(g.user_agents)}
        download(link, save_path, cache=cache, progress=progress_cb, headers=headers)
        init_ui_progress.reset_progress(g.api, g.task_id)
        app_logger.info(f"{file_name} has been successfully downloaded")
    sly.logger.info(f"Checking if {file_name} is archive...")
    if not sly.fs.is_archive(save_path):
        sly.logger.warning(f"File {file_name} is not an archive and will be skipped")
    else:
        sly.logger.info(f"Trying to unpack {file_name} archive to {g.storage_dir}...")
        try:
            unpack_archive(save_path, g.storage_dir, remove_junk=True)
            sly.logger.info(f"Archive {file_name} has been successfully unpacked")
        except Exception as e:
            sly.logger.error(f"There was an error while unpacking {file_name} archive: {e}.")


def pascal_downloader(link: str, save_path: str, file_name: str, app_logger):
    try:
        download_from_link(link, save_path, file_name, app_logger, use_cache=True)
    except shutil.ReadError as e:
        app_logger.warn(f"Could not unpack {file_name} archive. {repr(e)}")
        silent_remove(save_path)

    if not file_exists(save_path):
        app_logger.info("Will try to download archive without cache")
        download_from_link(link, save_path, file_name, app_logger, use_cache=False)


def download_original(state: dict, app_logger):
    if state["trainval"] or state["train"] or state["val"]:
        trainval_archive = os.path.join(g.storage_dir, "VOCtrainval_11-May-2012.tar")
        pascal_downloader(
            g.pascal_train_val_dl_link,
            trainval_archive,
            "VOCtrainval_11-May-2012.tar",
            app_logger,
        )
    if state["test"]:
        test_archive = os.path.join(g.storage_dir, "VOC2012test.tar")
        pascal_downloader(g.pascal_test_dl_link, test_archive, "VOC2012test.tar", app_logger)


def download_custom(api: sly.Api, state: dict, app_logger):
    remote_path: str = state["customDataPath"]
    remote_path = f'{remote_path.strip().lstrip("/").rstrip("/")}'  # normalize team files path

    file_path = basename(normpath(remote_path))
    local_path = join(g.storage_dir, file_path)

    file_info = api.file.get_info_by_path(g.team_id, remote_path)
    if file_info is None:
        is_dir = api.file.dir_exists(g.team_id, remote_path)
        if is_dir:
            api.file.download_directory_async(
                g.team_id, remote_path, local_path, semaphore=asyncio.Semaphore(200)
            )
        else:
            raise FileNotFoundError(f"File or directory {remote_path} not found.")
    else:
        file_size = file_info.sizeb
        progress_download_cb = init_ui_progress.get_progress_cb(
            api,
            g.task_id,
            f'Download "{file_path}"',
            total=file_size,
            is_size=True,
        )

        api.file.download(g.team_id, remote_path, local_path, progress_cb=progress_download_cb)
        try:
            unpack_archive(
                local_path, join(g.storage_dir, get_file_name(file_path)), remove_junk=True
            )
        except:
            raise ValueError(f"File {local_path} is not archive")

        silent_remove(local_path)

    local_path = join(g.storage_dir, get_file_name(file_path))
    voc_dir = join(local_path, "VOCdevkit")
    if isdir(voc_dir):
        project_dir = join(g.storage_dir, "VOCdevkit")
        shutil.move(voc_dir, project_dir)
        remove_dir(local_path)
    else:
        raise ValueError(f"Could not find VOCdevkit directory in '{remote_path}'")

    app_logger.info(f'"{basename(normpath(remote_path))}" has been successfully downloaded')
    return project_dir, remote_path


def check_function(path):
    subdirs = get_subdirs(path)
    if "VOC" in subdirs:
        shutil.move(join(path, "VOC"), join(path, "VOC2012"))
        ds_path = join(path, "VOC2012")
    elif "VOC2012" in subdirs:
        ds_path = join(path, "VOC2012")
    else:
        return False

    annotations_dir = isdir(join(ds_path, "Annotations"))
    images_sets_dir = isdir(join(ds_path, "ImageSets"))
    images_dir = isdir(join(ds_path, "JPEGImages"))
    colors_file = isfile(join(ds_path, "colors.txt"))
    return images_dir and annotations_dir and images_sets_dir and colors_file


def download_data(api: sly.Api, state: dict, app_logger):
    if state["mode"] == "public":
        download_original(state, app_logger)
    else:
        project_dir, remote_dir = download_custom(api, state, app_logger)
        is_valid = check_function(project_dir)
        if not is_valid:
            raise ValueError(
                (
                    f"Directory '{remote_dir}' is not valid Pascal VOC dataset. "
                    "Please, check app documentation for more information about project structure."
                )
            )
