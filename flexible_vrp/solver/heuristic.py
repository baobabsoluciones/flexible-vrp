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
        self.dict_occupation_W = {w: [] for w in self.warehouses}
        self.dict_occupation_V = {v: [] for v in self.vehicles}
        self.dict_empty_W = {w: [(0, 480)] for w in self.warehouses}
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
        self.tree = {}
        for (v, w2, w3) in [(v, w2, w3) for v in self.vehicles for w2 in self.warehouses for w3 in self.warehouses
                            if (w3 != w2 and w2 != self.current_warehouse[v])]:
            # Estructura: self.tree{(v,w2,w3): (q1+q2+q3,t1+t2+t3+te)}
            q1 = min(self.veh_cap, self.comm_req[self.current_warehouse[v], w2])
            q2 = min(self.veh_cap, self.comm_req[w2, w3])
            q3 = 0
            t1 = q1 * (self.load_time + self.unload_time) + self.trip_duration[self.current_warehouse[v], w2]
            t2 = q2 * (self.load_time + self.unload_time) + self.trip_duration[self.current_warehouse[v], w2]
            t3 = 0
            te = 0
            # Si existe el 2º salto
            if self.comm_req[w2, w3] > 0:
                # Si además existe el 3º salto (de current_w a w3)
                if (w3 != self.current_warehouse[v]
                        and self.comm_req[self.current_warehouse[v], w3] > 0
                        and max(self.comm_req[self.current_warehouse[v], w2], self.comm_req[w2, w3]) < self.veh_cap
                        and self.comm_req[w2, w3] > 0):
                    q3 = min(self.veh_cap - max(q1, q2), self.comm_req[self.current_warehouse[v], w3])
                    t3 = q3 * (self.load_time + self.unload_time)
                self.tree[(v, w2, w3)] = (q1 + q2 + q3, t1 + t2 + t3 + te)
            # Si sólo existe el 1º salto
            elif self.comm_req[self.current_warehouse[v], w2] > 0 \
                    and not any((v, w2, w3) in self.tree.keys() for w3 in self.warehouses):
                self.tree[(v, w2, 0)] = (q1, t1 + te)
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
        t_arrival = self.current_time[v] + self.trip_duration[w, w2]
        t_load = q * self.load_time
        t_max_load = self.veh_cap * self.load_time
        t_unload = q * self.unload_time
        t = self.current_time[v] + self.trip_duration[w, w2] + t_unload + t_max_load  # t_departure

        # SIMULTANEITY VEH
        # Ventanas temporales del movimiento elegido para origen y destino
        if self.stops[v] != 0:
            selected_interval = [t_arrival, t]
        else:
            first_interval = [self.current_time[v], self.current_time[v] + t_load]
            selected_interval = [t_load + t_arrival, t_load + t]

        # Comprobación de intersección entre los intervalos
        busy = False
        if self.stops[v] != 0:
            busy = any((interval[2] < selected_interval[0] < interval[3] or selected_interval[0] < interval[2] <
                        selected_interval[1]) for interval in self.dict_occupation_W[w2])
        else:
            busy = any((interval[2] < first_interval[0] < interval[3] or first_interval[0] < interval[2] <
                        first_interval[1]) for interval in self.dict_occupation_W[w]) or \
                   any((interval[2] < selected_interval[0] < interval[3] or selected_interval[0] < interval[2] <
                        selected_interval[1]) for interval in self.dict_occupation_W[w2])

        if not busy:
            # Update warehouse occupation time
            if self.stops[v] != 0:
                self.dict_occupation_W[w2].append((v, self.stops[v] + 1, t_arrival, t))
            else:
                self.dict_occupation_W[w].append((v, self.stops[v], self.current_time[v], self.current_time[v] + t_load))
                self.dict_occupation_W[w2].append((v, self.stops[v] + 1, t_load + t_arrival, t_load + t))
            self.dict_occupation_W = {clave: sorted(values, key=lambda x: x[2]) for clave, values in
                                      self.dict_occupation_W.items()}
            # dict_empty_W guarda el inicio de una ventana temporal libre y su duración: [t inicio vacio, duracion]
            self.dict_empty_W = {w: [(tupla[i][3], tupla[i + 1][2] - tupla[i][3]) if i < len(tupla) - 1
                                     else (tupla[i][3], 480 - tupla[i][3])
                                     for i in range(len(tupla))] for w, tupla in self.dict_occupation_W.items()}

            # Update route selected
            self.comm_req[w, w2] -= q
            if q != 0:
                self.comm_req_loaded[w, w2] += q
            # self.comm_req_loaded[w, w2] += q if q != 0 else None
            if self.stops[v] != 0:
                self.current_time[v] += t
            else:
                self.current_time[v] = t + t_load
            self.stops[v] += 1
            self.sol[v, w2, self.stops[v]] = (q, t)
            self.current_warehouse[v] = w2
        # todo: if busy

        # " UPDATE 3º SALTO"
        # previous_warehouse = {key[1]: value for key, value in self.sol.items()
        #                       if self.stops[v] >= 2 and key[0] == v and key[2] == self.stops[v] - 2}
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
