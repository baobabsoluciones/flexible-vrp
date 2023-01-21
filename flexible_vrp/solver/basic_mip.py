# Class to solve the problem with a basic mip.
import pandas as pd

from flexible_vrp.core import Experiment, Solution
from flexible_vrp.solver.basic_mip_tools.create_model import create_model
from pyomo.environ import SolverFactory
from cornflow_client.constants import PYOMO_STOP_MAPPING


class BasicMip(Experiment):
    def __init__(self, instance, solution=None):
        super().__init__(instance, solution)

    def prepare_model_data(self):
        # data is the dict that is filled in and returned
        # Calculating MILP parameters and sets
        """
        # Estimating bigMs
        # Todo: estimate values as a function of instance parameters
        bigM1 = max (data['pTripDuration'])
        bigM2 = data['pOptTimeLimit']
        bigM3 = (data['pOptTimeLimit'] - data['pReqTimeLimit'])
        """
        # Generating the dictionary for Pyomo

        data = dict()

        # Adding the set for Warehouses
        # Retrieving origins and destination
        origins = set([c["location1"] for c in self.instance.data["trip_durations"]])
        destinations = set(
            [c["location2"] for c in self.instance.data["trip_durations"]]
        )
        # Getting a list from the union of destinations and origins
        warehouses = list(origins.union(destinations))
        # Adding the info to the output dict
        data["sWarehouses"] = {None: warehouses}

        # Adding the set for Commodities
        data["sCommodities"] = {
            None: [
                (c["origin"], c["destination"], c["quantity"], c["required"])
                for c in self.instance.data["commodities"]
            ]
        }
        # todo: estimate the number of stops for the current data. Remove from this method
        self.instance.data["parameters"]["no_stops"] = 5
        # Adding the set for Stops
        data["sStops"] = {
            None: [s for s in range(int(self.instance.data["parameters"]["no_stops"]))]
        }
        data["sStopsButLast"] = {
            None: [
                s for s in range(int(self.instance.data["parameters"]["no_stops"] - 1))
            ]
        }
        # Adding the set for Vehicles
        data["sVehicles"] = {
            None: [
                v for v in range(int(self.instance.data["parameters"]["fleet_size"]))
            ]
        }

        data["sTripDuration"] = {
            None: [
                (v, s, s + 1) for v in range(int(self.instance.data["parameters"]["fleet_size"]))
                for s in range(int(self.instance.data["parameters"]["no_stops"] - 1))
            ]
        }
        # Adding the parameters
        data["pVehCAP"] = {None: self.instance.data["parameters"]["vehicle_capacity"]}
        data["pFleetSize"] = {None: self.instance.data["parameters"]["fleet_size"]}
        data["pLoadTime"] = {None: self.instance.data["parameters"]["load_pallet"]}
        data["pUnloadTime"] = {None: self.instance.data["parameters"]["unload_pallet"]}
        data["pReqTimeLimit"] = {
            None: self.instance.data["parameters"]["req_time_limit"]
        }
        data["pOptTimeLimit"] = {
            None: self.instance.data["parameters"]["opt_time_limit"]
        }

        # Adding the pCommodities parameter
        data["pTripDuration"] = {
            (x["location1"], x["location2"]): x["time"]
            for x in self.instance.data["trip_durations"]
        }

        # Adding the parameters BigM

        data["pBigM1"] = {None: max(data["pTripDuration"].values())}
        data["pBigM2"] = data["pOptTimeLimit"]
        data["pBigM3"] = {None: data["pOptTimeLimit"][None] - data["pReqTimeLimit"][None]}

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
        status = PYOMO_STOP_MAPPING[result.solver.termination_condition]
        self.get_solution(model_instance)
        self.status = self.get_status(result)
        model_result = model_instance
        obj = model_instance.f_obj()
        print("Status: {} Objective value: {}".format(self.status, obj))

        # # Prepare solution
        # if self.is_feasible(self.status): #todo: create method
        #     self.totals = self.get_total(model_result, result)
        #     model_solution = self.get_model_solution(model_result)
        #     self.solution = Solution(self.build_solution(model_solution))
        # else:
        #     self.solution = self.get_empty_solution()
        #     self.variables_to_excel(model_result)

        return 1  # dict(status=STATUS_TIME_LIMIT, status_sol=SOLUTION_STATUS_FEASIBLE)

        # Example of solve method:
        #
        # model = create_model()
        #
        # model_instance = model.create_instance(data, report_timing=False)
        # logfile = "./data/logfile.log"
        # # Solve
        # opt = self.set_solver(options)
        # try:
        #     result = opt.solve(
        #         model_instance,
        #         tee=True,
        #         warmstart=False,
        #         logfile=logfile,
        #     )
        # except ApplicationError:
        #     message = "Solver error: a solver license may not be available to solve the model."
        #     raise Exception(message)
        #
        # self.status = get_status(result)
        # model_result = model_instance
        # obj = model_instance.f_obj()
        # print("Status: {} Objective value: {}".format(self.status, obj))
        #
        # # Prepare solution
        # if is_feasible(self.status):
        #     self.totals = self.get_total(model_result, result)
        #     model_solution = self.get_model_solution(model_result)
        #     self.solution = Solution(self.build_solution(model_solution))
        # else:
        #     self.solution = self.get_empty_solution()
        #     self.variables_to_excel(model_result)
        #
        # return dict(status=STATUS_TIME_LIMIT, status_sol=SOLUTION_STATUS_FEASIBLE)

        model = create_model()
        self.solution = Solution({"data": "This solver is not implemented yet"})
        return {}

    def set_solver(self, options):
        # Create the solver object and set the relevant options.
        #
        # param options: dict of options.
        # :return: the pyomo solver
        if "solver_name" in options:
            opt = SolverFactory(options["solver_name"])
        else:
            opt = SolverFactory("cbc")
        if "solver_config" in options:
            opt.options.update(options["solver_config"])
        return opt

    def get_solution(self, model_instance):
        data = [[v, s, w, c[0], c[1], c[2], c[3],
                model_instance.vQuantityAtArrival[v, s, c].value,
                model_instance.vLoadQuantity[v, s, c].value,
                model_instance.vUnloadQuantity[v, s, c].value]
                for v in model_instance.sVehicles
                for s in model_instance.sStops
                for w in model_instance.sWarehouses
                for c in model_instance.sCommodities
                if model_instance.vLoadQuantity[v, s, c].value +
                model_instance.vUnloadQuantity[v, s, c].value +
                model_instance.vQuantityAtArrival[v, s, c].value
                > 0
                and model_instance.vAlpha[v, s, w].value == 1
                ]
        df = pd.DataFrame(data, columns=["Vehicle", "Stop", "Warehouse", "Comm (or.)", "Comm (dest.)", "Comm (qty)",
                                         "Comm (comp.)", "Qty (arr)", "Load", "Unload"])
        df["Qty (dep)"] = df.groupby(by=["Vehicle", "Comm (or.)", "Comm (dest.)", "Comm (qty)",
                                         "Comm (comp.)"])["Qty (arr)"].shift(-1)
        df["Qty (dep)"].fillna(0, inplace=True)

        warehouses_visited = {(v, s): w for v in model_instance.sVehicles for s in model_instance.sStops for
                              w in model_instance.sWarehouses if model_instance.vAlpha[v, s, w].value == 1}

        trip_durations = {(v, s): model_instance.pTripDuration[warehouses_visited[v,s], warehouses_visited[v, s + 1]].value for
                          v in model_instance.sVehicles for s in model_instance.sStopsButLast
                          if (v, s) in warehouses_visited.keys() and (v, s + 1) in warehouses_visited.keys()}

        trip_durations = {
            (v, s): (model_instance.pTripDuration[warehouses_visited[v, s], warehouses_visited[v, s + 1]].value if
                     (v, s + 1) in warehouses_visited.keys() else 0) for
            v in model_instance.sVehicles for s in model_instance.sStopsButLast
            if (v, s) in warehouses_visited.keys()}


        for v in model_instance.sVehicles:
            trip_durations[v, len(model_instance.sStops) - 1] = "-"

        data = [[v, s, w, model_instance.vArrivalTime[v, s].value,
                 model_instance.vUnloadDuration[v, s].value,
                 model_instance.vLoadDuration[v, s].value,
                 model_instance.vDepartureTime[v, s].value,
                 trip_durations[v,s]]
                for v in model_instance.sVehicles
                for s in model_instance.sStops
                for w in model_instance.sWarehouses
                if model_instance.vAlpha[v, s, w].value == 1
                ]
        df_times = pd.DataFrame(data, columns=["Vehicle", "Stop", "Warehouse", "Arr. time", "Unload dur.", "Load dur.",
                                               "Dep. time", "Trip dur."])

        return df, df_times
