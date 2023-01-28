

class HeuristicSolution():
    def __init__(self):
        pass

    def build_solution(self):
        while not self.stop_contition():
            self.select_vehicle()
            self.select_commodity()
        self.gen_ouput_data()

    def select_vehicle(self):
        pass

    def select_commodity(self):
        pass

    def stop_contition(self):
        pass

    def gen_ouput_data(self):
        pass