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
        max_veh_cap_err = {(v, s): quantity[v, s] - veh_cap for (v, s) in quantity.keys() if quantity[v, s] > veh_cap}
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
        load_req_err = {c: expected_load[c + (1,)] - actual_load[c + (1,)] for c in compulsory_comm
                        if actual_load[c + (1,)] < expected_load[c + (1,)]}
        return load_req_err

    def check_unload_req(self, data):
        actual_unload = TupList(data)\
            .to_dict(indices=["comm_or", "comm_dest", "comm_comp"], result_col="unload").vapply(sum)
        expected_unload = TupList(self.instance.to_dict()['commodities'])\
            .to_dict(indices=["origin", "destination", "required"], result_col="quantity", is_list=False)
        compulsory_comm = list(set([(c[0], c[1]) for c in expected_unload.keys() if c[2] == 1]))
        unload_req_err = {c: expected_unload[c + (1,)] - actual_unload[c + (1,)] for c in compulsory_comm
                          if actual_unload[c + (1,)] < expected_unload[c + (1,)]}
        return unload_req_err

    def check_load(self, data):
        actual_load = TupList(data)\
            .to_dict(indices=["comm_or", "comm_dest", "comm_comp"], result_col="load").vapply(sum)
        expected_load = TupList(self.instance.to_dict()['commodities'])\
            .to_dict(indices=["origin", "destination", "required"], result_col="quantity", is_list=False)

        comm_with_actual_load = [c for c in actual_load.keys() if actual_load[c] > 0]

        load_excess_err = {c: - expected_load[c] + actual_load[c] for c in comm_with_actual_load
                           if actual_load[c] > expected_load[c]}
        return load_excess_err

    def check_zero_unload(self, data):
        zero_unload = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="unload").vapply(sum)
        vehicle = list(set([(v[0]) for v in zero_unload.keys()]))
        stop = list(set([(i[1]) for i in zero_unload.keys() if i[1] == 0]))
        zero_unload_err = {(v, s): zero_unload[v, s] for v in vehicle for s in stop if zero_unload[v, s] > 0}
        return zero_unload_err

    def check_max_load(self, data):
        load = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="load").vapply(sum)
        veh_cap = self.instance.data["parameters"]["vehicle_capacity"]
        max_load_err = {(v, s): load[v, s] - veh_cap for (v, s) in load.keys() if load[v, s] > veh_cap}
        return max_load_err

    def check_max_unload(self, data):
        unload = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="unload").vapply(sum)
        veh_cap = self.instance.data["parameters"]["vehicle_capacity"]
        max_unload_err = {(v, s): unload[v, s] - veh_cap for (v, s) in unload.keys() if unload[v, s] > veh_cap}
        return max_unload_err

    def check_different_warehouse(self, data):
        dict_warehouse = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="warehouse")
        warehouse = {}
        for key, value in dict_warehouse.items():
            warehouse[key] = value[0]
        vehicle = list(set([(v[0]) for v in dict_warehouse.keys()]))
        stop = list(set([(i[1]) for i in dict_warehouse.keys() if i[1] != 0]))
        warehouse_err = {(v, s): warehouse[v, s] for v in vehicle for s in stop
                         if ((v, s) in dict_warehouse.keys()
                         and warehouse[v, s] == warehouse[v, s - 1])}
        return warehouse_err

    def check_load_duration(self, data):
        dict_load_duration = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="load_dur")
        load_duration = {}
        for key, value in dict_load_duration.items():
            load_duration[key] = value[0]
        load = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="load").vapply(sum)
        load_time_pallet = self.instance.data["parameters"]["load_pallet"]
        load_duration_err = {(v, s): load_duration[v, s] - load[v, s] * load_time_pallet
                             for (v, s) in load_duration.keys()
                             if ((load_duration[v, s] < 0.99 * load[v, s] * load_time_pallet) or
                                 (load_duration[v, s] > 1.01 * load[v, s] * load_time_pallet))}
        return load_duration_err

    def check_unload_duration(self, data):
        dict_unload_duration = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="unload_dur")
        unload = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="unload").vapply(sum)
        unload_duration = {}
        for key, value in dict_unload_duration.items():
            unload_duration[key] = value[0]
        unload_time_pallet = self.instance.data["parameters"]["unload_pallet"]
        unload_duration_err = {(v, s): unload_duration[v, s] - unload[v, s] * unload_time_pallet
                               for (v, s) in unload_duration.keys()
                               if ((unload_duration[v, s] < 0.99 * unload[v, s] * unload_time_pallet) or
                                   (unload_duration[v, s] > 1.01 * unload[v, s] * unload_time_pallet))}
        return unload_duration_err

    def check_arrival_time(self, data):
        dict_arrival_time = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="arr_time")  # s + 1
        arrival_time = {}
        for key, value in dict_arrival_time.items():
            arrival_time[key] = value[0]
        dict_departure_time = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="dep_time")
        departure_time = {}
        for key, value in dict_departure_time.items():
            departure_time[key] = value[0]
        dict_trip_dur = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="trip_dur")  # s + 1 y [s, s+1]
        trip_dur = {}
        for key, value in dict_trip_dur.items():
            trip_dur[key] = value[0]
        vehicle = list(set([(v[0]) for v in departure_time.keys()]))
        stop = list(set([(i[1]) for i in departure_time.keys() if i[1] != 0]))
        arrival_time_err = {(v, s-1): (arrival_time[v, s] - trip_dur[v, s-1] - departure_time[v, s-1])
                            for v in vehicle for s in stop
                            if ((v, s) in arrival_time.keys() and (v, s) in departure_time.keys() and
                                (v, s) in trip_dur.keys() and
                                (arrival_time[v, s] < 0.99 * (trip_dur[v, s-1] + departure_time[v, s-1])) or
                                (arrival_time[v, s] > 1.01 * (trip_dur[v, s-1] + departure_time[v, s-1])))}
        return arrival_time_err

    def check_departure_time(self, data):
        dict_departure_time = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="dep_time")
        departure_time = {}
        for key, value in dict_departure_time.items():
            departure_time[key] = value[0]
        dict_arrival_time = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="arr_time")
        arrival_time = {}
        for key, value in dict_arrival_time.items():
            arrival_time[key] = value[0]
        dict_load_duration = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="load_dur")
        load_duration = {}
        for key, value in dict_load_duration.items():
            load_duration[key] = value[0]
        dict_unload_duration = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="unload_dur")
        unload_duration = {}
        for key, value in dict_unload_duration.items():
            unload_duration[key] = value[0]
        dep_time_err = {(v, s): (departure_time[v, s] - arrival_time[v, s]
                                 - load_duration[v, s] - unload_duration[v, s])
                        for (v, s) in departure_time.keys()
                        if ((departure_time[v, s] <
                             0.99 * (arrival_time[v, s] + load_duration[v, s] + unload_duration[v, s])) or
                            (departure_time[v, s] > 1.01 * (arrival_time[v, s] + load_duration[v, s] +
                            unload_duration[v, s])))}
        return dep_time_err

    def check_unload_time(self, data):
        unload_time = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="unload_time")
        arrival_time = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="arr_time")
        unload_duration = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="unload_dur")
        unload_time_err = {(v, s): (unload_time[v, s] - arrival_time[v, s] - unload_duration[v, s])
                           for (v, s) in unload_time.keys()
                           if ((unload_time[v, s] < (arrival_time[v, s] + unload_duration[v, s]) * 0.99) or
                               (unload_time[v, s] > (arrival_time[v, s] + unload_duration[v, s]) * 1.01))}
        return unload_time_err

    def check_no_simultaneity(self, data):
        arrival_time = TupList(data) \
            .to_dict(indices=["vehicle", "warehouse"], result_col="arr_time")
        arrival_time2 = TupList(data) \
            .to_dict(indices=["vehicle", "warehouse"], result_col="arr_time")
        departure_time = TupList(data) \
            .to_dict(indices=["vehicle", "warehouse"], result_col="dep_time")
        departure_time2 = TupList(data) \
            .to_dict(indices=["vehicle", "warehouse"], result_col="dep_time")
        simultaneity_err = {(v, v2, w): 1
                            for (v, w) in arrival_time.keys()
                            for (v2, w2) in arrival_time2.keys()
                            if (v != v2 and w == w2 and ((arrival_time2[v2, w2] >= 0.99 * departure_time[v, w]) ==
                                                         (arrival_time[v, w] >= 0.99 * departure_time2[v2, w2])))}
        return simultaneity_err

    def check_correct_ho(self, data):
        actual_time_unload = TupList(data).\
            to_dict(indices=["comm_or", "comm_dest", "comm_comp"], result_col="unload_time")
        opt_time_limit = self.instance.data["parameters"]["opt_time_limit"]
        comm = list(set([(c[0], c[1]) for c in actual_time_unload.keys()]))
        ho_err = {c: actual_time_unload[c + (1,)] - opt_time_limit for c in comm
                  if actual_time_unload[c + (1,)] > opt_time_limit}
        return ho_err

    def check_correct_hr(self, data):
        actual_time_unload = TupList(data)\
            .to_dict(indices=["comm_or", "comm_dest", "comm_comp"], result_col="unload_time")
        req_time_limit = self.instance.data["parameters"]["req_time_limit"]
        compulsory_comm = list(set([(c[0], c[1]) for c in actual_time_unload.keys() if c[2] == 1]))
        hr_err = {c: actual_time_unload[c + (1,)] - req_time_limit for c in compulsory_comm
                  if actual_time_unload[c + (1,)] > req_time_limit}
        return hr_err

    def check_load_time_limit(self, data):
        load = TupList(data) \
            .to_dict(indices=["vehicle", "stop", "comm_or", "comm_dest", "comm_comp"], result_col="load").vapply(sum)
        gamma = TupList(data) \
            .to_dict(indices=["vehicle", "stop"], result_col="gamma")
        veh_cap = self.instance.data["parameters"]["vehicle_capacity"]
        vehicle = list(set([(v[0]) for v in load.keys()]))
        stop = list(set([(i[1]) for i in load.keys()]))
        compulsory_comm = list(set([(c[2], c[3]) for c in load.keys() if c[4] == 1]))
        load_time_limit_err = {(v, s, c): load[(v, s) + c + (1,)] - (1 - gamma[v, s]) * veh_cap for c in compulsory_comm
                               for v in vehicle for s in stop if load[(v, s) + c + (1,)] > (1 - gamma[v, s]) * veh_cap}
        return load_time_limit_err

    def check_unload_time_limit(self, data):
        unload = TupList(data) \
            .to_dict(indices=["vehicle", "stop", "comm_or", "comm_dest", "comm_comp"], result_col="unload").vapply(sum)
        gamma = TupList(data)\
            .to_dict(indices=["vehicle", "stop"], result_col="gamma")
        veh_cap = self.instance.data["parameters"]["vehicle_capacity"]
        vehicle = list(set([(v[0]) for v in unload.keys()]))
        stop = list(set([(i[1]) for i in unload.keys()]))
        compulsory_comm = list(set([(c[2], c[3]) for c in unload.keys() if c[4] == 1]))
        unload_time_limit_err = {(v, s, c): unload[(v, s) + c + (1,)] - (1 - gamma[v, s]) * veh_cap
                                 for c in compulsory_comm for v in vehicle for s in stop
                                 if unload[(v, s) + c + (1,)] > (1 - gamma[v, s]) * veh_cap}
        return unload_time_limit_err

    def check_solution(self, *args, **kwargs) -> dict:
        # Todo: create a method to check the solution.
        data = self.solution.to_dict()['data']
        print(data)
        return dict(
            # c2_max_cap=self.check_max_cap(data),
            # c3_load_req=self.check_load_req(data),
            # c4_unload_req=self.check_unload_req(data),
            # c7_load_total=self.check_load(data),
            # c8_zero_unload_first_stop=self.check_zero_unload(data),
            # c9_max_load=self.check_max_load(data),
            # c10_max_unload=self.check_max_unload(data),
            # c16_different_warehouse_for_stop=self.check_different_warehouse(data),
            # c18_load_duration=self.check_load_duration(data),
            # c19_unload_duration=self.check_unload_duration(data),
            # # c20_arrival_time=self.check_arrival_time(data), # error al leer trip_duration
            # c21_departure_time=self.check_departure_time(data),
            # c22_unload_time=self.check_unload_time(data),
            # c23y24_no_simultaneity=self.check_no_simultaneity(data),
            # c25_correct_ho=self.check_correct_ho(data),
            # c26_correct_hr=self.check_correct_hr(data),
            # c27_load_time_limit=self.check_load_time_limit(data),
            # c28_unload_time_limit=self.check_unload_time_limit(data)
        )

    def solve(self, options):
        raise NotImplementedError
