import os
import shutil
import init_ui
import requests
import globals as g
import pascal_importer
import init_ui_progress
import supervisely_lib as sly
from supervisely_lib.io.fs import download, file_exists


@g.my_app.callback("import_pascal_voc")
@sly.timeit
def import_pascal_voc(api: sly.Api, task_id, context, state, app_logger):
    if state["mode"] == "public":
        if state["trainval"] or state["train"] or state["val"]:
            trainval_archive = os.path.join(g.storage_dir, "VOCtrainval_11-May-2012.tar")
            if not file_exists(trainval_archive):
                response = requests.head(g.pascal_train_val_dl_link, allow_redirects=True)
                sizeb = int(response.headers.get('content-length', 0))
                progress_cb = init_ui_progress.get_progress_cb(g.api, g.task_id, "Download 'VOCtrainval_11-May-2012.tar'", sizeb, is_size=True)
                download(g.pascal_train_val_dl_link, trainval_archive, progress=progress_cb)
                init_ui_progress.reset_progress(g.api, g.task_id)
                app_logger.info('"VOCtrainval_11-May-2012.tar" has been successfully downloaded')
            shutil.unpack_archive(trainval_archive, g.storage_dir, format="tar")
        if state["test"]:
            test_archive = os.path.join(g.storage_dir, "VOC2012test.tar")
            if not file_exists(test_archive):
                response = requests.head(g.pascal_test_dl_link, allow_redirects=True)
                sizeb = int(response.headers.get('content-length', 0))
                progress_cb = init_ui_progress.get_progress_cb(g.api, g.task_id, "Download 'VOC2012test.tar'", sizeb, is_size=True)
                download(g.pascal_test_dl_link, test_archive, progress=progress_cb)
                init_ui_progress.reset_progress(g.api, g.task_id)
                app_logger.info('"VOC2012test.tar" has been successfully downloaded')
            shutil.unpack_archive(test_archive, g.storage_dir, format="tar")
    else:
        remote_dir = state["customDataPath"]
        local_archive = os.path.join(g.storage_dir, os.path.basename(os.path.normpath(remote_dir)))

        file_size = api.file.get_info_by_path(g.team_id, remote_dir).sizeb
        if not file_exists(os.path.join(g.storage_dir, os.path.basename(os.path.normpath(remote_dir)))):
            progress_upload_cb = init_ui_progress.get_progress_cb(g.api,
                                                                  g.task_id,
                                                                  f'Download "{os.path.basename(os.path.normpath(remote_dir))}"',
                                                                  total=file_size,
                                                                  is_size=True)
            api.file.download(g.team_id, remote_dir, local_archive, progress_cb=progress_upload_cb)

            app_logger.info(f'"{os.path.basename(os.path.normpath(remote_dir))}" has been successfully downloaded')
        shutil.unpack_archive(local_archive, g.storage_dir)
        if "VOC2012" not in os.listdir(os.path.join(g.storage_dir, "VOCdevkit")):
            os.rename(os.path.join(g.storage_dir, "VOCdevkit", "VOC"),
                      os.path.join(g.storage_dir, "VOCdevkit", "VOC2012"))

    pascal_importer.main(state)
    proj_dir = os.path.join(g.storage_dir, "SLY_PASCAL")

    files = []
    for r, d, f in os.walk(proj_dir):
        for file in f:
            files.append(os.path.join(r, file))
    total_files = len(files)-1  # meta.json

    progress_project_cb = init_ui_progress.get_progress_cb(api, task_id, f'Uploading project"', total_files)
    sly.upload_project(dir=proj_dir, api=api, workspace_id=state["workspaceId"], project_name=state["resultingProjectName"],
                       log_progress=False, progress_cb=progress_project_cb)

    fields = [
        {"field": "data.started", "payload": False},
        {"field": "data.finished", "payload": True},
    ]
    api.task.set_fields(task_id, fields)

    g.my_app.show_modal_window(f"'{state['resultingProjectName']}' project has been successfully imported.")
    g.my_app.stop()


def main():
    sly.logger.info(
        "Script arguments",
        extra={
            "team_id": g.team_id,
            "workspace_id": g.workspace_id,
            "task_id": g.task_id
        }
    )

    data = {}
    state = {}

    init_ui.init(data, state)
    init_ui_progress.init_progress(data,state)
    g.my_app.run(data=data, state=state)


if __name__ == "__main__":
    sly.main_wrapper("main", main)
