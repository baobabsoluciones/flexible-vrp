# Experiment is the class which is used to solve the problem.
import os

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

    def check_solution(self, *args, **kwargs) -> dict:
        # Todo: create a method to check the solution.
        # check compulsory pallets
        if compulsory==1:
            number_req_com = sum(model_instance.vUnloadQuantity[v, s, origin, destination, quantity, compulsory]
                           for v in model_instance.sVehicles for s in model_instance.sStops)
        # check optional pallets
        if compulsory==0:
            number_opt_com = sum(model_instance.vUnloadQuantity[v, s, origin, destination, quantity, compulsory]
                           for v in model_instance.sVehicles for s in model_instance.sStops)
        # check req_com_time_limit

        # check simultaneity
        # ls=[(v, v2, w) for v in model_instance.sVehicles for v2 in model_instance.sVehicles for w in model_instance.sWarehouses if v != v2 and |v va a w|
        #  if ln(ls)=0 |v2 va a w| y |solapan|]
        return {}

    def solve(self, options):
        raise NotImplementedError
