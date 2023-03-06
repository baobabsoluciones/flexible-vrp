# Class to solve the problem with a heuristic approach.
import random

from timeit import default_timer as timer
from flexible_vrp.core import Experiment, Solution


class Heuristic(Experiment):
    def __init__(self, instance, solution=None):
        super().__init__(instance, solution)

    def prepare_data(self):
        origins = set([c["location1"] for c in self.instance.data["trip_durations"]])
        destinations = set([c["location2"] for c in self.instance.data["trip_durations"]])
        # Getting a list from the union of destinations and origins
        self.warehouses = list(origins.union(destinations))
        self.vehicles = [v for v in range(int(self.instance.data["parameters"]["fleet_size"]))]
        self.trip_duration = {(x["location1"], x["location2"]): x["time"] for x in self.instance.data["trip_durations"]}
        self.comm_req = {(c["origin"], c["destination"]): c["quantity"]
                         for c in self.instance.data["commodities"] if c["required"]}
        self.comm_opt = {(c["origin"], c["destination"]): c["quantity"]
                         for c in self.instance.data["commodities"] if not c["required"]}
        self.comm_req_loaded = {(c["origin"], c["destination"]): 0
                                for c in self.instance.data["commodities"] if c["required"]}
        self.comm_opt_loaded = {(c["origin"], c["destination"]): 0
                                for c in self.instance.data["commodities"] if not c["required"]}
        self.current_warehouse = dict()
        self.veh_cap = self.instance.data["parameters"]["vehicle_capacity"]
        self.load_time = self.instance.data["parameters"]["load_pallet"]
        self.unload_time = self.instance.data["parameters"]["unload_pallet"]
        self.req_time_limit = self.instance.data["parameters"]["req_time_limit"]
        self.opt_time_limit = self.instance.data["parameters"]["opt_time_limit"]

    def solve(self, options):
        self.prepare_data()
        t_init = timer()  # guarda en t_init en tiempo actual
        best_sol = dict()
        time = timer() - t_init
        time_limit = options["solver_config"]["TimeLimit"]
        while time <= time_limit:  # comprobamos que tiempo_actual - t_init <= time_limit
            current_sol = self.gen_sol()
            if current_sol["obj"] < best_sol["obj"]:
                best_sol = current_sol
        return 1

    def gen_sol(self):
        elegible_warehouses = [w for w in self.warehouses if any([(w, w2) for w2 in self.warehouses if
                                                                  (w, w2) in self.comm_req.keys()])]
        self.current_warehouse = {v: random.choice(elegible_warehouses) for v in self.vehicles}
        self.sol = {(v, self.current_warehouse[v]): (0, 0) for v in self.vehicles
                    }
        stop = False
        while not stop:
            self.explore()
            self.select_move()
            self.update()
            # stop = self.check_if_stop()
        return self.sol

    def check_if_stop(self):
        # com_req_delivered = sum(self.comm_req[i] for i in self.warehouses.keys()) == 0
        time_limit_over = all([v for v in self.vehicles if v.current_time[v] > self.time_limit])
        return time_limit_over

    def explore(self, w2=None):
        self.t = 0
        self.tree = {(v, w2, w3): (self.comm_req[self.current_warehouse[v], w2] + self.comm_req[w2, w3], self.t)
                     for v in self.vehicles for w2 in self.warehouses for w3 in self.warehouses
                     if (w2 != self.current_warehouse[v]
                         and (self.current_warehouse[v], w2) in self.comm_req.keys()
                         and w3 != w2
                         and (w2, w3) in self.comm_req.keys()
                         and self.comm_req[w2, w3] > 0)
        }
        for v in self.vehicles:
            for w2 in self.warehouses:
                a = 0
                for w3 in self.warehouses:
                    if (v, w2, w3) in self.tree.keys():
                        a += 1
                if (a == 0
                        and w2 != self.current_warehouse[v]
                        and (self.current_warehouse[v], w2) in self.comm_req.keys()
                        and self.comm_req[self.current_warehouse[v], w2] > 0):
                    self.tree[(v, w2)] = (self.comm_req[self.current_warehouse[v], w2], self.t)
        return self.tree

    def select_move(self):
        # k = max(valor[0] for valor in self.tree.values())
        max_valor = None
        for clave, valor in self.tree.items():
            if max_valor is None or valor[0] > max_valor:
                max_valor = valor[0]
        self.move = random.choice([clave for clave, valor in self.tree.items() if valor[0] == max_valor])[:2]
        return self.move

    def update(self):
        # update route selected
        v = self.move[0]
        cant = self.comm_req[(self.current_warehouse[v], self.move[1])]
        q = min(cant, 22)
        self.comm_req[(self.current_warehouse[v], self.move[1])] -= q
        self.comm_req_loaded[(self.current_warehouse[v], self.move[1])] += q
        self.sol[self.move] = (q, self.t)  #for q in c[quantity] (leer c[origin] y c[destination])
        self.current_warehouse[v] = self.move[1]
        return self.sol
