import os
import sys
from pathlib import Path

import supervisely as sly
from dotenv import load_dotenv
from supervisely.app.v1.app_service import AppService

root_source_dir = str(Path(sys.argv[0]).parents[1])
print(f"App source directory: {root_source_dir}")
sys.path.append(root_source_dir)

# only for convenient debug
debug_env_path = os.path.join(root_source_dir, "debug.env")
secret_debug_env_path = os.path.join(root_source_dir, "secret_debug.env")
load_dotenv(debug_env_path)
load_dotenv(secret_debug_env_path, override=True)


my_app = AppService()
api: sly.Api = my_app.public_api

task_id = my_app.task_id
team_id = int(os.environ["context.teamId"])
workspace_id = int(os.environ["context.workspaceId"])

storage_dir = os.path.join(my_app.data_dir, "pascal_importer")
sly.fs.mkdir(storage_dir, remove_content_if_exists=True)

pascal_train_val_dl_link = "http://pjreddie.com/media/files/VOCtrainval_11-May-2012.tar"
pascal_test_dl_link = "http://pjreddie.com/media/files/VOC2012test.tar"
