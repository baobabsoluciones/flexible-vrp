# Experiment is the class which is used to solve the problem.
import os
from pytups import TupList

# Imports from cornflow libraries
from cornflow_client import ExperimentCore, get_empty_schema
from cornflow_client.core.tools import load_json

# Imports from internal modules
from .instance import Instance
from .solution import Solution


class Experiment(ExperimentCore):
    schema_checks = load_json(
        os.path.join(os.path.dirname(__file__), "../schemas/solution_checks.json")
    )

    def __init__(self, instance: Instance, solution: Solution):
        super().__init__(instance, solution)
        if solution is None:
            self.solution = Solution({})
        return

    @property
    def instance(self) -> Instance:
        return super().instance

    @property
    def solution(self) -> Solution:
        return super().solution

    @solution.setter
    def solution(self, value):
        self._solution = value

    def get_objective(self) -> float:
        # Todo: create a method to recalculate the objective function.
        return 0

    def check_max_cap(self, data):
        quantity = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="qty_arr").vapply(sum)
        veh_cap = self.instance.data["parameters"]["vehicle_capacity"]
        # This dictionary returns all pairs vehicle-stop where the corresponding vehicle arrives to the stop with a
        # larger amount of commodities than the vehicle capacity.
        max_veh_cap_err = {(v,s): quantity[v,s] - veh_cap for (v,s) in quantity.keys() if quantity[v,s] > veh_cap}
        return max_veh_cap_err

    def check_load_req(self, data):
        actual_load = TupList(data)\
            .to_dict(indices=["comm_or", "comm_dest", "comm_comp"], result_col="load").vapply(sum)
        expected_load = TupList(self.instance.to_dict()['commodities'])\
            .to_dict(indices=["origin", "destination", "required"], result_col="quantity", is_list=False)
        # This is the list of required commodities (origin, destination)
        compulsory_comm = list(set([(c[0], c[1]) for c in expected_load.keys() if c[2] == 1]))
        # This dictionary returns the not unload commodity for every tuple (origin-destination) with some required
        # commodity to be delivered
        load_req_err = {c: expected_load[c + (1,)] - actual_load[c + (1,)] for c in compulsory_comm if actual_load[c + (1,)] < expected_load[c + (1,)]}
        return load_req_err

    def check_required_pallets(self, data):
        actual_unload = TupList(data)\
            .to_dict(indices=["comm_or", "comm_dest", "comm_comp"], result_col="unload").vapply(sum)
        expected_unload = TupList(self.instance.to_dict()['commodities'])\
            .to_dict(indices=["origin", "destination", "required"], result_col="quantity", is_list=False)

        return

    def check_zero_unload(self, data):
        zero_unload = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="unload").vapply(sum)
        # if stop != 0:
        #     error =[vehicle,stop]
        return

    def check_max_load(self, data):
        load = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="load").vapply(sum)
        # capacity = TupList(self.instance.to_dict()['parameters']) \
        #     .to_dict(result_col="vehicle_capacity", is_list=False)

        return

    def check_max_unload(self, data):
        unload = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="unload").vapply(sum)
        # capacity = TupList(self.instance.to_dict()['parameters']) \
        #     .to_dict(result_col="vehicle_capacity", is_list=False)

        return

    def check_different_warehouse(self, data):
        warehouse = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="warehouse")
        return

    def check_load_duration(self, data):
        load_duration = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="load_dur").vapply(sum)
        load = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="load").vapply(sum)
        # load_pallet = TupList(self.instance.to_dict()['parameters']) \
        #     .to_dict(result_col="load_pallet", is_list=False)
        return

    def check_unload_duration(self, data):
        unload_duration = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="unload_dur").vapply(sum)
        unload = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="unload").vapply(sum)
        # unload_pallet = TupList(self.instance.to_dict()['parameters']) \
        #     .to_dict(result_col="unload_pallet", is_list=False)
        return

    def check_arrival_time(self, data):
        arrival_time = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="arr_time")  # s + 1
        departure_time = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="dep_time")
        trip_dur = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="trip_dur")  # s + 1 y [s, s+1]
        return

    def check_departure_time(self, data):
        departure_time = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="dep_time")
        arrival_time = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="arr_time")
        load_duration = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="load_dur").vapply(sum)
        unload_duration = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="unload_dur").vapply(sum)
        return

    def check_unload_time(self, data):
        unload_time = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="unload_time")
        arrival_time = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="arr_time")
        unload_duration = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="unload_dur").vapply(sum)
        return

    def check_no_simultaneity(self, data):
        actual_simultaneity = TupList(data). \
            to_dict(indices=["vehicle", "warehouse"], result_col=("arr_time", "dep_time"))
        return

    def check_correct_ho(self, data):
        actual_time_unload = TupList(data).\
            to_dict(indices=["comm_or", "comm_dest", "comm_comp"], result_col="unload_time")
        # expected_time_unload_opt = TupList(self.instance.to_dict()['parameters']).\
        #     to_dict(indices=["opt_time_limit"], is_list=False)
        return

    def check_correct_hr(self, data):
        actual_time_unload = TupList(data)\
            .to_dict(indices=["comm_or", "comm_dest", "comm_comp"], result_col="unload_time")
        # expected_time_unload_req = TupList(self.instance.to_dict()['parameters'])\
        #     .to_dict(result_col="req_time_limit", is_list=False)
        return

    def check_load_time_limit(self, data):
        load = TupList(data) \
            .to_dict(indices=["vehicle", "stop", "comm_comp"], result_col="load").vapply(sum)
        gamma = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="gamma")
        # capacity = TupList(self.instance.to_dict()['parameters']) \
        #     .to_dict(result_col="vehicle_capacity", is_list=False)
        return

    def check_unload_time_limit(self, data):
        unload = TupList(data) \
            .to_dict(indices=["vehicle", "stop", "comm_comp"], result_col="unload").vapply(sum)
        gamma = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="gamma")
        # capacity = TupList(self.instance.to_dict()['parameters']) \
        #     .to_dict(result_col="vehicle_capacity", is_list=False)
        return

    def check_solution(self, *args, **kwargs) -> dict:
        # Todo: create a method to check the solution.
        data = self.solution.to_dict()['data']
        print(data)
        return dict(
            c2_max_cap=self.check_max_cap(data),
            c3_load_req=self.check_load_req(data),
            c4y7_unload_req=self.check_required_pallets(data),
            c8_zero_unload_first_stop=self.check_zero_unload(data),
            c9_max_load=self.check_max_load(data),
            c10_max_unload=self.check_max_unload(data),
            c16_different_warehouse_for_stop=self.check_different_warehouse(data),
            c18_load_duration=self.check_load_duration(data),
            c19_unload_duration=self.check_unload_duration(data),
            c20_arrival_time=self.check_arrival_time(data),
            c21_departure_time=self.check_departure_time(data),
            c22_unload_time=self.check_unload_time(data),
            c23y24_no_simultaneity=self.check_no_simultaneity,
            c25_correct_ho=self.check_correct_ho(data),
            c26_correct_hr=self.check_correct_hr(data),
            c27_load_time_limit=self.check_load_time_limit,
            c28_unload_time_limit=self.check_unload_time_limit
        )

    def solve(self, options):
        raise NotImplementedError
