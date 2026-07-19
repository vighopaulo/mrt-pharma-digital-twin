from datetime import datetime, timedelta

import pytest

from mrt.simulation.resource_dispatcher import ResourceDispatcher
from mrt.simulation.resource_pool import ResourcePool, ResourceUnit
from mrt.simulation.resource_queue import ResourceQueue

START = datetime(2026, 7, 19, 8, 0)

def make_dispatcher() -> ResourceDispatcher:
    return ResourceDispatcher(
        name="PET Dispatch",
        queue=ResourceQueue("PET Queue"),
        pool=ResourcePool(
            "PET Scanner Pool",
            [ResourceUnit("PET-1"), ResourceUnit("PET-2")],
        ),
    )

def test_dispatch_one_assigns_first_waiting_entity() -> None:
    dispatcher = make_dispatcher()
    dispatcher.queue.enqueue("patient-1", START)
    assignment = dispatcher.dispatch_one(START + timedelta(minutes=5))
    assert assignment is not None
    assert assignment.queue_entry.entity == "patient-1"
    assert assignment.resource_unit.name == "PET-1"
    assert assignment.waiting_seconds == 300.0

def test_dispatch_available_uses_all_available_resources() -> None:
    dispatcher = make_dispatcher()
    dispatcher.queue.enqueue("patient-1", START)
    dispatcher.queue.enqueue("patient-2", START)
    dispatcher.queue.enqueue("patient-3", START)
    assignments = dispatcher.dispatch_available(START + timedelta(minutes=1))
    assert len(assignments) == 2
    assert dispatcher.pool.allocated_count == 2
    assert dispatcher.queue.length == 1

def test_dispatch_returns_none_without_waiting_entity() -> None:
    assert make_dispatcher().dispatch_one(START) is None

def test_dispatch_returns_none_when_pool_exhausted() -> None:
    dispatcher = make_dispatcher()
    dispatcher.pool.acquire()
    dispatcher.pool.acquire()
    dispatcher.queue.enqueue("patient-1", START)
    assert dispatcher.dispatch_one(START) is None

def test_assignment_lookup_by_entity() -> None:
    dispatcher = make_dispatcher()
    dispatcher.queue.enqueue("patient-1", START)
    dispatcher.dispatch_one(START)
    assert dispatcher.assignment_for_entity("patient-1").queue_entry.entity == "patient-1"

def test_missing_assignment_lookup_raises() -> None:
    with pytest.raises(KeyError):
        make_dispatcher().assignment_for_entity("unknown")
