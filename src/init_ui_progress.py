import supervisely_lib as sly
from functools import partial


def init_progress(data, state):
    data["progressName"] = None
    data["currentProgressLabel"] = 0
    data["totalProgressLabel"] = 0
    data["currentProgress"] = 0
    data["totalProgress"] = 0


def reset_progress(api, task_id):
    _set_progress(api, task_id, None, 0, 0, 0, 0)


def _set_progress(api, task_id, message, current, total):
    fields = [
        {"field": f"data.progressName", "payload": message},
        {"field": f"data.currentProgress", "payload": current},
        {"field": f"data.totalProgress", "payload": total},
    ]
    api.task.set_fields(task_id, fields)


def _update_progress_ui(api, task_id, progress: sly.Progress):
    _set_progress(api, task_id, progress.message, progress.current, progress.total)


def update_progress(count, api: sly.Api, task_id, progress: sly.Progress):
    count = min(count, progress.total - progress.current)
    progress.iters_done(count)
    if progress.need_report():
        progress.report_progress()
        _update_progress_ui(api, task_id, progress)


def set_progress(current, api: sly.Api, task_id, progress: sly.Progress):
    old_value = progress.current
    delta = current - old_value
    update_progress(delta, api, task_id, progress)


def get_progress_cb(api, task_id, message, total, is_size=False, func=update_progress):
    progress = sly.Progress(message, total, is_size=is_size)
    progress_cb = partial(func, api=api, task_id=task_id, progress=progress)
    progress_cb(0)
    return progress_cb