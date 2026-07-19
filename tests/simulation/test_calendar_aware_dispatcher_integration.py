from datetime import datetime, time

from mrt.simulation.resource_calendar import (
    DailyOperatingWindow,
    ResourceCalendar,
)
from mrt.simulation.resource_dispatcher import ResourceDispatcher
from mrt.simulation.resource_pool import ResourcePool, ResourceUnit
from mrt.simulation.resource_queue import ResourceQueue


def test_waiting_entity_dispatches_when_resource_reopens() -> None:
    calendar = ResourceCalendar(
        name="Scanner Calendar",
        weekly_schedule={
            0: (
                DailyOperatingWindow(
                    start_time=time(8, 0),
                    end_time=time(17, 0),
                ),
            )
        },
    )
    dispatcher = ResourceDispatcher(
        name="Scanner Dispatch",
        queue=ResourceQueue("Scanner Queue"),
        pool=ResourcePool(
            "Scanner Pool",
            [ResourceUnit("Scanner-1")],
        ),
        calendar=calendar,
    )

    monday_closed = datetime(2026, 7, 20, 7, 30)
    monday_open = datetime(2026, 7, 20, 8, 0)

    dispatcher.queue.enqueue("patient-1", monday_closed)

    assert dispatcher.dispatch_one(monday_closed) is None

    assignment = dispatcher.dispatch_one(monday_open)

    assert assignment is not None
    assert assignment.queue_entry.entity == "patient-1"
    assert assignment.waiting_seconds == 1800.0
