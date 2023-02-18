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
    model.vBeta = Var(model.sVehicles, model.sStops, model.sVehicles, model.sStops, domain=Binary)
    model.vGamma = Var(model.sVehicles, model.sStops, domain=Binary)

    # Continuous Variables
    model.vQuantityAtArrival = Var(model.sVehicles, model.sStops, model.sCommodities, domain=NonNegativeReals)
    model.vLoadQuantity = Var(model.sVehicles, model.sStops, model.sCommodities, domain=NonNegativeIntegers)
    model.vUnloadQuantity = Var(model.sVehicles, model.sStops, model.sCommodities, domain=NonNegativeReals)
    model.vTotalNonCompulsory = Var(domain=NonNegativeReals)
    model.vTripDuration = Var(model.sTripDuration, domain=NonNegativeReals)
    model.vArrivalTime = Var(model.sVehicles, model.sStops, domain=NonNegativeIntegers)
    model.vDepartureTime = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
    model.vUnloadTime = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
    model.vLoadDuration = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
    model.vUnloadDuration = Var(model.sVehicles, model.sStops, domain=NonNegativeReals)
    model.vTripDuration = Var(model.sTripDuration, domain=NonNegativeReals)

    # Balance Constraints

    def fc1_balance_commodities(model, v, s, origin, destination, quantity, compulsory):
        if s == 0:
            return model.vQuantityAtArrival[v, s + 1, origin, destination, quantity, compulsory] == \
                   model.vLoadQuantity[v, s, origin, destination, quantity, compulsory]
        elif s == len(model.sStops) - 1:
            return model.vUnloadQuantity[v, s, origin, destination, quantity, compulsory] == \
                   model.vQuantityAtArrival[v, s, origin, destination, quantity, compulsory]
        else:
            return model.vQuantityAtArrival[v, s + 1, origin, destination, quantity, compulsory] == \
               model.vQuantityAtArrival[v, s, origin, destination, quantity, compulsory] \
               - model.vUnloadQuantity[v, s, origin, destination, quantity, compulsory] \
               + model.vLoadQuantity[v, s, origin, destination, quantity, compulsory]

    def fc2_cap_max(model, v, s):
        return sum(model.vQuantityAtArrival[v, s, c] for c in model.sCommodities) <= model.pVehCAP

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

    def fc5_correct_load(model, v, s, w,  origin, destination, quantity, compulsory):
        if origin == w:
            return model.vLoadQuantity[v, s, origin, destination, quantity, compulsory] <= \
                   quantity * model.vAlpha[v, s, w]
        else:
            return Constraint.Skip

    def fc6_correct_unload(model, v, s, w, origin, destination, quantity, compulsory):
        if destination == w:
            return model.vUnloadQuantity[v, s, origin, destination, quantity, compulsory] <= \
                   quantity * model.vAlpha[v, s, w]
        else:
            return Constraint.Skip

    def fc7_max_load_total_comm(model, origin, destination, quantity, compulsory):
        return sum(model.vLoadQuantity[v, s, origin, destination, quantity, compulsory] for v in model.sVehicles
                   for s in model.sStops) <= quantity

    def fc8_zero_unload_on_first_stop(model, v):
        s = 0
        return sum(model.vUnloadQuantity[v, s, c] for c in model.sCommodities) == 0

    def fc9_load_max_veh(model, v, s):
        return sum(model.vLoadQuantity[v, s, c] for c in model.sCommodities) <= model.pVehCAP

    def fc10_unload_max_veh(model, v, s):
        return sum(model.vUnloadQuantity[v, s, c] for c in model.sCommodities) <= model.pVehCAP

    def fc11_total_non_compulsory_bound(model):
        return model.vTotalNonCompulsory <= sum(c[2] for c in model.sCommodities
                                                if c[3] == 0)

    def fc12_alpha_zero_if_no_load_unload(model, v, s, w):
        return model.vAlpha[v, s, w] <= sum(model.vUnloadQuantity[v, s, c] +
                                            model.vLoadQuantity[v, s, c] for c in model.sCommodities)

    def fc13_single_warehouse_per_stop(model, v, s):
        return sum(model.vAlpha[v, s, w] for w in model.sWarehouses) <= 1

    def fc14_consecutive_stops(model, v, s):
        return sum(model.vAlpha[v, s + 1, w] for w in model.sWarehouses) <= \
                sum(model.vAlpha[v, s, w] for w in model.sWarehouses)

    def fc15_unload_after_load(model, v, s, origin, destination, quantity, compulsory):
        return sum(model.vUnloadQuantity[v, s2, origin, destination, quantity, compulsory] for s2 in model.sStops
                   if s2 <= s) <= sum(model.vLoadQuantity[v, s2, origin, destination, quantity, compulsory]
                                      for s2 in model.sStops if s2 < s)

    def fc16_consecutive_stops_diff_warehouse(model, v, s, w):
        return model.vAlpha[v, s + 1, w] <= 1 - model.vAlpha[v, s, w]

    # Time Constraints
    def fc17_trip_duration(model, v, s, w, w2):
        if w != w2:
            return model.vTripDuration[v, s, s + 1] >= model.pTripDuration[w, w2] \
                - model.pBigM1 * (2 - model.vAlpha[v, s, w] - model.vAlpha[v, s + 1, w2])
        else:
            return Constraint.Skip

    def fc18_load_duration(model, v, s):
        return model.vLoadDuration[v, s] == sum(model.vLoadQuantity[v, s, c] for c in model.sCommodities) \
               * model.pLoadTime

    def fc19_unload_duration(model, v, s):
        return model.vUnloadDuration[v, s] == sum(model.vUnloadQuantity[v, s, c] for c in model.sCommodities) \
               * model.pUnloadTime

    def fc20_arrival_time(model, v, s):
        return model.vArrivalTime[v, s + 1] == model.vDepartureTime[v, s] + model.vTripDuration[v, s, s + 1]

    def fc21_departure_time(model, v, s):
        return model.vDepartureTime[v, s] == model.vArrivalTime[v, s] + model.vLoadDuration[v, s] \
               + model.vUnloadDuration[v, s]

    def fc22_unload_time(model, v, s):
        return model.vUnloadTime[v, s] == model.vArrivalTime[v, s] + model.vUnloadDuration[v, s]

    def fc23_simultaneity_veh_1(model, v, s, v2, s2, w):
        if v != v2:
            return model.vBeta[v, s, v2, s2] + model.vBeta[v2, s2, v, s] >= model.vAlpha[v, s, w] \
                   + model.vAlpha[v2, s2, w] - 1
        else:
            return Constraint.Skip

    def fc24_simultaneity_veh_2(model, v, s, v2, s2):
        if v != v2:
            return model.vArrivalTime[v2, s2] >= model.vDepartureTime[v, s] - (1 - model.vBeta[v, s, v2, s2]) \
                   * model.pBigM2
        else:
            return Constraint.Skip

    def fc25_optional_time_limit(model, v, s):
        return model.vUnloadTime[v, s] <= model.pOptTimeLimit

    def fc26_required_time_limit(model, v, s):
        return model.vUnloadTime[v, s] <= model.pReqTimeLimit + model.vGamma[v, s] * model.pBigM3

    def fc27_load_time_limit(model, v, s, origin, destination, quantity, compulsory):
        if compulsory == 1:
            return model.vLoadQuantity[v, s, origin, destination, quantity, compulsory] <= (1-model.vGamma[v, s]) \
                   * model.pVehCAP
        else:
            return Constraint.Skip

    def fc28_unload_time_limit(model, v, s, origin, destination, quantity, compulsory):
        if compulsory == 1:
            return model.vUnloadQuantity[v, s, origin, destination, quantity, compulsory] <= (1-model.vGamma[v, s]) \
                   * model.pVehCAP
        else:
            return Constraint.Skip

    # Objective Function
    def f_obj_expression(model):
        return sum(model.vUnloadQuantity[v, s, c]
                   for v in model.sVehicles
                   for s in model.sStops
                   for c in model.sCommodities
                   if c[3] == 0)

    # Activate constraints
    model.c1_balance_commodities = Constraint(model.sVehicles, model.sStops, model.sCommodities,
                                              rule=fc1_balance_commodities)
    model.c2_cap_max = Constraint(model.sVehicles, model.sStops, rule=fc2_cap_max)
    model.c3_load_req = Constraint(model.sCommodities, rule=fc3_load_req)
    model.c4_unload_req = Constraint(model.sCommodities, rule=fc4_unload_req)
    model.c5_correct_load = Constraint(model.sVehicles, model.sStops, model.sWarehouses, model.sCommodities,
                                       rule=fc5_correct_load)
    model.c6_correct_unload = Constraint(model.sVehicles, model.sStops, model.sWarehouses, model.sCommodities,
                                         rule=fc6_correct_unload)
    model.c7_max_load_total_comm = Constraint(model.sCommodities, rule=fc7_max_load_total_comm)
    model.c8_zero_unload_on_first_stop = Constraint(model.sVehicles, rule=fc8_zero_unload_on_first_stop)
    model.c9_load_max_veh = Constraint(model.sVehicles, model.sStops, rule=fc9_load_max_veh)
    model.c10_unload_max_veh = Constraint(model.sVehicles, model.sStops, rule=fc10_unload_max_veh)
    model.c11_total_non_compulsory_bound = Constraint(rule=fc11_total_non_compulsory_bound)
    model.c12_alpha_zero_if_no_load_unload = Constraint(model.sVehicles, model.sStops, model.sWarehouses,
                                                        rule=fc12_alpha_zero_if_no_load_unload)
    model.c13_single_warehouse_per_stop = Constraint(model.sVehicles, model.sStops, rule=fc13_single_warehouse_per_stop)
    model.c14_consecutive_stops = Constraint(model.sVehicles, model.sStopsButLast, rule=fc14_consecutive_stops)
    model.c15_unload_after_load = Constraint(model.sVehicles, model.sStops, model.sCommodities,
                                             rule=fc15_unload_after_load)
    model.c16_consecutive_stops_diff_warehouse = Constraint(model.sVehicles, model.sStopsButLast, model.sWarehouses,
                                                            rule=fc16_consecutive_stops_diff_warehouse)
    model.c17_trip_duration = Constraint(model.sVehicles, model.sStopsButLast, model.sWarehouses, model.sWarehouses,
                                         rule=fc17_trip_duration)
    model.c18_load_duration = Constraint(model.sVehicles, model.sStops, rule=fc18_load_duration)
    model.c19_unload_duration = Constraint(model.sVehicles, model.sStops, rule=fc19_unload_duration)
    model.c20_arrival_time = Constraint(model.sVehicles, model.sStopsButLast, rule=fc20_arrival_time)
    model.c21_departure_time = Constraint(model.sVehicles, model.sStops, rule=fc21_departure_time)
    model.c22_unload_time = Constraint(model.sVehicles, model.sStops, rule=fc22_unload_time)
    model.c23_simultaneity_veh_1 = Constraint(model.sVehicles, model.sStops, model.sVehicles, model.sStops,
                                              model.sWarehouses, rule=fc23_simultaneity_veh_1)
    model.c24_simultaneity_veh_2 = Constraint(model.sVehicles, model.sStops, model.sVehicles, model.sStops,
                                              rule=fc24_simultaneity_veh_2)
    model.c25_optional_time_limit = Constraint(model.sVehicles, model.sStops, rule=fc25_optional_time_limit)
    model.c26_required_time_limit = Constraint(model.sVehicles, model.sStops, rule=fc26_required_time_limit)
    model.c27_load_time_limit = Constraint(model.sVehicles, model.sStops, model.sCommodities, rule=fc27_load_time_limit)
    model.c28_unload_time_limit = Constraint(model.sVehicles, model.sStops, model.sCommodities,
                                             rule=fc28_unload_time_limit)

    # Activate Objetive function
    model.obj_func = Objective(rule=f_obj_expression, sense=pyomo.core.maximize)
    return model
# fmt: on
