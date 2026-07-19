from datetime import datetime, time

from mrt.simulation.resource_calendar import (
    DailyOperatingWindow,
    ResourceCalendar,
)
from mrt.simulation.resource_reopening import calculate_resource_reopening


def test_calculates_resource_reopening_record() -> None:
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

    requested_at = datetime(2026, 7, 19, 12, 0)
    reopening = calculate_resource_reopening(
        resource_name="PET Scanner",
        calendar=calendar,
        requested_at=requested_at,
    )

    assert reopening is not None
    assert reopening.resource_name == "PET Scanner"
    assert reopening.reopens_at == datetime(2026, 7, 20, 8, 0)


def test_returns_none_without_future_opening() -> None:
    calendar = ResourceCalendar(name="Closed Resource")

    assert calculate_resource_reopening(
        resource_name="Cyclotron",
        calendar=calendar,
        requested_at=datetime(2026, 7, 19, 8, 0),
        search_days=2,
    ) is None
