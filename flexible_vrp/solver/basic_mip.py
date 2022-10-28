# Class to solve the problem with a basic mip.

from ..core import Experiment, Solution
from .basic_mip_tools.create_model import create_model

class BasicMip(Experiment):
    def __init__(self, instance, solution=None):
        super().__init__(instance, solution)

    def solve(self, options):
        if not self.instance.to_dict():
            raise ValueError("The instance is empty")
        # Todo: replace this by the solve method
        model = create_model()
        self.solution = Solution({"data": "This solver is not implemented yet"})
        return {}
