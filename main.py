from cornflow_client.core.tools import load_json
from flexible_vrp import FlexibleVRP
from analysis_tools.read_tools import read_input_data
from mango.processing.file_functions import list_files_directory
import os
import datetime


def solver_inst(config, fecha):
    """
    Ejecuta todas las instancias con el solver elegido y guarda la fecha y hora de ejecución.

    :param config: Configuración del solver, que incluye el solver a utilizar y las instancias a resolver.
    :param fecha: Fecha y hora en la que se ejecuta la función, para registrar en los resultados.
    """
    list_path = list_files_directory(directory="data", extensions=["xlsx"])
    for file_path in list_path:
        try:
            data = read_input_data(file_path)
            # Solve the problem.
            app = FlexibleVRP()
            solution, checks, instance_checks, log_txt, log = app.solve(data, config)
            if config["solver"] == "basic_mip":
                if "solver_name" in config:
                    # basic_mip gurobi
                    nombre_log = f"{fecha}_log_mip_gurobi_{os.path.basename(file_path).split('.')[0]}.log"
                    nuevo_excel = f"{fecha}_mip_gurobi_{os.path.basename(file_path).split('.')[0]}.xlsx"
                else:
                    # basic_mip cbc
                    nombre_log = f"{fecha}_log_mip_cbc_{os.path.basename(file_path).split('.')[0]}.log"
                    nuevo_excel = f"{fecha}_mip_cbc_{os.path.basename(file_path).split('.')[0]}.xlsx"
                os.rename('C:/TFG/Flexible/data/logfile.log',
                          f"C:/TFG/Flexible/data/{nombre_log}")
            else:
                # heuristic
                nuevo_excel = f"{fecha}_heuristic_{os.path.basename(file_path).split('.')[0]}.xlsx"
            os.rename('C:/TFG/Flexible/data/data_salida/solucion.xlsx',
                      f"C:/TFG/Flexible/data/data_salida/{nuevo_excel}")
            print("Solution: ", solution)
        except ValueError as e:
            if config["solver"] == "basic_mip":
                if "solver_name" in config:
                    print(f"Error processing file {file_path} with gurobi: {e}")
                    nombre_log = f"{fecha}_log_mip_gurobi_{os.path.basename(file_path).split('.')[0]}.log"
                else:
                    # cbc
                    print(f"Error processing file {file_path} with cbc: {e}")
                    nombre_log = f"{fecha}_log_mip_cbc_{os.path.basename(file_path).split('.')[0]}.log"
                os.rename('C:/TFG/Flexible/data/logfile.log',
                          f"C:/TFG/Flexible/data/{nombre_log}")
            continue
    return


fecha_hora_inicio = datetime.datetime.now().strftime("%Y%m%d_%H%M")

# --------------------------------------------------------------------------------------------------------------
# Elección de solver

# config = {
#     "solver": "basic_mip",
#     "solver_name": "gurobi",
#     "solver_config": {"TimeLimit": 3600, "gap": 0, "Heuristics": 0.0},
# }
# solver_inst(config, fecha_hora_inicio)

# gap absoluto es: allow
# gap relativo es: ratio
# config = {
#     "solver": "basic_mip",
#     "solver_config": {"sec": 600, "allow": 0},
# }
# solver_inst(config, fecha_hora_inicio)

config = {
     "solver": "heuristic2",
     "solver_config": {"TimeLimit": 600}
 }
solver_inst(config, fecha_hora_inicio)

print(datetime.datetime.now().strftime("%Y%m%d_%H%M"))

# --------------------------------------------------------------------------------------------------------------
# Execute only one instance

# Instancias

# file_path = "data/inst_1.xlsx"
# file_path = "data/inst_2.xlsx"
# file_path = "data/inst_3.xlsx"
# file_path = "data/inst_4.xlsx"
# file_path = "data/inst_5.xlsx"
# file_path = "data/inst_6.xlsx"
# file_path = "data/inst_7_dia_1.xlsx"
# file_path = "data/inst_8_dia_2.xlsx"
# file_path = "data/inst_9_dia_3.xlsx"

# Solve the problem

# data = read_input_data(file_path)
# app = FlexibleVRP()
# solution, checks, instance_checks, log_txt, log = app.solve(data, config)

# print("Solution: ", solution)
