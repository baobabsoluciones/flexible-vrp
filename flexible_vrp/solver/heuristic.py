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
        self.veh_cap = self.instance.data["parameters"]["vehicle_capacity"]
        self.load_time = self.instance.data["parameters"]["load_pallet"]
        self.unload_time = self.instance.data["parameters"]["unload_pallet"]
        self.req_time_limit = self.instance.data["parameters"]["req_time_limit"]
        self.opt_time_limit = self.instance.data["parameters"]["opt_time_limit"]
        self.average_time_d = self.instance.data["parameters"]["average_time_d"]

    def solve(self, options):
        self.prepare_data()
        t_init = timer()  # guarda en t_init en tiempo actual
        best_sol = dict()
        time = timer() - t_init
        # self.time_limit es el tiempo máx de simulación
        self.time_limit = options["solver_config"]["TimeLimit"]
        while time <= self.time_limit:  # comprobamos que tiempo_actual - t_init <= time_limit
            current_sol = self.gen_sol()
            if current_sol["obj"] < best_sol["obj"]:
                best_sol = current_sol
        return 1

    def gen_sol(self):
        self.comm_req = {(w1, w2): 0 for w1 in self.warehouses for w2 in self.warehouses if w1 != w2}
        for c in [c for c in self.instance.data["commodities"] if c['required']]:
            self.comm_req[(c["origin"], c["destination"])] = c["quantity"]
        # for c in self.instance.data["commodities"]:
        #     if c["required"]:
        #         self.comm_req[(c["origin"], c["destination"])] = c["quantity"]
        self.comm_opt = {(c["origin"], c["destination"]): c["quantity"]
                         for c in self.instance.data["commodities"] if not c["required"]}
        self.comm_req_loaded = {(c["origin"], c["destination"]): 0
                                for c in self.instance.data["commodities"] if c["required"]}
        self.comm_opt_loaded = {(c["origin"], c["destination"]): 0
                                for c in self.instance.data["commodities"] if not c["required"]}
        possible_warehouses = [w for w in self.warehouses if any([(w, w2) for w2 in self.warehouses if
                                                                  (w, w2) in self.comm_req.keys()])]
        self.current_warehouse = {v: random.choice(possible_warehouses) for v in self.vehicles}
        self.current_time = {v: 0 for v in self.vehicles}  # "t" + str(v)
        self.stops = {v: 0 for v in self.vehicles}
        self.sol = {(v, self.current_warehouse[v], self.stops[v]): (0, self.current_time[v]) for v in self.vehicles}
        stop = False
        while not stop:
            self.explore()
            self.select_move()
            self.update()
            stop = self.check_if_stop()
        return self.sol

    def check_if_stop(self):
        time_limit_over = [v for v in self.vehicles if self.current_time[v] > self.req_time_limit]
        stop = 0
        if self.comm_req.values() == 0:
            stop = 1
        if len(time_limit_over) == len(self.vehicles):
            stop = 1
        for i in time_limit_over:
            if i in self.vehicles:
                self.vehicles.remove(i)
        return stop

    def explore(self, w2=None):
        # carga + viaje + descarga + carga + viaje + descarga
        self.tree = {(v, w2, w3): (self.comm_req[self.current_warehouse[v], w2] + self.comm_req[w2, w3],
                                   (self.comm_req[self.current_warehouse[v], w2] * self.load_time +
                                   self.trip_duration[self.current_warehouse[v], w2] +
                                   self.comm_req[self.current_warehouse[v], w2] * self.unload_time +
                                   self.comm_req[w2, w3] * self.load_time +
                                   self.trip_duration[self.current_warehouse[v], w2] +
                                   self.comm_req[w2, w3] * self.unload_time))
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
                    self.tree[(v, w2)] = (self.comm_req[self.current_warehouse[v], w2],
                                          (self.comm_req[self.current_warehouse[v], w2] * self.load_time +
                                           self.trip_duration[self.current_warehouse[v], w2] +
                                           self.comm_req[self.current_warehouse[v], w2] * self.unload_time
                                           ))
        # self.tree.update({(v, w2): (self.comm_req[self.current_warehouse[v], w2],
        #                             (self.comm_req[self.current_warehouse[v], w2] * self.load_time +
        #                              self.trip_duration[self.current_warehouse[v], w2] +
        #                              self.comm_req[self.current_warehouse[v], w2] * self.unload_time))
        #                   for v in self.vehicles
        #                   for w2 in self.warehouses
        #                   if (w2 != self.current_warehouse[v]
        #                       and (self.current_warehouse[v], w2) in self.comm_req.keys()
        #                       and any((v, w2, w3) in self.tree for w3 in self.warehouses)
        #                       or (self.comm_req[w2, w3] > 0
        #                           and (self.current_warehouse[v], w2) in self.comm_req.keys()
        #                           and w3 != w2
        #                           and (w2, w3) in self.comm_req.keys()))
        #                   })
        return self.tree

    def select_move(self):
        # attractive
        k = self.veh_cap * (self.load_time + self.unload_time) * 2
        alpha = 1/(self.veh_cap * 2)
        beta = self.average_time_d * 2 + k
        # Diccionario que recoge el atractivo de cada movimiento
        dict_attractive = {clave: valor[0] * alpha + beta / valor[1] for clave, valor in self.tree.items()}
        dict_sorted_attractive = {clave: valor for clave, valor in sorted(dict_attractive.items(),
                                                                          key=lambda item: item[1], reverse=True)}
        # Progresión geométrica para asignar probabilidades
        n = len(self.tree)
        # Todo: estimar r y ¿definirlo en excel?
        r = 0.5
        a1 = (r - 1) / ((r**n) - 1)
        formula_an = lambda x: a1 * (r**(x - 1))
        list_probabilities = [a1 if i == 0 else formula_an(i) for i in range(1, n+1)]
        self.move = random.choices(list(dict_sorted_attractive.keys()), list_probabilities)[0]
        return self.move

    def update(self):
        v = self.move[0]
        w = self.current_warehouse[v]
        w2 = self.move[1]
        cant = self.comm_req[w, w2]
        q = min(cant, self.veh_cap)
        t = (q * self.load_time + self.trip_duration[w, w2] + q * self.unload_time)
        # update route selected
        self.comm_req[w, w2] -= q
        if (q!=0):
            self.comm_req_loaded[w, w2] += q
        # self.comm_req_loaded[w, w2] += q if q != 0 else None
        self.current_time[v] += t
        self.stops[v] += 1
        self.sol[v, w2, self.stops[v]] = (q, t)
        self.current_warehouse[v] = w2
        return self.sol
