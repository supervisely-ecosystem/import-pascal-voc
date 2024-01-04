import os

from dotenv import load_dotenv

import supervisely as sly

if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))


my_app = sly.AppService()
api: sly.Api = my_app.public_api

task_id = sly.env.task_id()
team_id = sly.env.team_id()
workspace_id = sly.env.workspace_id()

storage_dir = os.path.join(my_app.data_dir, "pascal_importer")
sly.fs.mkdir(storage_dir, remove_content_if_exists=True)

# pascal_train_val_dl_link = "http://pjreddie.com/media/files/VOCtrainval_11-May-2012.tar"
pascal_train_val_dl_link = (
    "http://host.robots.ox.ac.uk/pascal/VOC/voc2012/VOCtrainval_11-May-2012.tar"
)
# pascal_test_dl_link = "http://pjreddie.com/media/files/VOC2012test.tar"
pascal_test_dl_link = "http://host.robots.ox.ac.uk:8080/eval/downloads/VOC2012test.tar"
