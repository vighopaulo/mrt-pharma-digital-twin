from datetime import datetime, timedelta
from mrt.simulation.clock import SimulationClock
from mrt.simulation.engine import SimulationEngine
from mrt.simulation.event import SimulationEvent

def test_three_stage_patient_workflow():
    start = datetime(2026, 7, 19, 8, 0)
    engine = SimulationEngine(SimulationClock(start))
    timeline = []

    def arrival(e, active):
        timeline.append("arrival")
        active.schedule(SimulationEvent(e.scheduled_at + timedelta(minutes=10), 1, "uptake"))

    def uptake(e, active):
        timeline.append("uptake")
        active.schedule(SimulationEvent(e.scheduled_at + timedelta(minutes=20), 1, "scan"))

    engine.register_handler("arrival", arrival)
    engine.register_handler("uptake", uptake)
    engine.register_handler("scan", lambda e, _: timeline.append("scan"))
    engine.schedule(SimulationEvent(start, 1, "arrival"))

    assert engine.run() == 3
    assert timeline == ["arrival", "uptake", "scan"]
    assert engine.clock.current_time == start + timedelta(minutes=30)
