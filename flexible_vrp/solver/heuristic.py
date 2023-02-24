# Class to solve the problem with a heuristic approach.
import random

from flexible_vrp.core import Experiment, Solution
from random import *

class Heuristic(Experiment):
    def __init__(self, instance, solution=None):
        super().__init__(instance, solution)


    def prepare_data(self):
        origins = set([c["location1"] for c in self.instance.data["trip_durations"]])
        destinations = set(
            [c["location2"] for c in self.instance.data["trip_durations"]]
        )
        # Getting a list from the union of destinations and origins
        self.warehouses = list(origins.union(destinations))
        self.vehicles = [v for v in range(int(self.instance.data["parameters"]["fleet_size"]))]
        self.trip_duration = {(x["location1"], x["location2"]): x["time"] for x in self.instance.data["trip_durations"]}
        self.comm_req = {(c["origin"], c["destination"]): c["quantity"] for c in self.instance.data["commodities"] if c["required"]}
        self.comm_opt = {(c["origin"], c["destination"]): c["quantity"] for c in self.instance.data["commodities"] if not c["required"]}
        self.comm_req_loaded = {(c["origin"], c["destination"]): 0 for c in self.instance.data["commodities"] if c["required"]}
        self.comm_opt_loaded = {(c["origin"], c["destination"]): 0 for c in self.instance.data["commodities"] if not c["required"]}


        self.current_warehouse = dict()

    def solve(self):
        self.prepare_data()
        # t_init = 0# guardar en t_init en tiempo actual
        # best_sol = dict()
        # while tiempo_no_superado: # comprobamos que tiempo actual - t_init <= time_limit
        #     current_sol = self.gen_sol()
        #     if current_sol["obj"] < best_sol["obj"]:
        #         best_sol = current_sol
        return 1

    def gen_sol(self):
        self.current_warehouse = {v: random.choice(self.warehouses) for v in self.vehicles}
        self.explore()
        self.select_move()
        sol = dict()
        return sol


    def explore(self):
        tree = {(v, w): random.random() for v in self.vehicles for w in self.warehouses if w != self.current_warehouse[v]}
        return tree


    def select_move(self):
        # select (v, n)
        pass

    def update(self):
        # update route selected
        pass
