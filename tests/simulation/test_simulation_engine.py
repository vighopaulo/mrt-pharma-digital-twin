from datetime import datetime, timedelta
import pytest
from mrt.simulation.clock import SimulationClock
from mrt.simulation.engine import SimulationEngine
from mrt.simulation.event import SimulationEvent

START = datetime(2026, 7, 19, 8, 0)

def event(minutes: int, kind: str = "arrival") -> SimulationEvent:
    return SimulationEvent(
        scheduled_at=START + timedelta(minutes=minutes),
        priority=1,
        event_type=kind,
    )

def test_engine_executes_and_advances_clock():
    engine = SimulationEngine(SimulationClock(START))
    handled = []
    engine.register_handler("arrival", lambda e, _: handled.append(e.event_type))
    engine.schedule(event(10))
    assert engine.run() == 1
    assert handled == ["arrival"]
    assert engine.clock.current_time == START + timedelta(minutes=10)

def test_handler_can_schedule_follow_up():
    engine = SimulationEngine(SimulationClock(START))
    handled = []
    def arrival(e, active):
        handled.append("arrival")
        active.schedule(SimulationEvent(
            scheduled_at=e.scheduled_at + timedelta(minutes=5),
            priority=1,
            event_type="complete",
        ))
    engine.register_handler("arrival", arrival)
    engine.register_handler("complete", lambda e, _: handled.append("complete"))
    engine.schedule(event(0))
    assert engine.run() == 2
    assert handled == ["arrival", "complete"]

def test_missing_handler_preserves_event():
    engine = SimulationEngine(SimulationClock(START))
    engine.schedule(event(5, "unknown"))
    with pytest.raises(KeyError):
        engine.step()
    assert engine.event_queue.event_count == 1

def test_run_until_and_max_events():
    engine = SimulationEngine(SimulationClock(START))
    handled = []
    engine.register_handler("arrival", lambda e, _: handled.append(e.scheduled_at))
    engine.schedule(event(5))
    engine.schedule(event(20))
    assert engine.run(until=START + timedelta(minutes=10)) == 1
    assert len(handled) == 1
    assert engine.event_queue.event_count == 1
