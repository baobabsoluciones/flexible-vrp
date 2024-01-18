from cornflow_client.core.tools import load_json
from flexible_vrp import FlexibleVRP
from analysis_tools.read_tools import read_input_data
from mango.processing.file_functions import list_files_directory

# config = {
#     "solver": "basic_mip",
#     "solver_name": "gurobi",
#     "solver_config": {"TimeLimit": 600, "gap": 0, "Heuristics": 0.0},
# }

# gap absoluto es: allow
# gap relativo es: ratio
config = {
    "solver": "basic_mip",
    "solver_config": {"sec": 600, "allow": 0},

}

# config = {
#     "solver": "heuristic2",
#     "solver_config": {"TimeLimit": 120}
# }

# data = load_json("./data/simple_instance.json")

# file_path = "data/datos_min.xlsx"
# file_path = "data/inst_1.xlsx"
file_path = "data/inst_2.xlsx"
# file_path = "data/inst_3.xlsx"
# file_path = "data/inst_4.xlsx"
# file_path = "data/inst_5.xlsx"
# file_path = "data/inst_6.xlsx"
# file_path = "data/inst_7_dia_1.xlsx"
# file_path = "data/inst_8_dia_2.xlsx"
# file_path = "data/inst_9_dia_3.xlsx"

data = read_input_data(file_path)

# Solve the problem.
app = FlexibleVRP()
solution, checks, instance_checks, log_txt, log = app.solve(data, config)

print("Solution: ", solution)

list_path = list_files_directory(directory="data", extensions=["xlsx"])

# list_path = ["data/inst_1.xlsx", "data/inst_2.xlsx", "data/inst_3.xlsx", "data/inst_4.xlsx", "data/inst_5.xlsx",
#              "data/inst_6.xlsx", "data/inst_7_dia_1.xlsx", "data/inst_8_dia_2.xlsx", "data/inst_9_dia_3.xlsx"]
# for file_path in list_path:
#     data = read_input_data(file_path)
#     inst_name = {'name': file_path.split("/")[-1]}
#     # Solve the problem.
#     app = FlexibleVRP()
#     solution, checks, instance_checks, log_txt, log = app.solve(data, config, inst_name)
#
#     print("Solution: ", solution)
