# Class to solve the problem with a heuristic approach.
import random

from timeit import default_timer as timer
from flexible_vrp.core import Experiment, Solution


class Heuristic(Experiment):
    def __init__(self, instance, solution=None):
        super().__init__(instance, solution)

    def prepare_data(self):
        destinations = set([c["destination"] for c in self.instance.data["commodities"]])
        self.origins = set([c["origin"] for c in self.instance.data["commodities"]])
        # Getting a list from the union of destinations and origins
        self.warehouses = list(self.origins.union(destinations))
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
        best_sol = dict()
        # Timer to search the best solution
        t_init = timer()
        time = timer() - t_init
        self.time_limit = options["solver_config"]["TimeLimit"]
        while time <= self.time_limit:
            current_sol = self.gen_sol()
            if current_sol["obj"] < best_sol["obj"]:
                best_sol = current_sol
        return 1

    def gen_sol(self):
        # Generate dicts to store the number of commodities
        self.comm_req = {(w1, w2): 0 for w1 in self.warehouses for w2 in self.warehouses if w1 != w2}
        for c in [c for c in self.instance.data["commodities"] if c['required']]:
            self.comm_req[(c["origin"], c["destination"])] = c["quantity"]
        self.comm_opt = {(c["origin"], c["destination"]): c["quantity"]
                         for c in self.instance.data["commodities"] if not c["required"]}
        self.comm_req_loaded = {(c["origin"], c["destination"]): 0
                                for c in self.instance.data["commodities"] if c["required"]}
        self.comm_opt_loaded = {(c["origin"], c["destination"]): 0
                                for c in self.instance.data["commodities"] if not c["required"]}
        # Other dicts
        possible_warehouses = [w for w in self.origins if any([(w, w2) for w2 in self.warehouses
                                                               if (w, w2) in self.comm_req_loaded.keys()])]
        self.current_warehouse = {v: random.choice(possible_warehouses) for v in self.vehicles}
        self.current_time = {v: 0 for v in self.vehicles}  # "t" + str(v)
        self.stops = {v: 0 for v in self.vehicles}
        self.dict_occupation = {v: [] for v in self.warehouses}
        self.sol = {(v, self.current_warehouse[v], self.stops[v]): (0, self.current_time[v]) for v in self.vehicles}
        stop = False
        while not stop:
            self.explore()
            self.select_move()
            self.update()
            stop = self.check_if_stop()
        return self.sol

    def check_if_stop(self):
        # Parada (stop = 1) si no quedan comm_req que entregar o si todos los vehículos superan el límite horario
        # todo: parar si no quedan commodities opcionales
        # lista de vehículos que ha superado el tiempo límite
        list_veh_time_over = [v for v in self.vehicles if self.current_time[v] > self.req_time_limit]
        stop = 0
        if all(valor == 0 for valor in self.comm_req.values()):
            stop = 1
        if len(list_veh_time_over) == len(self.vehicles):
            stop = 1
        self.vehicles = [v for v in self.vehicles if v not in list_veh_time_over]  # remove v de self.vehicles
        return stop

    def explore(self, w2=None):
        # Exploración a 3 saltos vista
        self.tree = {(v, w2, w3): (min(self.veh_cap, self.comm_req[self.current_warehouse[v], w2])
                                   + min(self.veh_cap, self.comm_req[w2, w3])
                                   + min(self.veh_cap - max(self.comm_req[self.current_warehouse[v], w2],
                                                            self.comm_req[w2, w3]),
                                         self.comm_req[self.current_warehouse[v], w3]),
                                   (self.comm_req[self.current_warehouse[v], w2] * self.load_time +
                                    self.trip_duration[self.current_warehouse[v], w2] +
                                    self.comm_req[self.current_warehouse[v], w2] * self.unload_time +
                                    self.comm_req[w2, w3] * self.load_time +
                                    self.trip_duration[self.current_warehouse[v], w2] +
                                    self.comm_req[w2, w3] * self.unload_time +
                                    self.comm_req[self.current_warehouse[v], w3] * self.load_time +
                                    self.comm_req[self.current_warehouse[v], w3] * self.unload_time))
                     for v in self.vehicles for w2 in self.warehouses for w3 in self.warehouses
                     if ((self.current_warehouse[v], w3) in self.comm_req.keys()
                         and w2 != self.current_warehouse[v]
                         and (self.current_warehouse[v], w2) in self.comm_req.keys()
                         and w3 != w2
                         and self.comm_req[w2, w3] > 0
                         and max(self.comm_req[self.current_warehouse[v], w2], self.comm_req[w2, w3]) < self.veh_cap)
                     }
        # Exploración a 2 saltos vista
        # Valor de self.tree = (Comm_req no entregados a 2 saltos vista, tiempo (carga + viaje + descarga)x2)
        self.tree.update({(v, w2, w3): ((min(self.veh_cap, self.comm_req[self.current_warehouse[v], w2]) +
                                         min(self.veh_cap, self.comm_req[w2, w3]),
                                         (self.comm_req[self.current_warehouse[v], w2] * self.load_time +
                                          self.trip_duration[self.current_warehouse[v], w2] +
                                          self.comm_req[self.current_warehouse[v], w2] * self.unload_time +
                                          self.comm_req[w2, w3] * self.load_time +
                                          self.trip_duration[self.current_warehouse[v], w2] +
                                          self.comm_req[w2, w3] * self.unload_time)))
                          for v in self.vehicles for w2 in self.warehouses for w3 in self.warehouses
                          if (not((v, w2, w3) in self.tree.keys())
                              and w2 != self.current_warehouse[v]
                              and (self.current_warehouse[v], w2) in self.comm_req.keys()
                              and w3 != w2
                              and self.comm_req[w2, w3] > 0)
                     })

        # Exploración a 1 salto vista
        self.tree.update({(v, w2): (min(self.veh_cap, self.comm_req[self.current_warehouse[v], w2]),
                                    (self.comm_req[self.current_warehouse[v], w2] * self.load_time +
                                     self.trip_duration[self.current_warehouse[v], w2] +
                                     self.comm_req[self.current_warehouse[v], w2] * self.unload_time))
                          for v in self.vehicles
                          for w2 in self.warehouses
                          for w3 in self.warehouses
                          if (w2 != self.current_warehouse[v]
                              and (self.current_warehouse[v], w2) in self.comm_req.keys()
                              and not any((v, w2, w3) in self.tree.keys() for w3 in self.warehouses)
                              and self.comm_req[self.current_warehouse[v], w2] > 0
                              and (self.current_warehouse[v], w2) in self.comm_req.keys()
                              and w3 != w2
                              and (w2, w3) in self.comm_req.keys())
                          })
        return self.tree

    def select_move(self):
        # attractive
        k = self.veh_cap * (self.load_time + self.unload_time) * 2
        alpha = 1/(self.veh_cap * 2)
        beta = self.average_time_d * 2 + k
        # dict_attractive: diccionario que recoge el atractivo de cada movimiento
        dict_attractive = {clave: valor[0] * alpha + beta / valor[1] for clave, valor in self.tree.items()}
        dict_sorted_attractive = {clave: valor for clave, valor in sorted(dict_attractive.items(),
                                                                          key=lambda item: item[1], reverse=True)}
        # Progresión geométrica para asignar probabilidades
        n = len(self.tree)  # n: número de términos de la progresión
        # Todo: estimar r y ¿definirlo en excel?
        r = 0.5  # r: razón
        a1 = (r - 1) / ((r**n) - 1)  # a1: primer término de la progresión, siendo la suma Sn = 1
        formula_an = lambda x: a1 * (r**(x - 1))  # an: probabilidad asignada a cada término
        list_probabilities = [a1 if i == 0 else formula_an(i) for i in range(1, n+1)]  # lista [a1,a2,...,an]
        # move selected
        self.move = random.choices(list(dict_sorted_attractive.keys()), list_probabilities)[0]
        return self.move

    def update(self):
        v = self.move[0]
        w = self.current_warehouse[v]
        w2 = self.move[1]
        cant = self.comm_req[w, w2]
        q = min(cant, self.veh_cap)
        t = (q * self.load_time + self.trip_duration[w, w2] + q * self.unload_time)  # todo: tiempo holgura
        # SIMULTANEITY VEH
        # Ventanas temporales del movimiento elegido para origen y destino
        selected_interval_o = [self.current_time[v], self.current_time[v] + q * self.load_time]
        selected_interval_d = [self.current_time[v] + q * self.load_time + self.trip_duration[w, w2],
                               self.current_time[v] + t]
        # Comprobación de intersección entre los
        busy = False
        busy = any((interval[0] < selected_interval_o[0] < interval[1] or selected_interval_o[0] < interval[0] <
                    selected_interval_o[1])
                   for interval in self.dict_occupation[w]) or \
               any((interval[0] < selected_interval_d[0] < interval[1] or selected_interval_d[0] < interval[0] <
                    selected_interval_d[1])
                   for interval in self.dict_occupation[w2])
        if not busy:
            # Update warehouse occupation time
            self.dict_occupation[w].append([self.current_time[v], self.current_time[v] + q * self.load_time])
            self.dict_occupation[w2].append([self.current_time[v] + q * self.load_time + self.trip_duration[w, w2],
                                             self.current_time[v] + t])
            self.dict_occupation = {clave: sorted(values, key=lambda x: x[0]) for clave, values in
                                    self.dict_occupation.items()}
            # Update route selected
            self.comm_req[w, w2] -= q
            if q != 0:
                self.comm_req_loaded[w, w2] += q
            # self.comm_req_loaded[w, w2] += q if q != 0 else None
            self.current_time[v] += t
            self.stops[v] += 1
            self.sol[v, w2, self.stops[v]] = (q, t)
            self.current_warehouse[v] = w2
        # " UPDATE 3º SALTO"
        previous_warehouse = {key[1]: value for key, value in self.sol.items()
                              if self.stops[v] >= 2 and key[0] == v and key[2] == self.stops[v] - 2}
        # todo: update tiempo
        # todo: conflictos saltos grandes (terceros)
        # self.sol.update({(v, w2, self.stops[v] - 2):
        #                      (min(self.veh_cap - max(self.sol[(v, previous_warehouse.keys(), self.stops[v] - 2)][0],
        #                                              self.sol[(v, self.current_warehouse[v], self.stops[v] - 1)][0]),
        #                           self.comm_req[(previous_warehouse.keys(), w2)]), t)
        #                      if (self.stops[v] >= 2
        #                          and self.comm_req[(previous_warehouse.keys(), w2)] > 0
        #                          and (v, previous_warehouse.keys(), self.stops[v] - 2) in self.sol.keys()
        #                          and (v, self.current_warehouse[v], self.stops[v] - 1) in self.sol.keys()
        #                          and self.sol[(v, previous_warehouse.keys(), self.stops[v] - 2)][0] < self.veh_cap
        #                          and self.sol[(v, self.current_warehouse[v], self.stops[v] - 1)][0] < self.veh_cap)
        #                  })
        return self.sol
