from datetime import datetime, timezone

import pytest

from mrt.simulation.snapshot_manager import (
    SimulationSnapshotManager,
)


class FakeEngine:
    def __init__(self) -> None:
        self.state = {"clock": 0, "queue": ["patient-1"]}

    def export_state(self) -> dict:
        return {
            "clock": self.state["clock"],
            "queue": list(self.state["queue"]),
        }


def test_snapshot_is_due_at_interval() -> None:
    manager = SimulationSnapshotManager(interval=5)

    assert manager.should_snapshot(5) is True
    assert manager.should_snapshot(10) is True
    assert manager.should_snapshot(4) is False


def test_zero_does_not_create_snapshot() -> None:
    manager = SimulationSnapshotManager(interval=5)

    assert manager.capture_if_due(FakeEngine(), 0) is None


def test_capture_stores_independent_state_copy() -> None:
    engine = FakeEngine()
    manager = SimulationSnapshotManager(interval=5)

    snapshot = manager.capture(
        engine,
        5,
        created_at=datetime(2026, 7, 19, tzinfo=timezone.utc),
    )
    engine.state["queue"].append("patient-2")

    assert snapshot.state["queue"] == ["patient-1"]


def test_duplicate_trigger_is_not_captured_twice() -> None:
    manager = SimulationSnapshotManager(interval=5)
    engine = FakeEngine()

    assert manager.capture_if_due(engine, 5) is not None
    assert manager.capture_if_due(engine, 5) is None


def test_retention_policy_keeps_latest_snapshots() -> None:
    manager = SimulationSnapshotManager(
        interval=5,
        max_snapshots=2,
    )
    engine = FakeEngine()

    manager.capture(engine, 5)
    manager.capture(engine, 10)
    manager.capture(engine, 15)

    assert [item.trigger_value for item in manager.snapshots] == [10, 15]


def test_invalid_interval_is_rejected() -> None:
    with pytest.raises(ValueError):
        SimulationSnapshotManager(interval=0)
