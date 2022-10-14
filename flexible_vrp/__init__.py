from cornflow_client import ApplicationCore
from cornflow_client.core.tools import load_json


from .core import Experiment, Instance, Solution


class FlexibleVRP(ApplicationCore):
    name = "flexible-vrp"
    instance = Instance
    solution = Solution
    solvers = dict()
    schema = load_json(os.path.join(os.path.dirname(__file__), "./schemas/config.json"))

    def test_cases(self):
        return []
