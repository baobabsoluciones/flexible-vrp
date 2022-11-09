from pyomo.environ import *

# black won't reformat this file.
# fmt: off


def create_model():

    # Create model
    model = AbstractModel()

    # Sets
    model.sVehicles = Set()
    model.sStops = Set()
    model.sWarehouses = Set()
    model.sCommodities = Set()

    # Derived sets
    model.sTripDurationDomain = Set(dimen=3)

    # TO-DO: esto será la definición del conjunto
    # vTripDurationDomin = [(v, s, s2) for v in sVehicles for s in sStops for s2 in sStops
    #                       if sStops.index_set(s2) = sStops.index_set(s) + 1]

    # Parameters
    model.pReqCommodity = Param(,mutable=True)
    model.pLoadTime = Param(,mutable=True) # 1 min
    model.pUnloadTime = Param(,mutable=True) # 0.5 min
    model.pVehCAP = Param(,mutable=True) # 22 pallets
    model.pFleetSize = Param(,mutable=True) # 8 vehicles
    model.pReqTimeLimit = Param(,mutable=True) #8 horas=480 min
    model.pOptTimeLimit = Param(,mutable=True) #10 horas=600 min
    model.pTripDuration = Param(model.sWarehouses * model.sWarehouses)
    model.pOrigin = Param(model.sCommodities[0],mutable=True)
    model.pDestination = Param(model.sCommodities[1],mutable=True)
    model.pQuantity = Param(model.sCommodities[2], mutable=True)
    model.pBigM1 = Param(,mutable=True)
    model.pBigM2 = Param(,mutable=True)
    model.pBigM3 = Param(,mutable=True)

    # Binary Variables
    model.vAlpha = Var(model.sVehicles, model.sStops, model.sWarehouses, domain=Binary)
    model.vBeta = Var(model.sVehicles, model.sStops, model.sVehicles, model.sStops, domain=Binary)
    model.vBeta = Var(model.sVehicles, model.sStops, model.sVehicles, model.sStops, domain=Binary)
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
    model.vTripDuration = Var(model.sTripDurationDomain, domain=NonNegativeReals)

    # Constraints
    def fcMaxVehCAP(model, v, s):
        return sum(model.vQuantity[v, s, c] for c in model.sCommodities) <= model.pCapacity


    # Activate constraints

    return model


# fmt: on
