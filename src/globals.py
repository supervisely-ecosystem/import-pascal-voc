import os
import sys
from pathlib import Path

import supervisely as sly
from dotenv import load_dotenv
from supervisely.app.v1.app_service import AppService

if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))


my_app = AppService()
api: sly.Api = my_app.public_api

task_id = my_app.task_id
team_id = int(os.environ["context.teamId"])
workspace_id = int(os.environ["context.workspaceId"])

storage_dir = os.path.join(my_app.data_dir, "pascal_importer")
sly.fs.mkdir(storage_dir, remove_content_if_exists=True)

pascal_train_val_dl_link = "http://pjreddie.com/media/files/VOCtrainval_11-May-2012.tar"
pascal_test_dl_link = "http://pjreddie.com/media/files/VOC2012test.tar"
