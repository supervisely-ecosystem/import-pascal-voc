import os
import shutil
import init_ui
import requests
import globals as g
import pascal_importer
import init_ui_progress
import supervisely_lib as sly
from supervisely_lib.io.fs import download, file_exists


def pascal_downloader(link, save_path, file_name, app_logger):
    response = requests.head(link, allow_redirects=True)
    sizeb = int(response.headers.get('content-length', 0))
    progress_cb = init_ui_progress.get_progress_cb(g.api, g.task_id, f"Download {file_name}", sizeb, is_size=True)
    if not file_exists(save_path):
        download(link, save_path, cache=g.my_app.cache, progress=progress_cb)
        init_ui_progress.reset_progress(g.api, g.task_id)
        app_logger.info(f'{file_name} has been successfully downloaded')
    shutil.unpack_archive(save_path, g.storage_dir, format="tar")


@g.my_app.callback("import_pascal_voc")
@sly.timeit
def import_pascal_voc(api: sly.Api, task_id, context, state, app_logger):
    if state["mode"] == "public":
        if state["trainval"] or state["train"] or state["val"]:
            trainval_archive = os.path.join(g.storage_dir, "VOCtrainval_11-May-2012.tar")
            pascal_downloader(g.pascal_train_val_dl_link, trainval_archive, "VOCtrainval_11-May-2012.tar", app_logger)
        if state["test"]:
            test_archive = os.path.join(g.storage_dir, "VOC2012test.tar")
            pascal_downloader(g.pascal_test_dl_link, test_archive, "VOC2012test.tar", app_logger)
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

    pascal_importer.start(state)
    proj_dir = os.path.join(g.storage_dir, "SLY_PASCAL")

    files = []
    for r, d, f in os.walk(proj_dir):
        for file in f:
            files.append(os.path.join(r, file))
    total_files = len(files)-1  # meta.json

    progress_project_cb = init_ui_progress.get_progress_cb(api, task_id, f'Uploading project"', total_files)
    res_project_id, res_project_name = sly.upload_project(dir=proj_dir,
                                                          api=api,
                                                          workspace_id=g.workspace_id,
                                                          project_name=state["resultingProjectName"],
                                                          log_progress=False,
                                                          progress_cb=progress_project_cb)
    res_project = api.project.get_info_by_id(res_project_id)

    fields = [
        {"field": "data.started", "payload": False},
        {"field": "data.finished", "payload": True},
        {"field": "data.resultProject", "payload": res_project_name},
        {"field": "data.resultProjectId", "payload": res_project_id},
        {"field": "data.resultProjectPreviewUrl", "payload": api.image.preview_url(res_project.reference_image_url, 100, 100)}
    ]
    api.task.set_fields(task_id, fields)

    api.task.set_output_project(g.my_app.task_id, res_project_id, res_project_name)
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
