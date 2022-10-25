from flexible_vrp import FlexibleVRP


# Todo: create functions to read the config and data.
config = {"solver": "basic_mip"}
data = {"data": None}

# Solve the problem.
app = FlexibleVRP()
solution, checks, instance_checks, log_txt, log = app.solve(data, config)

print("Solution: ", solution)
