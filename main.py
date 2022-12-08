from cornflow_client.core.tools import load_json
from flexible_vrp import FlexibleVRP
from analysis_tools.read_tools import read_input_data


# Todo: create functions to read the config and data.
config = {"solver": "basic_mip", "solver_name":"gurobi", "solver_config":{"TimeLimit":120, "gap":0.01}}
# data = load_json("./data/simple_instance.json")
file_path = "H:\Mi unidad\\academico\docencia\\tfx\en_curso\stn\codigo\\flexible-vrp\data\datos2.xlsx"
data = read_input_data(file_path)

# Solve the problem.
app = FlexibleVRP()
solution, checks, instance_checks, log_txt, log = app.solve(data, config)

print("Solution: ", solution)
