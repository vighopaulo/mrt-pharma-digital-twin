class ThroughputMonitor:
    def __init__(self):
        self.completed = 0
        self.start_time = 0.0
        self.current_time = 0.0

    def start(self, simulation_time=0.0):
        self.start_time = float(simulation_time)
        self.current_time = float(simulation_time)

    def record_completion(self, simulation_time, count=1):
        self.current_time = float(simulation_time)
        self.completed += int(count)

    def rate_per_hour(self):
        elapsed = self.current_time - self.start_time
        return 0.0 if elapsed <= 0 else (self.completed / elapsed) * 60.0

    def status(self):
        return {
            "completed": self.completed,
            "rate_per_hour": self.rate_per_hour(),
            "build": "51"
        }
