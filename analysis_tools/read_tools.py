# Tools for reading and wrting the solution from Excel
# df.to_records()

#df.to_records() convierte DataFrame en una matriz de registros NumPy.

import pandas as pd
datos = 'https://github.com/baobabsoluciones/flexible-vrp/blob/feature/base_mip/data/datos2.xlsx'

sheet_param = pd.read_excel(datos, sheet_name ="parameters")
sheet_warehouse = pd.read_excel(datos, sheet_name ="warehouse")
sheet_trip_duration = pd.read_excel(datos, sheet_name ="trip_duration")
sheet_inst1 = pd.read_excel(datos, sheet_name ="comp_quantity_inst1")

#df.to_dict()
dict_param = sheet_param.to_dict()
dict_warehouse = sheet_warehouse.to_dict()
dict_trip_duration = sheet_trip_duration.to_dict()
dict_inst1= sheet_inst1.to_dict()

dict1={'dict_param':dict_param,'dict_warehouse': dict_warehouse,'dict_trip_duration':dict_trip_duration,\
    'dict_inst1':dict_inst1}

# Sets
listaVeh = []
Vehicles = listaVeh
for i in range(sheet_param.cell_value(2, 1)):
    listaVeh.append(i + 1)

listaStops = []
Stops = listaStops

listaW = []
Wareahouses = listaW
for i in range(0,sheet_warehouse.nrows):
    listaW.append(sheet_warehouse.cell_value(i, 0)) #como decirle que es str

listaCom = []
Commodities = listaCom
for i in range(0,sheet_inst1.nrows):
    listaCom.append([])
    for j in range(3):
        listaCom[i].append(sheet_inst1.cell_value(i, j)) #str

# Parameters
VehCAP = sheet_param.cell_value(1, 1)# valor = 22 pallets
FleetSize = sheet_param.cell_value(2, 1)# valor= 8 vehicles
LoadTime = sheet_param.cell_value(3, 1) # valor= 1 min
UnloadTime = sheet_param.cell_value(4, 1)# valor = 0.5 min
ReqTimeLimit = sheet_param.cell_value(5, 1)# valor = 8 hours = 480 min
OptTimeLimit = sheet_param.cell_value(6, 1)# valor = 10 hours = 600 min
BigM1 = sheet_param.cell_value(7, 1)# valor = max TripDuration = 35 min
BigM2 = sheet_param.cell_value(8, 1)# valor = OptTimeLimit = 600 min
BigM3 = sheet_param.cell_value(9, 1) # valor = OptTimeLimit-ReqTimeLimit = 120 min

listaTrip = []
TripDuration = listaTrip
for i in range(0,sheet_trip_duration.nrows):
    listaTrip.append([])
    for j in range(3):
        listaTrip[i].append(sheet_trip_duration.cell_value(i, j))  #leer string

data = {
    "table1":[{"col1":1, "col2":3}, {"col1":2, "col2":3}, {"col1":3, "col2":3}],
    "table2":[{"col1":1, "col2":3}, {"col1":2, "col2":3}, {"col1":3, "col2":3}],
    "parameters":{"p1":1}
 }


