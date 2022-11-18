# Class to solve the problem with a basic mip.

from ..core import Experiment, Solution
from .basic_mip_tools.create_model import create_model


class BasicMip(Experiment):
    def __init__(self, instance, solution=None):
        super().__init__(instance, solution)

    def solve(self, options):
        if not self.instance.to_dict():
            raise ValueError("The instance is empty")
        # Todo: replace this by the solve method
        """
        Example of solve method:
        
        model = create_model()
        
        # Prepare data
        data = self.prepare_model_data(model)
        model_instance = model.create_instance(data, report_timing=False)
        logfile = "./data/logfile.log"
        # Solve
        opt = self.set_solver(options)
        try:
            result = opt.solve(
                model_instance,
                tee=True,
                warmstart=False,
                logfile=logfile,
            )
        except ApplicationError:
            message = "Solver error: a solver license may not be available to solve the model."
            raise Exception(message)

        self.status = get_status(result)
        model_result = model_instance
        obj = model_instance.f_obj()
        print("Status: {} Objective value: {}".format(self.status, obj))

        # Prepare solution
        if is_feasible(self.status):
            self.totals = self.get_total(model_result, result)
            model_solution = self.get_model_solution(model_result)
            self.solution = Solution(self.build_solution(model_solution))
        else:
            self.solution = self.get_empty_solution()
            self.variables_to_excel(model_result)

        return dict(status=STATUS_TIME_LIMIT, status_sol=SOLUTION_STATUS_FEASIBLE)
        """
        

        model = create_model()
        self.solution = Solution({"data": "This solver is not implemented yet"})
        return {}
