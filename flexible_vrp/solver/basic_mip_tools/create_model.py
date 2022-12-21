import pandas as pd
from pyomo.environ import *

# black won't reformat this file.
# fmt: off

def create_model():
    # Create model
    model = AbstractModel()

    # Sets
    model.sVehicles = Set()
    model.sStops = Set()
    model.sStopsButLast = Set()
    model.sWarehouses = Set()
    model.sCommodities = Set()
    # Derived sets
    model.sTripDuration = Set(dimen=3)
    model.c7_constraint_domain = Set(dimen=5)

    # TO-DO: esto será la definición del conjunto
    # sTripDurationDomain = [(v, s, s2) for v in sVehicles for s in sStops for s2 in sStops
    #                       if sStops.index_set(s2) = sStops.index_set(s) + 1]



    # Parameters
    model.pVehCAP = Param(default=0, mutable=True) # valor = 22 pallets
    model.pFleetSize = Param(default=0, mutable=True) # valor= 8 vehicles
    model.pLoadTime = Param(default=0, mutable=True) # valor= 1 min
    model.pUnloadTime = Param(default=0, mutable=True) # valor = 0.5 min
    model.pReqTimeLimit = Param(default=0, mutable=True) # valor = 8 hours = 480 min
    model.pOptTimeLimit = Param(default=0, mutable=True) # valor = 10 hours = 600 min
    model.pBigM1 = Param(default=0, mutable=True) # valor = max TripDuration = 35 min
    model.pBigM2 = Param(default=0, mutable=True) # valor = OptTimeLimit = 600 min
    model.pBigM3 = Param(default=0, mutable=True) # valor = OptTimeLimit-ReqTimeLimit = 120 min

    model.pTripDuration = Param(model.sWarehouses, model.sWarehouses, mutable=True) #esto es una lista/tabla


    # Binary Variables
    model.vAlpha = Var(model.sVehicles, model.sStops, model.sWarehouses, domain=Binary)
    model.vBeta1 = Var(model.sVehicles, model.sStops, model.sVehicles, model.sStops, domain=Binary)
    model.vBeta2 = Var(model.sVehicles, model.sStops, model.sVehicles, model.sStops, domain=Binary)
    model.vGamma = Var(model.sVehicles, model.sStops, domain=Binary)


    # Continuous Variables
    model.vArrivalTime = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
    model.vDepartureTime = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
    model.vUnloadTime = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
    model.vLoadDuration = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
    model.vUnloadDuration = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
    model.vQuantity = Var(model.sVehicles, model.sStops, model.sCommodities, domain=NonNegativeReals)
    model.vLoadQuantity = Var(model.sVehicles, model.sStops, model.sCommodities, domain=NonNegativeReals)
    model.vUnloadQuantity = Var(model.sVehicles, model.sStops, model.sCommodities, domain=NonNegativeReals)
    model.vTripDuration = Var(model.sTripDuration, domain=NonNegativeReals)

    # Constraints
    def fc1_balance_commodities(model, v, s):
        s2 = s + 1
        return sum(model.vQuantity[v, s2, c] for c in model.sCommodities) == \
            sum(model.vQuantity[v, s, c] for c in model.sCommodities) - \
            sum(model.vUnloadQuantity[v, s, c] for c in model.sCommodities) + \
            sum(model.vLoadQuantity[v, s, c] for c in model.sCommodities)
    def fc2_cap_max(model, v, s):
        return sum(model.vQuantity[v, s, c] for c in model.sCommodities) <= model.pVehCAP

    def fc3_load_req(model, c):
        if model.sCommodities[3]==1:
            return sum(model.vLoadQuantity[v, s, c] for v in model.sVehicles \
            for s in model.sStops) == model.sCommodities[2]
        else:
            return Constraint.skip
    def fc4_unload_req(model, c):
        if model.sCommodities[3] == 1:
            return sum(model.vUnloadQuantity[v, s, c] for v in model.sVehicles \
            for s in model.sStops) == model.sCommodities[2]
        else:
            return Constraint.skip
    def fc5_correct_unload(model, v, s, w):
        if model.sCommodities[1]==model.sWarehouses:
            return sum(model.vUnloadQuantity[v, s, c] for c in model.sCommodities) <= \
            model.sCommodities[2] * model.vAlpha[v, s, w]
        else:
            return Constraint.skip

    def fc6_max_load(model, v, s, w):
        if model.sCommodities[1] == model.sWarehouses:
            return sum(model.vLoadQuantity[v, s, c] for c in model.sCommodities) <= \
            model.sCommodities[2] * model.vAlpha[v, s, w]  #model.sCommodities[2]
        else:
            return Constraint.skip
    def fc7_trip_duration(model, v, s, w, w2):
        if w!=w2:
            s2 = s + 1
            return model.vTripDuration[v, s, s2] >= model.pTripDuration[w, w2] \
            - model.pBigM1 * (2-model.vAlpha[v, s, w]-model.vAlpha[v, s2, w2])
        else:
            return Constraint.skip
    def fc8_unload_time(model, v, s):
        return model.vUnloadDuration[v, s] == sum(model.vUnloadQuantity[v, s, c] for c in model.sCommodities) \
        * model.pUnloadTime

    def fc9_load_time(model, v, s):
        return model.vLoadDuration[v, s] == sum(model.vLoadQuantity[v, s, c] for c in model.sCommodities) \
        * model.pLoadTime
    def fc10_departure_time(model, v, s):
        return model.vDepartureTime[v, s] == model.vArrivalTime[v, s] + model.vLoadDuration[v, s] + model.vUnloadDuration[v, s]
    def fc11_arrival_time(model, v, s):
        s2=s+1
        return model.vArrivalTime[v, s2] == model.vDepartureTime[v, s] + model.vTripDuration[v, s, s2]
    def fc12_unload_time(model, v, s):
        return model.vUnloadTime[v, s] == model.vArrivalTime[v, s] + model.vUnloadDuration[v, s]
    def fc13_simultaneidad_veh_1(model, v, s, v2, s2):
        if v!=v2:
            return model.vBeta1[v, s, v2, s2] + model.vBeta2[v2, s2, v, s] >= model.vAlpha[v, s, w] \
                   + model.vAlpha[v2, s2, w] -1
        else:
            return Constraint.skip
    def fc14_simultaneidad_veh_2(model, v, s, v2, s2):
        if v!= v2:
            return model.vArrivalTime[v, s]>= model.vDepartureTime[v, s]- (1-model.vBeta1[v, s, v2, s2]) * model.pBigM2
        else:
            return Constraint.skip
    def fc15_time_limit_1(model, v, s):
        return model.vUnloadTime[v, s] <= model.pReqTimeLimit + model.vGamma[v, s] * model.pBigM3
    def fc16_time_limit_2(model, v, s, c):
        if model.sCommodities[3]==1:
            return model.vLoadQuantity[v, s, c] <= (1-model.vGamma[v, s]) * model.pVehCAP
        else:
            return Constraint.skip
    def fc17_time_limit_3(model, v, s):
        return model.vUnloadTime[v, s] <= model.pOptTimeLimit


    # Activate constraints
    model.c1_balance_commodities = Constraint(model.sVehicles, model.sStopsButLast, rule=fc1_balance_commodities)
    model.c2_cap_max = Constraint(model.sVehicles, model.sStops, rule=fc2_cap_max)
    model.c3_load_req = Constraint(model.sCommodities, rule=fc3_load_req)
    model.c4_unload_req = Constraint(model.sCommodities, rule=fc4_unload_req)
    model.c5_correct_unload = Constraint(model.sVehicles, model.sStops, model.sWarehouses, rule=fc5_correct_unload)
    model.c6_max_load = Constraint(model.sVehicles, model.sStops, model.sWarehouses, rule=fc6_max_load)
    model.c7_trip_duration = Constraint(model.c7_constraint_domain, rule=fc7_trip_duration)
    model.c8_unload_time = Constraint(model.sVehicles, model.sStops, rule=fc8_unload_time)
    model.c9_load_time = Constraint(model.sVehicles, model.sStops, rule=fc9_load_time)
    model.c10_departure_time = Constraint(model.sVehicles, model.sStops, rule=fc10_departure_time)
    model.c11_arrival_time = Constraint(model.sVehicles, model.sStops, rule=fc11_arrival_time)
    model.c12_unload_time = Constraint(model.sVehicles, model.sStops, rule=fc12_unload_time)
    model.c13_simultaneidad_veh_1 = Constraint(model.sVehicles, model.sStops, model.sVehicles, model.sStops, rule=fc13_simultaneidad_veh_1)
    model.c14_simultaneidad_veh_2 = Constraint(model.sVehicles, model.sStops, model.sVehicles, model.sStops, rule=fc14_simultaneidad_veh_2)
    model.c15_time_limit_1 = Constraint(model.sVehicles, model.sStops, rule=fc15_time_limit_1)
    model.c16_time_limit_2 = Constraint(model.sVehicles, model.sStops, model.sCommodities, rule=fc16_time_limit_2)
    model.c17_time_limit_3 = Constraint(model.sVehicles, model.sStops, rule=fc17_time_limit_3)

    return model
