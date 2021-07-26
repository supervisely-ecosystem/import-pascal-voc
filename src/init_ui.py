def init(data, state):
    data["started"] = False
    data["finished"] = False

    state["mode"] = "public"
    state["samplePercent"] = 10
    state["trainval"] = True
    state["train"] = True
    state["val"] = True
    state["test"] = True
    state["customDataPath"] = None

    state["resultingProjectName"] = "my_project"
