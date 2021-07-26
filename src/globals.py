import os
import supervisely_lib as sly

my_app = sly.AppService(ignore_task_id=True)
api: sly.Api = my_app.public_api

task_id = my_app.task_id
team_id = int(os.environ['context.teamId'])
workspace_id = int(os.environ['context.workspaceId'])

sly.fs.mkdir(os.path.join(my_app.data_dir, "pascal_importer"), remove_content_if_exists=True)
storage_dir = os.path.join(my_app.data_dir, "pascal_importer")

pascal_train_val_dl_link = "http://pjreddie.com/media/files/VOCtrainval_11-May-2012.tar"
pascal_test_dl_link = "http://pjreddie.com/media/files/VOC2012test.tar"
