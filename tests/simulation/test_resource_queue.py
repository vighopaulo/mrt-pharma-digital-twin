from datetime import datetime, timedelta

import pytest

from mrt.simulation.resource_queue import QueueDiscipline, ResourceQueue


START = datetime(2026, 7, 19, 8, 0)


def test_fifo_queue_preserves_arrival_order() -> None:
    queue = ResourceQueue("PET Scanner Queue")
    first = queue.enqueue("patient-1", START)
    second = queue.enqueue("patient-2", START + timedelta(minutes=1))

    assert queue.dequeue(START + timedelta(minutes=2)) == first
    assert queue.dequeue(START + timedelta(minutes=3)) == second


def test_priority_queue_serves_highest_priority_first() -> None:
    queue = ResourceQueue(
        "Emergency Queue",
        discipline=QueueDiscipline.PRIORITY,
    )
    routine = queue.enqueue("routine", START, priority=5)
    urgent = queue.enqueue("urgent", START + timedelta(seconds=1), priority=1)

    assert queue.dequeue(START + timedelta(minutes=1)) == urgent
    assert queue.dequeue(START + timedelta(minutes=2)) == routine


def test_equal_priority_remains_fifo() -> None:
    queue = ResourceQueue(
        "Dose Queue",
        discipline=QueueDiscipline.PRIORITY,
    )
    first = queue.enqueue("dose-1", START, priority=2)
    second = queue.enqueue("dose-2", START, priority=2)

    assert queue.dequeue(START) == first
    assert queue.dequeue(START) == second


def test_capacity_is_enforced() -> None:
    queue = ResourceQueue("Carrier Queue", capacity=1)
    queue.enqueue("request-1", START)

    with pytest.raises(OverflowError):
        queue.enqueue("request-2", START)


def test_waiting_time_is_calculated() -> None:
    queue = ResourceQueue("Uptake Room Queue")
    entry = queue.enqueue("patient-1", START)

    assert queue.waiting_seconds(
        entry,
        START + timedelta(minutes=7),
    ) == 420.0


def test_maximum_length_is_recorded() -> None:
    queue = ResourceQueue("Scanner Queue")
    queue.enqueue("patient-1", START)
    queue.enqueue("patient-2", START)
    queue.dequeue(START)

    assert queue.maximum_length_observed == 2
