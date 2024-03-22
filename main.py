from cornflow_client.core.tools import load_json
from flexible_vrp import FlexibleVRP
from analysis_tools.read_tools import read_input_data
from mango.processing.file_functions import list_files_directory
import os
import datetime


def solver_inst(config, fecha):
    # list_path = list_files_directory(directory="data", extensions=["xlsx"])
    list_path = ["data/inst_1.xlsx", "data/inst_2.xlsx", "data/inst_3.xlsx", "data/inst_4.xlsx",
                 "data/inst_5.xlsx", "data/inst_6.xlsx", "data/inst_7_dia_1.xlsx", "data/inst_8_dia_2.xlsx",
                 "data/inst_9_dia_3.xlsx", "data/inst_10.xlsx", "data/inst_11.xlsx", "data/inst_12.xlsx"]
    for file_path in list_path:
        data = read_input_data(file_path)
        # Solve the problem.
        app = FlexibleVRP()
        solution, checks, instance_checks, log_txt, log = app.solve(data, config)
        if config["solver"] == "basic_mip":
            if "solver_name" in config:
                nombre_log = f"{fecha}_log_mip_gurobi_{file_path.split("/")[-1].split(".")[0]}.log"
                nuevo_excel = f"{fecha}_mip_gurobi_{file_path.split("/")[-1].split(".")[0]}.xlsx"
            else:
                nombre_log = f"{fecha}_log_mip_cbc_{file_path.split("/")[-1].split(".")[0]}.log"
                nuevo_excel = f"{fecha}_mip_cbc_{file_path.split("/")[-1].split(".")[0]}.xlsx"
            os.rename('C:/Users/MartaSierra/PycharmProjects/flexible-vrp/data/logfile.log',
                      f"C:/Users/MartaSierra/PycharmProjects/flexible-vrp/data/{nombre_log}")
        else:
            nuevo_excel = f"{fecha}_heuristic_{file_path.split("/")[-1].split(".")[0]}.xlsx"
        os.rename('C:/Users/MartaSierra/PycharmProjects/flexible-vrp/data/data_salida/solucion.xlsx',
                  f"C:/Users/MartaSierra/PycharmProjects/flexible-vrp/data/data_salida/{nuevo_excel}")
        print("Solution: ", solution)
    return


fecha_hora_inicio = datetime.datetime.now().strftime("%Y%m%d_%H%M")

config = {
    "solver": "basic_mip",
    "solver_name": "gurobi",
    "solver_config": {"TimeLimit": 600, "gap": 0, "Heuristics": 0.0},
}
# solver_inst(config, fecha_hora_inicio)

# gap absoluto es: allow
# gap relativo es: ratio
# config = {
#     "solver": "basic_mip",
#     "solver_config": {"sec": 600, "allow": 0},
# }
# solver_inst(config, fecha_hora_inicio)
#
config = {
    "solver": "heuristic2",
    "solver_config": {"TimeLimit": 120}
}
# solver_inst(config, fecha_hora_inicio)
# print(datetime.datetime.now().strftime("%Y%m%d_%H%M"))
# data = load_json("./data/simple_instance.json")

# file_path = "data/datos_min.xlsx"
file_path = "data/inst_1.xlsx"
# file_path = "data/inst_2.xlsx"
# file_path = "data/inst_3.xlsx"
# file_path = "data/inst_4.xlsx"
# file_path = "data/inst_5.xlsx"
# file_path = "data/inst_6.xlsx"
# file_path = "data/inst_7_dia_1.xlsx"
# file_path = "data/inst_8_dia_2.xlsx"
# file_path = "data/inst_9_dia_3.xlsx"
# file_path = "data/inst_10.xlsx"
# file_path = "data/inst_11.xlsx"
# file_path = "data/inst_12.xlsx"

data = read_input_data(file_path)

# Solve the problem.
app = FlexibleVRP()
solution, checks, instance_checks, log_txt, log = app.solve(data, config)

print("Solution: ", solution)


