from datetime import datetime
from uuid import UUID

import pytest

from mrt.simulation.event import (
    SimulationEvent,
    SimulationEventStatus,
)


def test_event_stores_required_fields() -> None:
    event = SimulationEvent(
        scheduled_at=datetime(2026, 7, 19, 9, 0),
        priority=1,
        event_type="dose_dispatch",
        payload={"dose_reference": "DOSE-001"},
    )

    assert isinstance(event.id, UUID)
    assert event.event_type == "dose_dispatch"
    assert event.payload["dose_reference"] == "DOSE-001"
    assert event.status == SimulationEventStatus.SCHEDULED


def test_event_type_is_trimmed() -> None:
    event = SimulationEvent(
        scheduled_at=datetime(2026, 7, 19, 9, 0),
        priority=1,
        event_type="  patient_arrival  ",
    )

    assert event.event_type == "patient_arrival"


def test_negative_priority_is_rejected() -> None:
    with pytest.raises(ValueError):
        SimulationEvent(
            scheduled_at=datetime(2026, 7, 19, 9, 0),
            priority=-1,
            event_type="patient_arrival",
        )


def test_valid_event_lifecycle() -> None:
    event = SimulationEvent(
        scheduled_at=datetime(2026, 7, 19, 9, 0),
        priority=1,
        event_type="patient_arrival",
    )

    event.mark_executed()

    assert event.status == SimulationEventStatus.EXECUTED


def test_executed_event_cannot_be_cancelled() -> None:
    event = SimulationEvent(
        scheduled_at=datetime(2026, 7, 19, 9, 0),
        priority=1,
        event_type="patient_arrival",
    )
    event.mark_executed()

    with pytest.raises(ValueError):
        event.cancel()
