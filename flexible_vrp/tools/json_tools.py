import json


def from_json(path: str):
    """
    :param path: path to json file

    :return: a dict
    """
    with open(path, "r") as f:
        data_json = json.load(f)
    return data_json


def to_json(data, path):
    """
    Export data to a json file.

    :param data: the data to export
    :param path: path of the json file
    :return: nothing
    """
    with open(path, "w") as f:
        json.dump(data, f, indent=4, sort_keys=False)
