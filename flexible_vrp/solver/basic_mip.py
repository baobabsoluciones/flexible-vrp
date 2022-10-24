# Class to solve the problem with a basic mip.

from ..core import Experiment, Solution


class BasicMip(Experiment):
    def __init__(self, instance, solution=None):
        super().__init__(instance, solution)

    def solve(self, options):
        # Todo: replace this by the solve method

        self.solution = Solution({"data": "This solver is not implemented yet"})
        return {}
