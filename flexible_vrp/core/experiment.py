# Experiment is the class which is used to solve the problem.

# Imports from cornflow libraries
from cornflow_client import ExperimentCore, get_empty_schema

# Imports from internal modules
from .instance import Instance
from .solution import Solution


class Experiment(ExperimentCore):

    schema_checks = get_empty_schema()

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
        return {}

    def solve(self, options):
        raise NotImplementedError
