import os

import globals as g
import init_ui
import init_ui_progress
import pascal_importer
import src.utils as utils
import supervisely as sly


@g.my_app.callback("import_pascal_voc")
@sly.timeit
def import_pascal_voc(api: sly.Api, task_id, context, state, app_logger):
    utils.download_data(api, state, app_logger)
    pascal_importer.start(state)
    proj_dir = os.path.join(g.storage_dir, "SLY_PASCAL")

    files = []
    for r, d, f in os.walk(proj_dir):
        for file in f:
            files.append(os.path.join(r, file))
    total_files = len(files) - 1  # meta.json

    progress_project_cb = init_ui_progress.get_progress_cb(
        api, task_id, f'Uploading project"', total_files
    )
    res_project_id, res_project_name = sly.upload_project(
        dir=proj_dir,
        api=api,
        workspace_id=state["workspaceId"],
        project_name=state["resultingProjectName"],
        log_progress=False,
        progress_cb=progress_project_cb,
    )
    res_project = api.project.get_info_by_id(res_project_id)

    fields = [
        {"field": "data.started", "payload": False},
        {"field": "data.finished", "payload": True},
        {"field": "data.resultProject", "payload": res_project_name},
        {"field": "data.resultProjectId", "payload": res_project_id},
        {
            "field": "data.resultProjectPreviewUrl",
            "payload": api.image.preview_url(res_project.reference_image_url, 100, 100),
        },
    ]
    api.task.set_fields(task_id, fields)

    api.task.set_output_project(g.my_app.task_id, res_project_id, res_project_name)
    g.my_app.show_modal_window(
        f"'{state['resultingProjectName']}' project has been successfully imported."
    )
    g.my_app.stop()


def main():
    sly.logger.info(
        "Script arguments",
        extra={
            "team_id": g.team_id,
            "workspace_id": g.workspace_id,
            "task_id": g.task_id,
        },
    )

    data = {}
    state = {}

    init_ui.init(data, state)
    init_ui_progress.init_progress(data, state)
    g.my_app.run(data=data, state=state)


if __name__ == "__main__":
    sly.main_wrapper("main", main, log_for_agent=False)
