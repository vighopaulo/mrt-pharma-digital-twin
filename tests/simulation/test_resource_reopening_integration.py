from datetime import datetime, time

from mrt.simulation.resource_calendar import (
    DailyOperatingWindow,
    ResourceCalendar,
)
from mrt.simulation.resource_dispatcher import ResourceDispatcher
from mrt.simulation.resource_pool import ResourcePool, ResourceUnit
from mrt.simulation.resource_queue import ResourceQueue
from mrt.simulation.resource_reopening import calculate_resource_reopening


def test_waiting_entity_dispatches_at_calculated_reopening() -> None:
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

    requested_at = datetime(2026, 7, 19, 12, 0)
    dispatcher.queue.enqueue("patient-1", requested_at)

    reopening = calculate_resource_reopening(
        "Scanner-1",
        calendar,
        requested_at,
    )
    assert reopening is not None

    assignment = dispatcher.dispatch_one(reopening.reopens_at)

    assert assignment is not None
    assert assignment.queue_entry.entity == "patient-1"
    assert assignment.assigned_at == datetime(2026, 7, 20, 8, 0)
