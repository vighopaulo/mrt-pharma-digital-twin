from datetime import datetime, timedelta

from mrt.simulation.resource_dispatcher import ResourceDispatcher
from mrt.simulation.resource_pool import ResourcePool, ResourceUnit
from mrt.simulation.resource_queue import ResourceQueue

def test_release_immediately_dispatches_next_waiting_entity() -> None:
    start = datetime(2026, 7, 19, 8, 0)
    dispatcher = ResourceDispatcher(
        name="Scanner Dispatch",
        queue=ResourceQueue("Scanner Queue"),
        pool=ResourcePool("Scanner Pool", [ResourceUnit("Scanner-1")]),
    )
    dispatcher.queue.enqueue("patient-1", start)
    dispatcher.queue.enqueue("patient-2", start + timedelta(minutes=2))
    first = dispatcher.dispatch_one(start)
    assert first is not None
    second = dispatcher.release_and_dispatch(
        first.resource_unit,
        start + timedelta(minutes=12),
    )
    assert second is not None
    assert second.queue_entry.entity == "patient-2"
    assert second.resource_unit.name == "Scanner-1"
    assert second.waiting_seconds == 600.0
    assert dispatcher.queue.is_empty is True
