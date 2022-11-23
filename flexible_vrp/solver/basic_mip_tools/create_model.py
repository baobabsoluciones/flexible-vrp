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
    model.pVehCAP = Param(default=0,mutable=True) # valor = 22 pallets
    model.pFleetSize = Param(default=0,mutable=True) # valor= 8 vehicles
    model.pLoadTime = Param(default=0,mutable=True) # valor= 1 min
    model.pUnloadTime = Param(default=0,mutable=True) # valor = 0.5 min
    model.pReqTimeLimit = Param(default=0,mutable=True) # valor = 8 hours = 480 min
    model.pOptTimeLimit = Param(default=0,mutable=True) # valor = 10 hours = 600 min
    model.pBigM1 = Param(default=0,mutable=True) # valor = max TripDuration = 35 min
    model.pBigM2 = Param(default=0,mutable=True) # valor = OptTimeLimit = 600 min
    model.pBigM3 = Param(default=0,mutable=True) # valor = OptTimeLimit-ReqTimeLimit = 120 min

    model.pTripDuration = Param(, mutable=True) #esto es una lista/tabla


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
    def fc1(model, v, s):
        s2 = s + 1
        return sum(model.vQuantity[v, s2, c] for c in model.sCommodities) = sum(model.vQuantity[v, s, c] for c in model.sCommodities) \
        - sum(model.vUnloadQuantity[v, s, c] for c in model.sCommodities) + sum(model.vLoadQuantity[v, s, c] for  c in model.sCommodities)
    def fc2(model, v, s):
        return sum(model.vQuantity[v, s, c] for c in model.sCommodities) <= model.pCapacity
    def fc3(model, c):
        if model.sCommodities[3]==1:
            return sum(model.vLoadQuantity[v, s, c] for v in model.sVehicles \
            for s in model.sStops) = model.sCommodities[2]
    def fc4(model, c):
        if model.sCommodities[3] == 1:
            return sum(model.vUnloadQuantity[v, s, c] for v in model.sVehicles \
            for s in model.sStops) = model.sCommodities[2]
    def fc5(model,v,s,w):
        if model.sCommodities[1]==model.sWarehouses:
            return sum(model.vUnloadQuantity[v,s,c] for c in model.sCommodities) <= \
            model.sCommodities[2] * model.vAlpha[v,s,w]

    def fc6(model, v, s, w):
        if model.sCommodities[1] == model.sWarehouses:
            return sum(model.vLoadQuantity[v, s, c] for c in model.sCommodities) <= \
            model.sCommodities[2] * model.vAlpha[v, s, w]  #model.sCommodities[2]

    def fc7(model, v, s, w, w2):
        if w!=w2:
            s2 = s + 1
            return model.vTripDuration[v, s, s2] >= model.pTripDuration[w,w2] \
            - model.pBigM1 * (2-model.vAlpha[v,s,w]-model.vAlpha[v,s2,w2])

    def fc8(model, v, s):
        return model.vUnloadDuration[v, s] = sum(model.vUnloadQuantity[v,s,c] for c in model.sCommodities) \
        * model.pUnloadTime

    def fc9(model, v, s):
        return model.vLoadDuration[v, s] = sum(model.vLoadQuantity[v,s,c] for c in model.sCommodities) \
        * model.pLoadTime
    def fc10(model, v, s):
        return model.vDepartureTime[v, s] = model.vArrivalTime[v, s] + model.vLoadDuration[v, s] + model.vUnloadDuration[v, s]
    def fc11(model, v, s):
        s2=s+1
        return model.vArrivalTime[v, s2] = model.vDepartureTime[v, s] + model.vTripDuration[v, s, s2]
    def fc12(model, v, s):
        return model.vUnloadTime[v, s] = model.vArrivalTime[v, s] + model.vUnloadDuration[v, s]
    def fc13(model,v,s,v2,s2):
        if v!=v2:
            return model.vBeta1[v,s,v2,s2] + model.vBeta2[v2,s2,v,s] >= model.vAlpha[v,s,w] + model.vAlpha[v2,s2,w] -1
    def fc14(model,v,s,v2,s2):
        if v!= v2:
            return model.vArrivalTime[v, s]>= model.vDepartureTime[v,s]- (1-model.vBeta1[v,s,v2,s2]) * model.pBigM2
    def fc15(model,v,s):
        return model.vUnloadTime[v,s] <= model.pReqTimeLimit + model.vGamma[v,s] * model.pBigM3
    def fc16(model,v,s,c):
        if model.sCommodities[3]==1:
            return model.vLoadQuantity[v,s,c] <= (1-model.vGamma[v,s]) * model.pVehCAP
    def fc17(model,v,s):
        return model.vUnloadTime[v,s] <= model.pOptTimeLimit


    # Activate constraints
    model.c1 = Constraint(model.sVehicles, model.sStops, rule=fc1)
    model.c2 = Constraint(model.sVehicles, model.sStops, rule=fc2)
    model.c3 = Constraint(model.sCommodities, rule=fc3)
    model.c4 = Constraint(model.sCommodities, rule=fc4)
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
