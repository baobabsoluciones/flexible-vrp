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
        #unload = TupList(data)
        #print(data)
        actual_unload = TupList(data).to_dict(indices=["comm_or", "comm_dest", "comm_comp"], result_col="unload").vapply(sum)
        expected_unload = TupList(self.instance.to_dict()['commodities'])\
            .to_dict(indices=["origin", "destination", "required"], result_col="quantity", is_list=False)

        #unload = TupList(v[""] for v in self.instance.data["unload"]).to_set()
        return [{"unload": n} for n in unload]

    # check simultaneity
    # ls=[(v, v2, w) for v in model_instance.sVehicles for v2 in model_instance.sVehicles for w in model_instance.sWarehouses if v != v2 and |v va a w|
    #  if ln(ls)=0 |v2 va a w| y |solapan|]

    def check_solution(self, *args, **kwargs) -> dict:
        # Todo: create a method to check the solution.
        data = self.solution.to_dict()['data']
        print(data)
        return dict(
            missing_required_pallets = self.check_required_pallets(data),
            # correct_Hr =
            # correct_Ho =
            # no_simultaneity =
        )

    def solve(self, options):
        raise NotImplementedError
