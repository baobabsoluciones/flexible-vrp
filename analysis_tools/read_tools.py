# Tools for reading and writing the solution from Excel
# df.to_records()

#df.to_records() convierte DataFrame en una matriz de registros NumPy.
import json
import pandas as pd
datos = '..\data\datos2.xlsx'

sheet_param = pd.read_excel(datos, sheet_name ="parameters")
sheet_warehouse = pd.read_excel(datos, sheet_name ="warehouse")
sheet_trip_duration = pd.read_excel(datos, sheet_name ="trip_duration")
sheet_inst1 = pd.read_excel(datos, sheet_name ="comp_quantity_inst1")

#to_records: Crea una matriz con el índice, el nombre del parámetro y el valor
df_param = sheet_param.to_records()
df_warehouse = sheet_warehouse.to_records()
df_trip_duration = sheet_trip_duration.to_records()
df_inst1 = sheet_inst1.to_records()

dict_param = sheet_param.set_index('name')['value'].to_dict()
dict_warehouse = sheet_warehouse.to_dict()
dict_trip_duration = sheet_trip_duration.to_dict()
dict_inst1 = sheet_inst1.to_dict()

dict_conjunto={
    'dict_param': dict_param,
    'dict_warehouse': dict_warehouse,
    'dict_trip_duration':dict_trip_duration,
    'dict_inst1':dict_inst1
}
#print(df_param)
#print(df_warehouse)
#print(df_inst1)
#print(df_trip_duration)
#print(dict_param)
#print(" \n")
#print(df_param)
#print(dict_warehouse)
#print(dict_trip_duration)
#print(dict_inst1)
#print(dict_conjunto)

data = {
    "table1":[{"col1":1, "col2":3}, {"col1":2, "col2":3}, {"col1":3, "col2":3}],
    "table2":[{"col1":1, "col2":3}, {"col1":2, "col2":3}, {"col1":3, "col2":3}],
    "parameters":{"p1":1}
 }

