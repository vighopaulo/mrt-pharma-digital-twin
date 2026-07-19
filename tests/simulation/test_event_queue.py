from datetime import datetime

import pytest

from mrt.simulation.event import (
    SimulationEvent,
    SimulationEventStatus,
)
from mrt.simulation.event_queue import SimulationEventQueue


def make_event(
    hour: int,
    minute: int,
    priority: int,
    event_type: str,
) -> SimulationEvent:
    return SimulationEvent(
        scheduled_at=datetime(2026, 7, 19, hour, minute),
        priority=priority,
        event_type=event_type,
    )


def test_events_execute_in_chronological_order() -> None:
    queue = SimulationEventQueue()
    later = make_event(9, 10, 1, "later")
    earlier = make_event(9, 0, 1, "earlier")

    queue.schedule(later)
    queue.schedule(earlier)

    assert queue.pop_next() is earlier
    assert queue.pop_next() is later


def test_priority_breaks_same_time_ties() -> None:
    queue = SimulationEventQueue()
    low_priority = make_event(9, 0, 5, "low")
    high_priority = make_event(9, 0, 1, "high")

    queue.schedule(low_priority)
    queue.schedule(high_priority)

    assert queue.pop_next() is high_priority
    assert queue.pop_next() is low_priority


def test_insertion_order_breaks_exact_ties() -> None:
    queue = SimulationEventQueue()
    first = make_event(9, 0, 1, "first")
    second = make_event(9, 0, 1, "second")

    queue.schedule(first)
    queue.schedule(second)

    assert queue.pop_next() is first
    assert queue.pop_next() is second


def test_pop_marks_event_executed() -> None:
    queue = SimulationEventQueue()
    event = make_event(9, 0, 1, "patient_arrival")
    queue.schedule(event)

    popped = queue.pop_next()

    assert popped.status == SimulationEventStatus.EXECUTED


def test_cancelled_event_is_skipped() -> None:
    queue = SimulationEventQueue()
    cancelled = make_event(9, 0, 1, "cancelled")
    valid = make_event(9, 5, 1, "valid")

    queue.schedule(cancelled)
    queue.schedule(valid)
    queue.cancel(cancelled)

    assert queue.pop_next() is valid
    assert queue.is_empty is True


def test_empty_queue_raises_error() -> None:
    queue = SimulationEventQueue()

    with pytest.raises(IndexError):
        queue.pop_next()
