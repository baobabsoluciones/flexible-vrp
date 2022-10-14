# Imports from cornflow libraries
from cornflow_client import ExperimentCore

# Imports from internal modules
from .instance import Instance
from .solution import Solution


class Experiment(ExperimentCore):
    def __init__(self, instance: Instance, solution: Solution):
        super().__init__(instance, solution)
        if solution is None:
            self.solution = Solution(SuperDict())
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

        return 0

    def check_solution(self, *args, **kwargs) -> dict:
        return {}

    def solve(self, options):
        raise NotImplementedError
