# Class to solve the problem with a heuristic approach.
import pandas as pd

from flexible_vrp.core import Experiment, Solution
from flexible_vrp.solver.basic_mip_tools.create_model import create_model
from cornflow_client.constants import PYOMO_STOP_MAPPING
from heuristic_tools.create_solution import HeuristicSolution


class Heuristic(Experiment):
    def __init__(self, instance, solution=None):
        super().__init__(instance, solution)

    def solve(self):
        self.gen_sol()
        pass

    def gen_sol(self):
        self.prepare_data()
        pass

    def prepare_data(self, instance):
        pass

    def explore(self):
        # explore two future nodes and return dict{(v,n): (t,q)}
        return

    def select_move(self):
        # select (v, n)
        return

    def update(self):
        # update route selected
        return
