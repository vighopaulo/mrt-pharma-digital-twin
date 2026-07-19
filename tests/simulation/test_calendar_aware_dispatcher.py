from datetime import datetime, time, timedelta

from mrt.simulation.resource_calendar import (
    AvailabilityStatus,
    AvailabilityWindow,
    DailyOperatingWindow,
    ResourceCalendar,
)
from mrt.simulation.resource_dispatcher import ResourceDispatcher
from mrt.simulation.resource_pool import ResourcePool, ResourceUnit
from mrt.simulation.resource_queue import ResourceQueue


def make_dispatcher() -> ResourceDispatcher:
    calendar = ResourceCalendar(
        name="PET Calendar",
        weekly_schedule={
            0: (
                DailyOperatingWindow(
                    start_time=time(8, 0),
                    end_time=time(17, 0),
                ),
            )
        },
    )
    return ResourceDispatcher(
        name="PET Dispatch",
        queue=ResourceQueue("PET Queue"),
        pool=ResourcePool(
            "PET Pool",
            [ResourceUnit("PET-1")],
        ),
        calendar=calendar,
    )


def test_dispatch_allowed_during_operating_hours() -> None:
    dispatcher = make_dispatcher()
    monday = datetime(2026, 7, 20, 9, 0)
    dispatcher.queue.enqueue("patient-1", monday)

    assignment = dispatcher.dispatch_one(monday)

    assert assignment is not None
    assert assignment.queue_entry.entity == "patient-1"


def test_dispatch_blocked_after_hours() -> None:
    dispatcher = make_dispatcher()
    monday_evening = datetime(2026, 7, 20, 18, 0)
    dispatcher.queue.enqueue("patient-1", monday_evening)

    assignment = dispatcher.dispatch_one(monday_evening)

    assert assignment is None
    assert dispatcher.queue.length == 1
    assert dispatcher.pool.available_count == 1


def test_dispatch_blocked_during_maintenance() -> None:
    dispatcher = make_dispatcher()
    monday = datetime(2026, 7, 20, 10, 0)
    dispatcher.calendar.add_override(
        AvailabilityWindow(
            start_at=monday,
            end_at=monday + timedelta(hours=2),
            status=AvailabilityStatus.MAINTENANCE,
        )
    )
    dispatcher.queue.enqueue("patient-1", monday)

    assignment = dispatcher.dispatch_one(
        monday + timedelta(minutes=30)
    )

    assert assignment is None
    assert dispatcher.queue.length == 1


def test_release_does_not_dispatch_when_calendar_closed() -> None:
    dispatcher = make_dispatcher()
    monday = datetime(2026, 7, 20, 9, 0)
    dispatcher.queue.enqueue("patient-1", monday)
    first = dispatcher.dispatch_one(monday)
    assert first is not None

    closed = datetime(2026, 7, 20, 18, 0)
    dispatcher.queue.enqueue("patient-2", closed)

    second = dispatcher.release_and_dispatch(
        first.resource_unit,
        closed,
    )

    assert second is None
    assert dispatcher.pool.available_count == 1
    assert dispatcher.queue.length == 1
