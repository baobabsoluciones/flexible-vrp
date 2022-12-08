# Tools for reading and writing the solution from Excel
# df.to_records()

#df.to_records() convierte DataFrame en una matriz de registros NumPy.
import json
import pandas as pd

def read_input_data(file_path):

    df_parameters = pd.read_excel(file_path, sheet_name ="parameters")
    df_warehouses = pd.read_excel(file_path, sheet_name ="warehouse")
    df_trip_durations = pd.read_excel(file_path, sheet_name ="trip_duration")
    df_commodities = pd.read_excel(file_path, sheet_name ="comp_quantity_inst1")

    #to_records: Crea una matriz con el índice, el nombre del parámetro y el valor
    df_parameters.columns = ['param_name', 'param_value']
    parameters = df_parameters.to_dict('records')
    warehouses = df_warehouses.to_dict('records')
    json_trip_durations = df_trip_durations.to_dict('records')
    json_commodities = df_commodities.to_dict('records')


    json_parameters = {c['param_name']: c['param_value'] for c in parameters}

    dct_input_data={
        'parameters': json_parameters,
        # 'warehouses': warehouses,
        'trip_durations': json_trip_durations,
        'commodities': json_commodities
    }
    print(dct_input_data)
    #print(df_warehouse)
    #print(commodities)
    #print(trip_durations)
    #print(dict_param)
    #print(" \n")
    #print(param)
    #print(dict_warehouse)
    #print(dict_trip_duration)
    #print(dict_inst1)
    #print(dict_conjunto)

    # data = {
    #     "table1":[{"col1":1, "col2":3}, {"col1":2, "col2":3}, {"col1":3, "col2":3}],
    #     "table2":[{"col1":1, "col2":3}, {"col1":2, "col2":3}, {"col1":3, "col2":3}],
    #     "parameters":{"p1":1}
    #  }
    #
    return dct_input_data

# if __name__ == "__main__":
#     file_path = '..\data\datos2.xlsx'
#     input_data = read_input_data(file_path)
#     print(input_data)