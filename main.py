from cornflow_client.core.tools import load_json
from flexible_vrp import FlexibleVRP
from analysis_tools.read_tools import read_input_data


# Todo: create functions to read the config and data.
# config = {
#     "solver": "basic_mip",
#     "solver_name": "gurobi",
#     "solver_config": {"TimeLimit": 120, "gap": 0},
# }

config = {
    "solver": "heuristic2",
    "solver_config": {"TimeLimit": 120}
}

# data = load_json("./data/simple_instance.json")
# file_path = "data/inst_1.xlsx"
file_path = "data/inst_2.xlsx"
# file_path = "data/inst_3.xlsx"
# file_path = "data/inst_4.xlsx"
# file_path = "data/inst_5.xlsx"
# file_path = "data/inst_6.xlsx"
# file_path = "data/dia_1.xlsx"
# file_path = "data/dia_2.xlsx"
# file_path = "data/dia_3.xlsx"
# file_path = "data/datos_min.xlsx"
# file_path = "data/datos_1_comm.xlsx"
data = read_input_data(file_path)

# Solve the problem.
app = FlexibleVRP()
solution, checks, instance_checks, log_txt, log = app.solve(data, config)

print("Solution: ", solution)
