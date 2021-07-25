<div align="center" markdown>
<img src="https://i.imgur.com/HgSP0bG.png"/>

# Export to Pascal VOC

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#Preparation">Preparation</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
</p>
  
[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/import-pascal-voc)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/import-pascal-voc)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-pascal-voc&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-pascal-voc&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-pascal-voc&counter=runs&label=runs&123)](https://supervise.ly)

</div>

## Overview
Converts [Pascal VOC](http://host.robots.ox.ac.uk/pascal/VOC/) format project to [Supervisely](https://docs.supervise.ly/data-organization/00_ann_format_navi) and creates a new project in selected `Team` -> `Workspace`. Backward compatible with [`export-to-pascal`](https://github.com/supervisely-ecosystem/export-to-pascal-voc) app.


#### Custom Pascal VOC Project archive must have the following structure:
```
.
└── custom_pascal_project.tar
    └── VOCdevkit
        └── VOC or VOC2012
            ├── Annotations
            ├── ImageSets
            |   ├── Action
            |	  ├── Layout
            |	  ├── Main
            |	  └── Segmentation
            ├── JPEGImages
            ├── SegmentationClass
            ├── SegmentationObject
            └── colors.txt (not original Pascal VOC format file)
```

**`colors.txt`** file is custom, and not provided in the original Pascal VOC Dataset. File contains information about instance mask colors associated with classes in Pascal VOC Project. This file is required by Supervisely Pascal VOC import plugin, if you are uploading custom dataset in Pascal VOC format.

**`colors.txt`** example:
```txt
neutral 224 224 192
kiwi 255 0 0
lemon 81 198 170
```
Colors are indicated in **`RGB`** format.

#### Pascal VOC format has the following ImageSets:

**Classification/Detection Image Sets**

The `VOC2012/ImageSets/Main/` directory contains text files specifying lists of images for the main classification/detection tasks.
The files train.txt, val.txt, trainval.txt and test.txt list the image identifiers for the corresponding image sets (training, validation, training+validation, test). Each line of the file contains a single image identifier.

* train: Training data.
* val: Validation data.
* trainval: The union of train and val.
* test: Test data.

The file `VOC/ImageSets/Main/<class>_<imgset>.txt` contains image identifiers and ground truth for a particular class and image set.
For example the file car_train.txt applies to the ‘car’ class and train image set.
Each line of the file contains a single image identifier and ground truth label, separated by a space, for example:

```txt
2009_000040 -1
2009_000042 -1
2009_000052 1
```
  
**Segmentation Image Sets**

The `VOC2012/ImageSets/Segmentation/` directory contains text files specifying lists of images for the segmentation task.
The files train.txt, val.txt and trainval.txt list the image identifiers for the corresponding image sets (training, validation, training+validation). Each line of the file contains a single image identifier.

**Action and Layout Classification Image Sets are not supported by import application.**

## How To Run 
**Step 1**: Add app to your team from [Ecosystem](https://ecosystem.supervise.ly/apps/import-pascal-voc) if it is not there.

**Step 2**: Run app from `Team` `Plugins & Apps` page.

## How to use

App can import original and custom Pascal VOC dataset.

**1. To import original dataset** - select `Public Data` in the gui and check datasets that you want to import. App will download and import pascal data.

<img src="https://i.imgur.com/Khn18Cc.png"/>

**2. To import custom dataset** - select `Custom Data`, upload custom dataset to `Team` -> `Files` copy path to your dataset and paste it to the text input in the app gui.

<img src="https://i.imgur.com/OmcJfik.png"/>


**Resulting project will be saved to selected `Team` -> `Workspace`**

<img src="https://i.imgur.com/l16W14R.png"/>
