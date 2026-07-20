class SimulationControls:
    def __init__(self):
        self.state='stopped'
    def start(self): self.state='running'
    def pause(self): self.state='paused'
    def reset(self): self.state='stopped'
    def status(self): return {'simulation_state':self.state,'build':'45'}
