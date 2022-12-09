# Class to solve the problem with a basic mip.

from ..core import Experiment, Solution
from .basic_mip_tools.create_model import create_model
from pyomo.environ import SolverFactory
import pandas as pd

class BasicMip(Experiment):
    def __init__(self, instance, solution=None):
        super().__init__(instance, solution)

    def prepare_model_data(self):
        # data is the dict that is filled in and returned
        # Calculating MILP parameters and sets

        # Estimating bigMs
        # Todo: estimate values as a funcion of instance parameters
        bigM1 = 100
        bigM2 = 100
        bigM3 = 100

        # Generating the dictionary for Pyomo
        data = dict()


        data = dict()

        # Adding the parameters
        data['pVehCAP'] = {None: self.instance.data['parameters']['vehicle_capacity']}
        # Todo: hacer lo mismo para el resto de parámetros

        # Adding the sWarehouses set.
        # Retrieving orings and destination
        origins = set([c['location1'] for c in self.instance.data['trip_durations']])
        destinations = set([c['location2'] for c in self.instance.data['trip_durations']])
        # Getting a list from the union of destinations and origins
        warehouses = list(origins.union(destinations))
        # Adding the info to the output dict
        data['sWarehouses'] = {None: warehouses}

        # Adding the sCommodities set
        data['sCommodities'] = {None: [(c['origin'], c['destination'], c['quantity'], c['required'])
                                    for c in self.instance.data['commodities']]}

        # Adding the pCommodities parameter
        data['pTripDuration'] = {(x['location1'], x['location2']): x['time'] for x in self.instance.data['trip_durations']}

        # Adding the set for Stops
        data['sStops'] = {None: [s for s in range(self.instance.data['parameters']['no_stops'])]}

        return {None: data}

    def solve(self, options):
        if not self.instance.to_dict():
            raise ValueError("The instance is empty")

        data = self.prepare_model_data()

        # Todo: replace this by the solve method
        model = create_model()

        model_instance = model.create_instance(data, report_timing=False)

        logfile = "./data/logfile.log"

        # Solve
        opt = self.set_solver(options)
        result = opt.solve(
            model_instance,
            tee=True,
            warmstart=False,
            logfile=logfile,
        )

        self.status = self.get_status(result) # todo: create method
        model_result = model_instance
        obj = model_instance.f_obj()
        print("Status: {} Objective value: {}".format(self.status, obj))
        #
        # # Prepare solution
        # if self.is_feasible(self.status): #todo: create method
        #     self.totals = self.get_total(model_result, result)
        #     model_solution = self.get_model_solution(model_result)
        #     self.solution = Solution(self.build_solution(model_solution))
        # else:
        #     self.solution = self.get_empty_solution()
        #     self.variables_to_excel(model_result)

        return 1 #dict(status=STATUS_TIME_LIMIT, status_sol=SOLUTION_STATUS_FEASIBLE)


        """
        Example of solve method:
        
        model = create_model()        

        model_instance = model.create_instance(data, report_timing=False)
        logfile = "./data/logfile.log"
        # Solve
        opt = self.set_solver(options)
        try:
            result = opt.solve(
                model_instance,
                tee=True,
                warmstart=False,
                logfile=logfile,
            )
        except ApplicationError:
            message = "Solver error: a solver license may not be available to solve the model."
            raise Exception(message)

        self.status = get_status(result)
        model_result = model_instance
        obj = model_instance.f_obj()
        print("Status: {} Objective value: {}".format(self.status, obj))

        # Prepare solution
        if is_feasible(self.status):
            self.totals = self.get_total(model_result, result)
            model_solution = self.get_model_solution(model_result)
            self.solution = Solution(self.build_solution(model_solution))
        else:
            self.solution = self.get_empty_solution()
            self.variables_to_excel(model_result)

        return dict(status=STATUS_TIME_LIMIT, status_sol=SOLUTION_STATUS_FEASIBLE)
        """
        """
        # Sets
       """
        #["v{}".format(n) for n in range(1,NUM+1)]
        """
        listaVeh = []
        Vehicles = listaVeh
        for i in range(sheet_param.cell_value(2, 1)):
            listaVeh.append(i + 1)

        listaStops = []
        Stops = listaStops

        listaW = []
        Wareahouses = listaW
        for i in range(0, sheet_warehouse.nrows):
            listaW.append(sheet_warehouse.cell_value(i, 0))  # como decirle que es str

        listaCom = []
        Commodities = listaCom
        for i in range(0, sheet_inst1.nrows):
            listaCom.append([])
            for j in range(3):
                listaCom[i].append(sheet_inst1.cell_value(i, j))  # str

        # Parameters
        VehCAP = sheet_param.cell_value(1, 1)  # valor = 22 pallets
        FleetSize = sheet_param.cell_value(2, 1)  # valor= 8 vehicles
        LoadTime = sheet_param.cell_value(3, 1)  # valor= 1 min
        UnloadTime = sheet_param.cell_value(4, 1)  # valor = 0.5 min
        ReqTimeLimit = sheet_param.cell_value(5, 1)  # valor = 8 hours = 480 min
        OptTimeLimit = sheet_param.cell_value(6, 1)  # valor = 10 hours = 600 min
        BigM1 = sheet_param.cell_value(7, 1)  # valor = max TripDuration = 35 min
        BigM2 = sheet_param.cell_value(8, 1)  # valor = OptTimeLimit = 600 min
        BigM3 = sheet_param.cell_value(9, 1)  # valor = OptTimeLimit-ReqTimeLimit = 120 min

        listaTrip = []
        TripDuration = listaTrip
        for i in range(0, sheet_trip_duration.nrows):
            listaTrip.append([])
            for j in range(3):
                listaTrip[i].append(sheet_trip_duration.cell_value(i, j))  # leer string
        """
        model = create_model()
        self.solution = Solution({"data": "This solver is not implemented yet"})
        return {}

    def set_solver(self, options):
        """
        Create the solver object and set the relevant options.

        :param options: dict of options.
        :return: the pyomo solver
        """
        if "solver_name" in options:
            opt = SolverFactory(options["solver_name"])
        else:
            opt = SolverFactory("cbc")
        if "solver_config" in options:
            opt.options.update(options["solver_config"])
        return opt