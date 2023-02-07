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

    def check_required_pallets(self, data):
        actual_unload = TupList(data).\
            to_dict(indices=["comm_or", "comm_dest", "comm_comp"], result_col="unload").vapply(sum)
        expected_unload = TupList(self.instance.to_dict()['commodities'])\
            .to_dict(indices=["origin", "destination", "required"], result_col="quantity", is_list=False)
        return

    def check_correct_hr(self, data):
        actual_time_unload = TupList(data).\
            to_dict(indices=["comm_or", "comm_dest", "comm_comp"], result_col="unload_time")
        expected_time_unload_req = TupList(self.instance.to_dict()['parameters']).\
            to_dict(indices=["req_time_limit"], is_list=False)
        return

    def check_correct_ho(self, data):
        actual_time_unload = TupList(data).\
            to_dict(indices=["comm_or", "comm_dest", "comm_comp"], result_col="unload_time")
        expected_time_unload_opt = TupList(self.instance.to_dict()['parameters']).\
            to_dict(indices=["opt_time_limit"], is_list=False)
        return

    def check_no_simultaneity(self, data):
        actual_simultaneity = TupList(data).\
            to_dict(indices=["vehicle", "warehouse"], result_col=("arr_time", "dep_time"))
        return

    # check simultaneity
    # ls=[(v, v2, w) for v in model_instance.sVehicles for v2 in model_instance.sVehicles
    # for w in model_instance.sWarehouses if v != v2 and |v va a w|
    #  if ln(ls)=0 |v2 va a w| y |solapa|]

    def check_solution(self, *args, **kwargs) -> dict:
        # Todo: create a method to check the solution.
        data = self.solution.to_dict()['data']
        print(data)
        return dict(
            missing_required_pallets=self.check_required_pallets(data),
            correct_hr=self.check_correct_hr(data),
            correct_ho=self.check_correct_ho(data),
            no_simultaneity=self.check_no_simultaneity
        )

    def solve(self, options):
        raise NotImplementedError
