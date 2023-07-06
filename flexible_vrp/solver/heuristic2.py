# Class to solve the problem with a heuristic2 approach.
import random
import pandas as pd

from timeit import default_timer as timer
from flexible_vrp.core import Experiment, Solution


class Heuristic2(Experiment):
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
        self.time_limit = options["solver_config"]["TimeLimit"]
        self.prepare_data()
        best_sol = dict()
        best_sol["obj"] = 0
        cont = 0
        # Timer to search the best solution
        t_init = timer()
        while timer() - t_init <= self.time_limit:
            current_sol = self.gen_sol()
            # si le faltan com_req y si no entrega los comm_req en el req_time_limit -> desechar la solución
            if self.t_fin_req <= self.req_time_limit:
                # suma commodities opcionales entregados
                tot_opt = sum(self.comm_opt_loaded.values())
                # suma tiempo restante
                t_restante = 0
                for clave in self.dict_occupation_V:
                    t_restante += self.opt_time_limit - self.dict_occupation_V[clave][-1][1]
                # obj = ponderación entre comm opt entregados y tiempo restante
                obj = tot_opt + t_restante/self.opt_time_limit
                # cont = número de soluciones generadas
                cont = cont + 1
            else:
                obj = 0
            current_sol["obj"] = obj
            if current_sol["obj"] > best_sol["obj"]:
                best_sol = current_sol
        print("Numero de soluciones obtenidas: ", cont)
        data_json = self.get_solution(best_sol)
        self.solution = Solution({"data": data_json})
        return 1

    def gen_sol(self):
        # Generate dicts to store the number of commodities
        self.comm_req = {(w1, w2): 0 for w1 in self.warehouses for w2 in self.warehouses if w1 != w2}
        for c in [c for c in self.instance.data["commodities"] if c['required']]:
            self.comm_req[(c["origin"], c["destination"])] = c["quantity"]
        self.comm_opt = {(w1, w2): 0 for w1 in self.warehouses for w2 in self.warehouses if w1 != w2}
        for c in [c for c in self.instance.data["commodities"] if not c['required']]:
            self.comm_opt[(c["origin"], c["destination"])] = c["quantity"]
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
        self.dict_occupation_V = {v: [(0, 0)] for v in self.vehicles}
        self.dict_empty_W = {w: [(0, self.opt_time_limit)] for w in self.warehouses}
        self.sol = {(v, self.current_warehouse[v], self.stops[v]): (0, self.current_time[v], "inicio")
                    for v in self.vehicles}
        self.flag_t_fin_req = 1
        self.t_fin_req = self.opt_time_limit
        stop = False
        while not stop:
            self.explore()
            # Para en caso de que las ventanas temporales esten saturadas
            if self.tree:
                self.select_move()
                self.update()
            stop = self.check_if_stop()
        return self.sol

    def check_if_stop(self):
        # Parada (stop = 1) si no quedan comm_opt que entregar o si todos los vehículos superan el límite horario
        # lista de vehículos que ha superado el tiempo límite
        list_veh_time_over = [v for v in self.vehicles
                              if (self.current_time[v] + self.veh_cap * self.load_time) > self.opt_time_limit]
        stop = 0
        if all(valor == 0 for valor in (self.comm_req.values() and self.comm_opt.values())):
            stop = 1
            for v in self.vehicles:
                self.sol[v, self.current_warehouse[v], self.stops[v]] = \
                    ("req", 0, 0, "opt", 0, 0, self.current_time[v], "fin")
        else:
            for v in list_veh_time_over:
                self.sol[v, self.current_warehouse[v], self.stops[v]] = \
                    ("req", 0, 0, "opt", 0, 0, self.current_time[v], "fin")
        if len(list_veh_time_over) == len(self.vehicles):
            stop = 1
        self.vehicles = [v for v in self.vehicles if v not in list_veh_time_over]  # remove v de self.vehicles
        # Para en caso de que las ventanas temporales esten saturadas
        if not self.tree:
            stop = 1
        return stop

    def explore(self, w2=None):
        self.tree = {}
        counter = 1
        for (v, w2, w3) in [(v, w2, w3) for v in self.vehicles for w2 in self.warehouses for w3 in self.warehouses
                            if (w3 != w2 and w2 != self.current_warehouse[v])]:
            # Estructura: self.tree{(v,w2,w3): (q1, q2, q3, te_w, te_w2, te_w3, q1o, q2o, q3o)}
            # qX: cantidad comm_req cargada, qXo: cantidad comm_opt cargada
            flag = 1
            q1 = min(self.veh_cap, self.comm_req[self.current_warehouse[v], w2])
            q1o = min(self.veh_cap-q1, self.comm_opt[self.current_warehouse[v], w2])
            q2 = min(self.veh_cap, self.comm_req[w2, w3])
            q2o = min(self.veh_cap-q2, self.comm_opt[w2, w3])
            q3 = 0
            q3o = 0
            # Si existe el 2º salto y además existe el 3º salto (de current_w a w3)
            if (w3 != self.current_warehouse[v]
                    and (self.comm_req[self.current_warehouse[v], w3] + self.comm_opt[self.current_warehouse[v], w3]
                         > 0)
                    and max(self.comm_req[self.current_warehouse[v], w2] + self.comm_opt[self.current_warehouse[v], w2],
                            self.comm_req[w2, w3] + self.comm_opt[w2, w3]) < self.veh_cap)\
                    and q1 + q1o + q2 + q2o > 0:
                q3 = min(self.veh_cap - max(q1 + q1o, q2 + q2o), self.comm_req[self.current_warehouse[v], w3])
                q3o = min(self.veh_cap - q3 - max(q1 + q1o, q2 + q2o), self.comm_opt[self.current_warehouse[v], w3])
            counter = counter + 1
            # Si sólo existe el 1º salto
            if counter == len(self.warehouses):
                if q2 + q2o + q3 + q3o == 0 and all((v, w2, w4) not in self.tree.keys() for w4 in self.warehouses):
                    flag = 0
                counter = 1

            t1 = (q1 + q1o + q3 + q3o) * (self.load_time + self.unload_time) + \
                self.trip_duration[self.current_warehouse[v], w2]
            t2 = (q2 + q2o) * (self.load_time + self.unload_time) + self.trip_duration[w2, w3]
            # te: tiempos de espera para que no exista simultaneidad
            te_w = 0  # Solo necesario en stop 0
            te_w2 = 0
            te_w3 = 0
            t_max_load = self.veh_cap * self.load_time
            t_unload_w2 = (q1 + q1o) * self.unload_time
            t_unload_w3 = (q2 + q2o + q3 + q3o) * self.unload_time
            t_departure_w = self.current_time[v] + (q1 + q1o + q3 + q3o) * self.load_time
            t_arrival_min_w2 = t_departure_w + self.trip_duration[self.current_warehouse[v], w2]
            if flag == 0 and q2 + q2o + q3 + q3o == 0 and q1 + q1o > 0:  # un salto
                t_departure_w2 = t_arrival_min_w2 + t_unload_w2 + t_max_load
            else:
                t_departure_w2 = t_arrival_min_w2 + t_unload_w2 + (q2 + q2o) * self.load_time

            # SIMULTANEITY VEH
            # Definir tiempo espera para s=0 te_w
            if self.stops[v] == 0:
                selected_interval_w = [self.current_time[v], t_departure_w]
                window_duration = (selected_interval_w[1] - selected_interval_w[0])
                lst = self.dict_empty_W[self.current_warehouse[v]]
                for tup in lst:
                    if tup[1] > window_duration and selected_interval_w[1] < (tup[0] + tup[1]):
                        te_w = max(tup[0] - selected_interval_w[0], 0)
                        break
                    else:
                        te_w = - 1

            # Definir tiempo espera te_w2
            selected_interval_w2 = [t_arrival_min_w2 + te_w, t_departure_w2 + te_w]
            window_duration = (selected_interval_w2[1] - selected_interval_w2[0])
            lst = self.dict_empty_W[w2]
            for tup in lst:
                if tup[1] > window_duration and selected_interval_w2[1] < (tup[0] + tup[1]):
                    te_w2 = max(tup[0] - selected_interval_w2[0], 0)
                    break
                else:
                    te_w2 = - 1

            # Definir tiempo espera salto 2 te_w3
            if flag != 0 and q2 + q2o + q3 + q3o > 0:
                t_arrival_min_w3 = t_departure_w2 + self.trip_duration[w2, w3]
                t_departure_w3 = t_arrival_min_w3 + t_unload_w3 + t_max_load
                selected_interval_w3 = [t_arrival_min_w3 + te_w + te_w2, t_departure_w3 + te_w + te_w2]
                window_duration = selected_interval_w3[1] - selected_interval_w3[0]
                lst = self.dict_empty_W[w3]
                for tup in lst:
                    if tup[1] > window_duration and selected_interval_w3[1] < (tup[0] + tup[1]):
                        te_w3 = max(tup[0] - selected_interval_w3[0], 0)
                        break
                    else:
                        te_w3 = - 1
            # tiempos negativos indican que no hay espacio en las ventanas temporales
            if te_w != -1 and te_w2 != -1 and te_w3 != -1:
                # Definición self.tree
                if flag != 0 and q2 + q2o + q3 + q3o > 0:
                    self.tree[(v, w2, w3)] = (q1, q2, q3, te_w, te_w2, te_w3, q1o, q2o, q3o)
                if flag == 0 and q2 + q2o + q3 + q3o == 0 and q1 + q1o > 0:
                    self.tree[(v, w2, "0")] = (q1, q2, q3, te_w, te_w2, te_w3, q1o, q2o, q3o)
        return self.tree

    def select_move(self):
        # attractive
        alpha = 1/(self.veh_cap + 1)
        # dict_attractive: diccionario que recoge el atractivo de cada movimiento
        dict_attractive = {clave: valor[0] + valor[1] * alpha + valor[2] * alpha ** 2
                           + (valor[6] + valor[7] * alpha + valor[8] * alpha ** 2) * alpha ** 2
                           for clave, valor in self.tree.items()}
        dict_sorted_attractive = {clave: valor for clave, valor in sorted(dict_attractive.items(),
                                                                          key=lambda item: item[1], reverse=True)}
        # Progresión geométrica para asignar probabilidades
        n = len(self.tree)  # n: número de términos de la progresión
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
        w3 = self.move[2]
        q1 = self.tree[self.move][0]
        q2 = self.tree[self.move][1]
        q3 = self.tree[self.move][2]
        te_w = self.tree[self.move][3]
        te_w2 = self.tree[self.move][4]
        te_w3 = self.tree[self.move][5]
        q1o = self.tree[self.move][6]
        q2o = self.tree[self.move][7]
        q3o = self.tree[self.move][8]
        t_load_w = (q1 + q1o + q3 + q3o) * self.load_time
        t_load_w2 = (q2 + q2o) * self.load_time
        t_max_load = self.veh_cap * self.load_time
        t_unload_w2 = (q1 + q1o) * self.unload_time
        t_unload_w3 = (q2 + q2o + q3 + q3o) * self.unload_time
        t_arrival_w = self.current_time[v] + te_w
        t_departure_w = t_arrival_w + t_load_w
        t_arrival_w2 = t_departure_w + self.trip_duration[w, w2] + te_w2
        t_departure_w2 = t_arrival_w2 + t_unload_w2 + t_load_w2
        t_arrival_w3 = 0
        t_departure_w3 = 0
        if w3 != "0":
            t_arrival_w3 = t_departure_w2 + self.trip_duration[w2, w3] + te_w3
            t_departure_w3 = t_arrival_w3 + t_unload_w3 + t_max_load

        # Update dict_occupation_W
        # dict_occupation_W[tiempo inicio ocupación, tiempo fin ocupación] muestra las ventanas temporales ocupadas
        if self.stops[v] == 0:
            self.dict_occupation_W[w].append((v, self.stops[v], self.current_time[v] + te_w, self.current_time[v]
                                              + te_w + t_load_w))
        if w3 != "0":
            self.dict_occupation_W[w2].append((v, self.stops[v] + 1, t_arrival_w2, t_departure_w2))
            self.dict_occupation_W[w3].append((v, self.stops[v] + 2, t_arrival_w3, t_departure_w3))
        else:
            self.dict_occupation_W[w2].append((v, self.stops[v] + 1, t_arrival_w2, t_departure_w2 + t_max_load))
        self.dict_occupation_W = {clave: sorted(values, key=lambda x: x[2]) for clave, values in
                                  self.dict_occupation_W.items()}
        # Update dict_occupation_V
        # dict_occupation_V guarda para cada vehículo el tiempo de llegada, tiempo de salida de un warehouse,
        #   el tipo y cantidad de commodities que carga en ese warehouse.
        if w3 != "0":
            self.dict_occupation_V[v].append(
                (t_arrival_w, t_departure_w, w, {(w, w2, "req"): q1}, {(w, w3, "req"): q3}))
            self.dict_occupation_V[v].append(
                (t_arrival_w, t_departure_w, w, {(w, w2, "opt"): q1o}, {(w, w3, "opt"): q3o}))
            self.dict_occupation_V[v].append((t_arrival_w2, t_departure_w2, w2, {(w2, w3, "req"): q2}))
            self.dict_occupation_V[v].append((t_arrival_w2, t_departure_w2, w2, {(w2, w3, "opt"): q2o}))
            self.dict_occupation_V[v].append((t_arrival_w3, t_departure_w3, w3, {(): ()}))
        else:
            self.dict_occupation_V[v].append((t_arrival_w, t_departure_w, w, {(w, w2, "req"): q1}))
            self.dict_occupation_V[v].append((t_arrival_w, t_departure_w, w, {(w, w2, "opt"): q1o}))
            self.dict_occupation_V[v].append((t_arrival_w2, t_departure_w2, w2, {(): ()}))

        # Update dict_empty
        # dict_empty_W guarda el inicio de una ventana temporal libre y su duración: [t inicio vacío, duración]
        self.dict_empty_W = {w: [] for w in self.warehouses}
        for x, tupla in self.dict_occupation_W.items():
            if len(self.dict_occupation_W[x]) != 0:
                if tupla[0][2] > 0:
                    self.dict_empty_W[x].append((0, tupla[0][2]))
                for i in range(len(tupla)):
                    if i < len(tupla)-1:
                        self.dict_empty_W[x].append((tupla[i][3], tupla[i + 1][2] - tupla[i][3]))
                    else:
                        if self.opt_time_limit - tupla[i][3] < 0:
                            b = 0
                        else:
                            b = self.opt_time_limit - tupla[i][3]
                        self.dict_empty_W[x].append((tupla[i][3], b))
            else:
                self.dict_empty_W[x].append((0, self.opt_time_limit))

        # Update commodities
        self.comm_req[w, w2] -= q1
        self.comm_opt[w, w2] -= q1o
        # t_fin_req guarda el valor del tiempo cuando termina de entregar comm_req
        if all(valor == 0 for valor in self.comm_req.values()) and self.flag_t_fin_req == 1:
            if q3 + q2 == 0:
                self.t_fin_req = t_arrival_w2 + t_unload_w2
            else:
                self.t_fin_req = t_arrival_w3 + t_unload_w3
            self.flag_t_fin_req = 0

        if w3 != "0":
            self.comm_req[w2, w3] -= q2
            self.comm_opt[w2, w3] -= q2o
            if q3 > 0:
                self.comm_req[w, w3] -= q3
            if q3o > 0:
                self.comm_opt[w, w3] -= q3o
        if q1 > 0:
            self.comm_req_loaded[w, w2] += q1
        if q1o > 0:
            self.comm_opt_loaded[w, w2] += q1o
        if w3 != "0":
            if q2 > 0:
                self.comm_req_loaded[w2, w3] += q2
            if q2o > 0:
                self.comm_opt_loaded[w2, w3] += q2o
            if q3 > 0:
                self.comm_req_loaded[w, w3] += q3
            if q3o > 0:
                self.comm_opt_loaded[w, w3] += q3o
        # Update solution
        # solucion: vehículo v llega a w en t_arrival_w, donde carga q1 + q3
        self.sol[v, w, self.stops[v]] = ("req", q1, q3, "opt", q1o, q3o, t_arrival_w)
        if w3 != "0":
            self.sol[v, w2, self.stops[v] + 1] = ("req", q2, 0, "opt", q2o, 0, t_arrival_w2 + t_unload_w2)
            self.current_warehouse[v] = w3
            self.current_time[v] = t_arrival_w3 + t_unload_w3
            self.stops[v] += 2
        else:
            self.current_warehouse[v] = w2
            self.current_time[v] = t_arrival_w2 + t_unload_w2
            self.stops[v] += 1
        return self.sol

    def get_solution(self, best_sol):
        data_solution = best_sol
        df = pd.DataFrame(data_solution)
        df.to_excel('archivo_excel.xlsx', index=False)
        return data_solution
