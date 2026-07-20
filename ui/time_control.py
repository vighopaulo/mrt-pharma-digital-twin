class TimeControl:
    def __init__(self):
        self.simulation_time=0.0
    def advance(self,dt):
        self.simulation_time+=float(dt)
    def reset(self):
        self.simulation_time=0.0
    def status(self):
        return {"simulation_time":self.simulation_time,"build":"47"}
