def init(data, state):
    data["started"] = False
    data["finished"] = False
    state["mode"] = "custom"  # "public" "custom"
    state["samplePercent"] = 100

    state["trainval"] = True
    state["train"] = True
    state["val"] = True
    state["test"] = True
    state["customDataPath"] = "/ApplicationsData/Export-to-Pascal-VOC/7092/3692_Lemons(Bitmap)_pascal_voc.tar.gz"  # "/pascal/dataset/"
    state["resultingProjectName"] = "my_project"  # "/pascal/dataset/"
