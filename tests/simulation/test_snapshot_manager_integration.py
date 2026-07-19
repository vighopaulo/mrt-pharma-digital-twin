from datetime import datetime

from mrt.simulation.clock import SimulationClock
from mrt.simulation.engine import SimulationEngine
from mrt.simulation.event import SimulationEvent
from mrt.simulation.snapshot_manager import (
    SimulationSnapshotManager,
)


def test_native_engine_state_is_captured_periodically() -> None:
    start = datetime(2026, 7, 19, 8, 0)
    engine = SimulationEngine(clock=SimulationClock(start))
    manager = SimulationSnapshotManager(interval=2)

    first = SimulationEvent(
    event_type="arrival",
    scheduled_at=start,
    priority=0,
)
    second = SimulationEvent(
    event_type="arrival",
    scheduled_at=start,
    priority=0,
)

    engine.register_handler("arrival", lambda event, current_engine: None)
    engine.schedule(first)
    engine.schedule(second)

    engine.step()
    assert manager.capture_if_due(engine, 1) is None

    engine.step()
    snapshot = manager.capture_if_due(engine, 2)

    assert snapshot is not None
    assert snapshot.trigger_value == 2
    assert snapshot.state["metadata"]["processed_event_count"] == 2
