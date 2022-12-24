import json
import pyomo.environ as pyo


def from_json(path: str):
    """
    :param path: path to json file

    :return: a dict
    """
    with open(path, "r") as f:
        data_json = json.load(f)
    return data_json


def safe_value(x):
    """
    Safely apply pyomo value to a variable.
    pyomo value generate an error if the variable has not been used.
    This function will return 0 instead.
    :param x: a pyomo variable
    :return:
    """
    try:
        if x is not None:
            return pyo.value(x)
        else:
            return 0
    except:
        return 0


def to_json(data, path):
    """
    Export data to a json file.

    :param data: the data to export
    :param path: path of the json file
    :return: nothing
    """
    with open(path, "w") as f:
        json.dump(data, f, indent=4, sort_keys=False)
