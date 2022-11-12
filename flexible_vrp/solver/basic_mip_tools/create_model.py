import xlrd
from pyomo.environ import *

# black won't reformat this file.
# fmt: off

# LECTURA DATOS

# ¿Cómo defino la localicion al repositorio de GitHub?
# De manera temporal y a modo de prueba he definido la localización en mi escritorio
location = (r"C:\Users\maria\OneDrive - Universidad Politécnica de Madrid\datos1.xls")
valor = xlrd.open_workbook(location)

hoja_param = valor.sheet_by_name("parameters")
hoja_trp_duration = valor.sheet_by_name("trip_duration")
hoja_inst1 = valor.sheet_by_name("comp_quantity_inst1")

def create_model():
    # Create model
    model = AbstractModel()

    # Sets
    model.sVehicles = Set([1,2,3,4,5,6,7,8])
    model.sStops = Set()
    model.sWarehouses = Set(["T1","T2","T3","T4","T5","F1","F2","F3"])
    model.sCommodities = Set()

    # Derived sets
    model.sTripDurationDomain = Set(dimen=3)

    # TO-DO: esto será la definición del conjunto
    # vTripDurationDomain = [(v, s, s2) for v in sVehicles for s in sStops for s2 in sStops
    #                       if sStops.index_set(s2) = sStops.index_set(s) + 1]



    # Parameters
    model.pVehCAP = Param(hoja_param.cell_value(1, 1), mutable=True) # valor = 22 pallets
    model.pFleetSize = Param(hoja_param.cell_value(2, 1), mutable=True) # valor= 8 vehicles
    model.pLoadTime = Param(hoja_param.cell_value(3, 1), mutable=True) # valor= 1 min
    model.pUnloadTime = Param(hoja_param.cell_value(4, 1), mutable=True) # valor = 0.5 min
    model.pReqTimeLimit = Param(hoja_param.cell_value(5, 1), mutable=True) # valor = 8 hours = 480 min
    model.pOptTimeLimit = Param(hoja_param.cell_value(6, 1), mutable=True) # valor = 10 hours = 600 min
    model.pBigM1 = Param(hoja_param.cell_value(7, 1), mutable=True) # valor = max Quantity = 143 pallets
    model.pBigM2 = Param(hoja_param.cell_value(8, 1), mutable=True) # valor = OptTimeLimit = 600 min
    model.pBigM3 = Param(hoja_param.cell_value(9, 1), mutable=True) # valor = OptTimeLimit-ReqTimeLimit = 120 min

    model.pTripDuration = Param(model.sWarehouses * model.sWarehouses)

    model.pOrigin = Param(model.sCommodities[0], mutable=True)
    model.pDestination = Param(model.sCommodities[1], mutable=True)
    model.pQuantity = Param(model.sCommodities[2], mutable=True)
    model.pReqCommodity = Param(model.sCommodities[3], mutable=True)



    # Binary Variables
    model.vAlpha = Var(model.sVehicles, model.sStops, model.sWarehouses) # domain=Binary)
    model.vBeta = Var(model.sVehicles, model.sStops, model.sVehicles, model.sStops) # domain=Binary)
    model.vBeta = Var(model.sVehicles, model.sStops, model.sVehicles, model.sStops) # domain=Binary)
    model.vGamma = Var(model.sVehicles, model.sStops) # domain=Binary)


    # Continuous Variables
    model.vArrivalTime = Var(model.sVehicles, model.sStops) # domain=NonNegativeReals)
    model.vDepartureTime = Var(model.sVehicles, model.sStops) # domain=NonNegativeReals)
    model.vUnloadTime = Var(model.sVehicles, model.sStops)# domain=NonNegativeReals)
    model.vLoadDuration = Var(model.sVehicles, model.sStos)# domain=NonNegativeReals)
    model.vUnloadDuration = Var(model.sVehicles, model.sStops) # domain=NonNegativeReals)
    model.vQuantity = Var(model.sVehicles, model.sStops, model.sCommodities) # domain=NonNegativeReals)
    model.vLoadQuantity = Var(model.sVehicles, model.sStops, model.sCommodities) # domain=NonNegativeReals)
    model.vUnloadQuantity = Var(model.sVehicles, model.sStops, model.sCommodities) # domain=NonNegativeReals)
    model.vTripDuration = Var(model.sTripDurationDomain) # domain=NonNegativeReals)

    # Constraints
    def fcMaxVehCAP(model, v, s):
        return sum(model.vQuantity[v, s, c] for c in model.sCommodities) <= model.pCapacity


    # Activate constraints

    return model

# fmt: on
