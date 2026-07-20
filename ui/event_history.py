class EventHistory:
    def __init__(self,max_entries=1000):
        self.max_entries=max_entries
        self.events=[]

    def record(self,event_type,simulation_time,entity=None):
        self.events.append({
            "event_type":event_type,
            "simulation_time":float(simulation_time),
            "entity":entity
        })
        self.events=self.events[-self.max_entries:]

    def recent(self,n=20):
        return self.events[-n:]

    def clear(self):
        self.events.clear()

    def status(self):
        return {"recorded_events":len(self.events),"build":"49"}
