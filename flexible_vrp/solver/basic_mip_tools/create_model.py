import pandas as pd
from pyomo.environ import *

# black won't reformat this file.
# fmt: off

# LECTURA DATOS

hoja_param = pd.read_excel("datos1.xlsx", sheet_name ="parameters")
hoja_warehouse = pd.read_excel("datos1.xlsx", sheet_name ="warehouse")
hoja_trip_duration = pd.read_excel("datos1.xlsx", sheet_name ="trip_duration")
hoja_inst1 = pd.read_excel("datos1.xlsx", sheet_name ="comp_quantity_inst1")

def create_model():
    # Create model
    model = AbstractModel()

    # TO-DO: mover esto a lectura de datos
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

    # Sets
    model.sVehicles = Set()
    model.sStops = Set()
    model.sWarehouses = Set()
    model.sCommodities = Set()
    # Derived sets
    model.sTripDuration = Set(dimen=3)

    # TO-DO: esto será la definición del conjunto
    # sTripDurationDomain = [(v, s, s2) for v in sVehicles for s in sStops for s2 in sStops
    #                       if sStops.index_set(s2) = sStops.index_set(s) + 1]



    # Parameters
    model.pVehCAP = Param(mutable=True) # valor = 22 pallets
    model.pFleetSize = Param(mutable=True) # valor= 8 vehicles
    model.pLoadTime = Param(mutable=True) # valor= 1 min
    model.pUnloadTime = Param(mutable=True) # valor = 0.5 min
    model.pReqTimeLimit = Param(mutable=True) # valor = 8 hours = 480 min
    model.pOptTimeLimit = Param(mutable=True) # valor = 10 hours = 600 min
    model.pBigM1 = Param(mutable=True) # valor = max TripDuration = 35 min
    model.pBigM2 = Param(mutable=True) # valor = OptTimeLimit = 600 min
    model.pBigM3 = Param(mutable=True) # valor = OptTimeLimit-ReqTimeLimit = 120 min

    model.pTripDuration = Param(mutable=True)


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
    model.vTripDuration = Var(model.sTripDuration, domain=NonNegativeReals)

    # Constraints
    def fc1(model, v, s, c):
        if model.sStops!=0
            return model.vQuantity[v, s2, c]= model.vQuantity[v, s, c]-model.vUnloadQuantity[v,s,c]+model.vLoadQuantity[v, s, c] \
            s2 for s+1
    def fc2MaxVehCAP(model, v, s)
        return sum(model.vQuantity[v, s, c] for c in model.sCommodities) <= model.pCapacity
    def fc3LodingReqCommodities(model, commodity):
        if model.sCommodities[3]==1
            return sum(model.vLoadQuantity[vehicle, stop, commodity] for vehicle in model.sVehicles \
            for stop in model.sStops) = model.sCommodities[2]
    def fc4UnlodingReqCommodities(model, commodity):
        if model.sCommodities[3] == 1
            return sum(model.vUnloadQuantity[vehicle, stop, commodity] for vehicle in model.sVehicles \
            for stop in model.sStops) = model.sCommodities[2]
    def fc5(model,v,s,c)
        if model.sCommodities[1]==model.sWarehouse
            return model.vUnloadQuantity[v,s,c]<=model.sCommodities[2]*model.vAlpha[v,s,w] \
            for w in model.sWarehouses
    def fc6(model, v, s, c)
        if model.sCommodities[1] == model.sWarehouse
            return model.vLoadQuantity[v, s, c] <= model.sCommodities[2] * model.vAlpha[v, s, w] \
            for w in model.sWarehouses
    def fc7(model, v, s, w, w2)
        if w!=w2
            return model.vTripDuration[v, s, s2] >= model.pTripDuration[w,w2] \
            - model.pBigM1 *(2-model.vAlpha[v,s,w]-model.vAlpha[v,s2,w2])
            for s2 in model.sStops if sStops.index_set(s2) = sStops.index_set(s) + 1



    # Activate constraints
    model.c1 = Constraint(model.sVehicles, model.sStops, model.sCommodities, rule=fc1)
    model.c2MaxVehCAP = Constraint(model.sVehicles, model.sStops, rule=fc2MaxVehCAP)
    model.c3LoadingReq = Constraint(model.sCommodities, rule=fc3LodingReqCommodities)
    model.c4UnloadingReq = Constraint(model.sCommodities, rule=fc4UnlodingReqCommodities)
    model.c5 = Constraint(model.sVehicles, model.sStops,model.sWarehouses, rule=fc5)
    model.c6 = Constraint(model.sVehicles, model.sStops,model.sWarehouses, rule=fc6)
    model.c7 = Constraint(model.sVehicles, model.sStops,model.sWarehouses,model.sWarehouses, rule=fc7)
    model.c8 = Constraint(model.sVehicles, model.sStops, rule=fc8)
    model.c9 = Constraint(model.sVehicles, model.sStops, rule=fc9)
    model.c10 = Constraint(model.sVehicles, model.sStops, rule=fc10)
    model.c11 = Constraint(model.sVehicles, model.sStops, rule=fc11)
    model.c12 = Constraint(model.sVehicles, model.sStops, rule=fc12)
    model.c13 = Constraint(model.sVehicles, model.sStops,model.sVehicles, model.sStops, rule=fc13)
    model.c14 = Constraint(model.sVehicles, model.sStops,model.sVehicles, model.sStops, rule=fc14)
    model.c15 = Constraint(model.sVehicles, model.sStops, rule=fc15)
    model.c16 = Constraint(model.sVehicles, model.sStops,model.sCommodities, rule=fc16)
    model.c17 = Constraint(model.sVehicles, model.sStops, rule=fc17)


    return model

# fmt: on
