# Tools for reading and writing the solution from Excel

import json
import pandas as pd


def read_input_data(file_path):

    df_parameters = pd.read_excel(file_path, sheet_name="parameters")
    df_trip_durations = pd.read_excel(file_path, sheet_name="trip_duration")
    df_commodities = pd.read_excel(file_path, sheet_name="comp_quantity_inst1")

    df_parameters.columns = ["param_name", "param_value"]
    parameters = df_parameters.to_dict("records")
    json_trip_durations = df_trip_durations.to_dict("records")
    json_commodities = df_commodities.to_dict("records")

    json_parameters = {c["param_name"]: c["param_value"] for c in parameters}

    dct_input_data = {
        "parameters": json_parameters,
        "trip_durations": json_trip_durations,
        "commodities": json_commodities,
    }
    print(dct_input_data)

    return dct_input_data

