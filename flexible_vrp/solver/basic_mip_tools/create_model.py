import pyomo.core
from pyomo.contrib.sensitivity_toolbox import sens
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
    model.sCommodities = Set(dimen=4)

    # Derived sets
    model.sTripDuration = Set(dimen=3)
    model.c7_constraint_domain = Set(dimen=4)

    # Parameters
    model.pVehCAP = Param(default=0, mutable=True)  # valor = 22 pallets
    model.pFleetSize = Param(default=0, mutable=True)  # valor= 8 vehicles
    model.pLoadTime = Param(default=0, mutable=True)  # valor= 1 min
    model.pUnloadTime = Param(default=0, mutable=True)  # valor = 0.5 min
    model.pReqTimeLimit = Param(default=0, mutable=True)  # valor = 8 hours = 480 min
    model.pOptTimeLimit = Param(default=0, mutable=True)  # valor = 10 hours = 600 min
    model.pBigM1 = Param(default=0, mutable=True)  # valor = max TripDuration = 35 min
    model.pBigM2 = Param(default=0, mutable=True)  # valor = OptTimeLimit = 600 min
    model.pBigM3 = Param(default=0, mutable=True)  # valor = OptTimeLimit-ReqTimeLimit = 120 min
    model.pTripDuration = Param(model.sWarehouses, model.sWarehouses, mutable=True)  # esto es una lista/tabla

    # Binary Variables
    model.vAlpha = Var(model.sVehicles, model.sStops, model.sWarehouses, domain=Binary)
    model.vBeta1 = Var(model.sVehicles, model.sStops, model.sVehicles, model.sStops, domain=Binary)
    model.vBeta2 = Var(model.sVehicles, model.sStops, model.sVehicles, model.sStops, domain=Binary)
    model.vGamma = Var(model.sVehicles, model.sStops, domain=Binary)

    # Continuous Variables
    model.vQuantity = Var(model.sVehicles, model.sStops, model.sCommodities, domain=NonNegativeReals)
    model.vLoadQuantity = Var(model.sVehicles, model.sStops, model.sCommodities, domain=NonNegativeReals)
    model.vUnloadQuantity = Var(model.sVehicles, model.sStops, model.sCommodities, domain=NonNegativeReals)
    model.vTotalNonCompulsory = Var(domain=NonNegativeReals)
    model.vTripDuration = Var(model.sTripDuration, domain=NonNegativeReals)
    model.vArrivalTime = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
    model.vDepartureTime = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
    model.vUnloadTime = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
    model.vLoadDuration = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
    model.vUnloadDuration = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
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

    def fc3_load_req(model, origin, destination, quantity, compulsory):
        if compulsory == 1:
            return sum(model.vLoadQuantity[v, s, origin, destination, quantity, compulsory] for v in model.sVehicles
                       for s in model.sStops) == quantity
        else:
            return Constraint.Skip

    def fc4_unload_req(model, origin, destination, quantity, compulsory):
        if compulsory == 1:
            return sum(model.vUnloadQuantity[v, s, origin, destination, quantity, compulsory] for v in model.sVehicles
                       for s in model.sStops) == quantity
        else:
            return Constraint.Skip

    def fc5_correct_unload(model, v, s, w):
        if model.sCommodities[1] == model.sWarehouses:
            return sum(model.vUnloadQuantity[v, s, c] for c in model.sCommodities) <= \
                   model.sCommodities[2] * model.vAlpha[v, s, w]
        else:
            return Constraint.Skip

    def fc6_max_load(model, v, s, w):
        if model.sCommodities[1] == model.sWarehouses:
            return sum(model.vLoadQuantity[v, s, c] for c in model.sCommodities) <= \
                   model.sCommodities[2] * model.vAlpha[v, s, w]  # model.sCommodities[2]
        else:
            return Constraint.Skip

    def fc7_zero_load_on_last_stop(model, v):
        s = model.sStops[len(model.sStops)-1]
        return sum(model.vLoadQuantity[v, s, c] for c in model.sCommodities) == 0

    def fc8_load_max_veh(model, v, s):
        return sum(model.vLoadQuantity[v, s, c] for c in model.sCommodities) <= model.pVehCAP

    def fc9_unload_max_veh(model, v, s):
        return sum(model.vUnloadQuantity[v, s, c] for c in model.sCommodities) <= model.pVehCAP

    def fc_10_total_non_compulsory(model):
        return model.vTotalNonCompulsory == sum(model.vUnloadQuantity[v, s, c]
                                                for v in model.sVehicles
                                                for s in model.sStops
                                                for c in model.sCommodities
                                                if c[3] == 0)

    def fc_11_total_non_compulsory_bound(model):
        return model.vTotalNonCompulsory <= sum(c[2] for c in model.sCommodities
                                                if c[3] == 0)

    def fc12_trip_duration(model, v, s, w, w2):
        if w != w2:
            s2 = s + 1
            return model.vTripDuration[v, s, s2] >= model.pTripDuration[w, w2] \
                - model.pBigM1 * (2 - model.vAlpha[v, s, w] - model.vAlpha[v, s2, w2])
        else:
            return Constraint.Skip

    def fc13_unload_time(model, v, s):
        return model.vUnloadDuration[v, s] == sum(model.vUnloadQuantity[v, s, c] for c in model.sCommodities) \
               * model.pUnloadTime

    def fc14_load_time(model, v, s):
        return model.vLoadDuration[v, s] == sum(model.vLoadQuantity[v, s, c] for c in model.sCommodities) \
               * model.pLoadTime

    def fc15_departure_time(model, v, s):
        return model.vDepartureTime[v, s] == model.vArrivalTime[v, s] + model.vLoadDuration[v, s] \
               + model.vUnloadDuration[v, s]

    def fc16_arrival_time(model, v, s):
        s2 = s + 1
        return model.vArrivalTime[v, s2] == model.vDepartureTime[v, s] + model.vTripDuration[v, s, s2]

    def fc17_unload_time(model, v, s):
        return model.vUnloadTime[v, s] == model.vArrivalTime[v, s] + model.vUnloadDuration[v, s]

    def fc18_simultaneity_veh_1(model, v, s, v2, s2, w):
        if v != v2:
            return model.vBeta1[v, s, v2, s2] + model.vBeta2[v2, s2, v, s] >= model.vAlpha[v, s, w] \
                   + model.vAlpha[v2, s2, w] - 1
        else:
            return Constraint.Skip

    def fc19_simultaneity_veh_2(model, v, s, v2, s2):
        if v != v2:
            return model.vArrivalTime[v, s] >= model.vDepartureTime[v, s] - (1-model.vBeta1[v, s, v2, s2]) \
                   * model.pBigM2
        else:
            return Constraint.Skip

    def fc20_time_limit_1(model, v, s):
        return model.vUnloadTime[v, s] <= model.pReqTimeLimit + model.vGamma[v, s] * model.pBigM3

    def fc21_time_limit_2(model, v, s, origin, destination, quantity, compulsory):
        if model.sCommodities[3] == 1:
            return model.vLoadQuantity[v, s, origin, destination, quantity, compulsory] <= (1-model.vGamma[v, s]) \
                   * model.pVehCAP
        else:
            return Constraint.Skip

    def fc22_time_limit_3(model, v, s):
        return model.vUnloadTime[v, s] <= model.pOptTimeLimit

    # Objective Function
    def f_obj_expression(model):
        return model.vTotalNonCompulsory

    # Activate constraints
    model.c1_balance_commodities = Constraint(model.sVehicles, model.sStopsButLast, rule=fc1_balance_commodities)
    model.c2_cap_max = Constraint(model.sVehicles, model.sStops, rule=fc2_cap_max)
    model.c3_load_req = Constraint(model.sCommodities, rule=fc3_load_req)
    model.c4_unload_req = Constraint(model.sCommodities, rule=fc4_unload_req)
    model.c5_correct_unload = Constraint(model.sVehicles, model.sStops, model.sWarehouses, rule=fc5_correct_unload)
    model.c6_max_load = Constraint(model.sVehicles, model.sStops, model.sWarehouses, rule=fc6_max_load)
    model.c7_zero_load_on_last_stop = Constraint(model.sVehicles, rule=fc7_zero_load_on_last_stop)
    model.c8_load_max_veh = Constraint(model.sVehicles, model.sStops, rule=fc8_load_max_veh)
    model.c9_unload_max_veh = Constraint(model.sVehicles, model.sStops, rule=fc9_unload_max_veh)
    model.c10_no_total_compulsory = Constraint(rule=fc_10_total_non_compulsory)
    model.c11_total_non_compulsory_bound = Constraint(rule=fc_11_total_non_compulsory_bound)
    # model.c12_trip_duration = Constraint(model.c7_constraint_domain, model.sStopsButLast, rule=fc12_trip_duration)
    # model.c13_unload_time = Constraint(model.sVehicles, model.sStops, rule=fc13_unload_time)
    # model.c14_load_time = Constraint(model.sVehicles, model.sStops, rule=fc14_load_time)
    # model.c15_departure_time = Constraint(model.sVehicles, model.sStops, rule=fc15_departure_time)
    # model.c16_arrival_time = Constraint(model.sVehicles, model.sStopsButLast, rule=fc16_arrival_time)
    # model.c17_unload_time = Constraint(model.sVehicles, model.sStops, rule=fc17_unload_time)
    # model.c18_simultaneity_veh_1 = Constraint(model.sVehicles, model.sStops, model.sVehicles, model.sStops,
    #                                            model.sWarehouses, rule=fc18_simultaneity_veh_1)
    # model.c19_simultaneity_veh_2 = Constraint(model.sVehicles, model.sStops, model.sVehicles, model.sStops,
    #                                            rule=fc19_simultaneity_veh_2)
    # model.c20_time_limit_1 = Constraint(model.sVehicles, model.sStops, rule=fc20_time_limit_1)
    # model.c21_time_limit_2 = Constraint(model.sVehicles, model.sStops, model.sCommodities, rule=fc21_time_limit_2)
    # model.c22_time_limit_3 = Constraint(model.sVehicles, model.sStops, rule=fc22_time_limit_3)

    # Activate Objetive function
    model.obj_func = Objective(rule=f_obj_expression, sense=pyomo.core.maximize)
    return model
# fmt: on
