import pandas as pd
import xlrd
from pyomo.environ import *

# black won't reformat this file.
# fmt: off

# LECTURA DATOS

# ¿Cómo defino la localicion al repositorio de GitHub?
# De manera temporal y a modo de prueba he definido la localización en mi escritorio
location = (r"C:\Users\maria\OneDrive - Universidad Politécnica de Madrid\datos1.xls")
valor = xlrd.open_workbook(location)

hoja_param = pd.read_excel("datos1.xlsx", sheet_name ="parameters")
hoja_warehouse = pd.read_excel("datos1.xlsx", sheet_name ="warehouse")
hoja_trip_duration = pd.read_excel("datos1.xlsx", sheet_name ="trip_duration")
hoja_inst1 = pd.read_excel("datos1.xlsx", sheet_name ="comp_quantity_inst1")

def create_model():
    # Create model
    model = AbstractModel()

    # TODO: mover esto a lectura de datos
    # # Sets
    # listaVeh=[]
    # model.sVehicles = Set(listaVeh)
    # for i in range(hoja_param.cell_value(2, 1)):
    #     listaVeh.append(i+1)
    #
    # listaStops=[]
    # model.sStops = Set(listaStops)
    #
    # listaW = []
    # model.sWarehouses = Set(listaW)
    # for i in range(): #hasta que el excel detecte la casilla vacía
    #     listaW.append(hoja_warehouse.cell_value(i,0)) #como decirle que es str
    #
    # listaCom = []
    # model.sCommodities = Set(listaCom)
    # for i in range(): #hasta que el excel detecte la casilla vacía
    #     listaCom.append([])
    #     for j in range(3):
    #         listaCom[i].append(hoja_inst1.cell_value(i,j)) #str


    # Derived sets
    model.sTripDurationDomain = Set(dimen=3)

    # TO-DO: esto será la definición del conjunto
    # sTripDurationDomain = [(v, s, s2) for v in sVehicles for s in sStops for s2 in sStops
    #                       if sStops.index_set(s2) = sStops.index_set(s) + 1]



    # Parameters
    model.pVehCAP = Param(hoja_param.cell_value(1, 1), mutable=True) # valor = 22 pallets
    model.pFleetSize = Param(hoja_param.cell_value(2, 1), mutable=True) # valor= 8 vehicles
    model.pLoadTime = Param(hoja_param.cell_value(3, 1), mutable=True) # valor= 1 min
    model.pUnloadTime = Param(hoja_param.cell_value(4, 1), mutable=True) # valor = 0.5 min
    model.pReqTimeLimit = Param(hoja_param.cell_value(5, 1), mutable=True) # valor = 8 hours = 480 min
    model.pOptTimeLimit = Param(hoja_param.cell_value(6, 1), mutable=True) # valor = 10 hours = 600 min
    model.pBigM1 = Param(hoja_param.cell_value(7, 1), mutable=True) # valor = max TripDuration = 35 min
    model.pBigM2 = Param(hoja_param.cell_value(8, 1), mutable=True) # valor = OptTimeLimit = 600 min
    model.pBigM3 = Param(hoja_param.cell_value(9, 1), mutable=True) # valor = OptTimeLimit-ReqTimeLimit = 120 min

    listaTrip = []
    model.pTripDuration = Param(listaTrip)
    for i in range(): #hasta que el excel detecte la casilla vacía
        listaTrip.append([])
        for j in range(3):
            listaTrip[i].append(hoja_trip_duration.cell_value(i,j))  #leer string


    # Binary Variables
    model.vAlpha = Var(model.sVehicles, model.sStops, model.sWarehouses, domain=Binary)
    model.vBeta1 = Var(model.sVehicles, model.sStops, model.sVehicles, model.sStops, domain=Binary)
    model.vBeta2 = Var(model.sVehicles, model.sStops, model.sVehicles, model.sStops, domain=Binary)
    model.vGamma = Var(model.sVehicles, model.sStops, domain=Binary)


    # Continuous Variables
    model.vArrivalTime = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
    model.vDepartureTime = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
    model.vUnloadTime = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
    model.vLoadDuration = Var(model.sVehicles, model.sStos, domain=NonNegativeReals)
    model.vUnloadDuration = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
    model.vQuantity = Var(model.sVehicles, model.sStops, model.sCommodities, domain=NonNegativeReals)
    model.vLoadQuantity = Var(model.sVehicles, model.sStops, model.sCommodities, domain=NonNegativeReals)
    model.vUnloadQuantity = Var(model.sVehicles, model.sStops, model.sCommodities, domain=NonNegativeReals)
    model.vTripDuration = Var(model.sTripDurationDomain, domain=NonNegativeReals)

    # Constraints
    def fcMaxVehCAP(model, v, s):
        return sum(model.vQuantity[v, s, c] for c in model.sCommodities) <= model.pCapacity

    #def fcLodingCompulsoryCommodities(model, commodity):
    #    sum(model.vLoadQuantity(truck, stop, commodity) for truck in model.sTrucks for stop in model.sStops) = commodity[2]

    # Activate constraints
    # activar la restriccion2 model.Constraint(model.sCommoditiesCompusory, rule= fcLodingCompulsoryCommodities)

    model.cMaxVehCAP = Constraint(model.sVehicles, model.sStops, rule=fcMaxVehCAP)

    return model

# fmt: on
