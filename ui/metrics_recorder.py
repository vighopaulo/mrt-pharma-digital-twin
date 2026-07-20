class MetricsRecorder:
    def __init__(self):
        self.metrics={}

    def record(self,name,time,value):
        self.metrics.setdefault(name,[]).append({
            "simulation_time":float(time),
            "value":float(value)
        })

    def latest(self,name):
        values=self.metrics.get(name,[])
        return values[-1] if values else None

    def clear(self):
        self.metrics.clear()

    def status(self):
        return {
            "metric_count":len(self.metrics),
            "sample_count":sum(len(v) for v in self.metrics.values()),
            "build":"50"
        }
