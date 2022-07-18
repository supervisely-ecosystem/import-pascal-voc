<div align="center" markdown>
<img src="https://i.imgur.com/ykox2iS.png"/>

# Import Pascal VOC

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#Preparation">Preparation</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
</p>
  
[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/import-pascal-voc)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/import-pascal-voc)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/import-pascal-voc)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/import-pascal-voc)](https://supervise.ly)

</div>

## Overview
Converts [Pascal VOC](http://host.robots.ox.ac.uk/pascal/VOC/) format to [Supervisely](https://docs.supervise.ly/data-organization/00_ann_format_navi) and creates a new project in selected `Team` -> `Workspace`. Backward compatible with [`export-to-pascal`](https://github.com/supervisely-ecosystem/export-to-pascal-voc) app.


#### Custom Pascal VOC archive must have the following structure:
```
.
└── custom_pascal.tar
    └── VOCdevkit
        └── VOC or VOC2012
            ├── Annotations
            ├── ImageSets
            |   ├── Main   
            |   └── Segmentation
            ├── JPEGImages
            ├── SegmentationClass
            ├── SegmentationObject
            └── colors.txt
```

**`colors.txt`** file is custom, and not provided in the original Pascal VOC Dataset. File contains information about instance mask colors associated with classes in Pascal VOC format. This file is required by this app, if you are uploading custom dataset. Each line of `colors.txt` file starts with `class_name` and ends with `RGB` values that represent class color.

**`colors.txt`** example:
```txt
neutral 224 224 192
kiwi 255 0 0
lemon 81 198 170
```

**Action and Layout Classification Image Sets are not supported by import application.**

## How To Run 
**Step 1**: Add app to your team from [Ecosystem](https://ecosystem.supervise.ly/apps/import-pascal-voc) if it is not there.

**Step 2**: Run app from `Team` -> `Plugins & Apps` page.

After running the app you will be redirected to the `Tasks` page.

<img src="https://i.imgur.com/tmmVKlI.png"/>


**Step 3**: Waiting until the app is started.

Once app is started, new task will appear in workspace tasks. Wait for message `Application is started ...` (1) and then press `Open` button (2).

<img src="https://i.imgur.com/dXcwVzn.png"/>

## How to use

**App can import public and custom Pascal VOC dataset.**

**1. To import original dataset** - select `Public Data` in the gui and check datasets that you want to import. App will download and import pascal data.

1. Select `Public Data`
2. Select which Pascal VOC datasets you want to import
3. Select which percent of Pascal VOC data you want to import
4. Select destination `Team`, `Workspace` and `Project name`
5. Press `Run`

<img src="https://i.imgur.com/bBStzR2.png"/>

**2. To import custom dataset** - select `Custom Data`, upload custom dataset to `Team` -> `Files` copy path to your dataset and paste it to the text input in the app gui.

1. Select `Custom Data`
2. Input path to your data from `Team` -> `Files`

<img src="https://i.imgur.com/YemDSqY.gif" width="700"/>

3. Select destination `Team`, `Workspace` and `Project name`
4. Press `Run`

<img src="https://i.imgur.com/ZII5d70.png"/>

You can access result project by clicking on it's name under the `Run` button. Resulting project will be saved to selected `Team` -> `Workspace`.

<img src="https://i.imgur.com/WwmeoLV.png"/>
