import os

from cornflow_client import ApplicationCore
from cornflow_client.core.tools import load_json


from .core import Experiment, Instance, Solution
from .solver.basic_mip import BasicMip
from .solver.heuristic import Heuristic

class FlexibleVRP(ApplicationCore):
    name = "flexible-vrp"
    instance = Instance
    solution = Solution
    solvers = dict(
        basic_mip=BasicMip,
        heuristic=Heuristic
    )
    schema = load_json(os.path.join(os.path.dirname(__file__), "./schemas/config.json"))

    def test_cases(self):
        return []
