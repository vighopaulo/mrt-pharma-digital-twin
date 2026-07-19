from datetime import datetime, time, timedelta

import pytest

from mrt.simulation.resource_calendar import (
    AvailabilityStatus,
    AvailabilityWindow,
    DailyOperatingWindow,
    ResourceCalendar,
)


def make_calendar() -> ResourceCalendar:
    window = DailyOperatingWindow(time(8, 0), time(17, 0))
    return ResourceCalendar(
        name="PET Calendar",
        weekly_schedule={
            0: (window,),
            1: (window,),
            2: (window,),
            3: (window,),
            4: (window,),
        },
    )


def test_returns_same_time_when_already_available() -> None:
    monday = datetime(2026, 7, 20, 10, 0)

    assert make_calendar().next_available_at(monday) == monday


def test_returns_next_morning_after_closing() -> None:
    monday_evening = datetime(2026, 7, 20, 18, 0)
    expected = datetime(2026, 7, 21, 8, 0)

    assert make_calendar().next_available_at(monday_evening) == expected


def test_skips_weekend() -> None:
    friday_evening = datetime(2026, 7, 24, 18, 0)
    expected = datetime(2026, 7, 27, 8, 0)

    assert make_calendar().next_available_at(friday_evening) == expected


def test_available_override_can_be_next_opening() -> None:
    calendar = make_calendar()
    sunday = datetime(2026, 7, 19, 7, 0)
    emergency_open = datetime(2026, 7, 19, 9, 0)
    calendar.add_override(
        AvailabilityWindow(
            start_at=emergency_open,
            end_at=emergency_open + timedelta(hours=2),
            status=AvailabilityStatus.AVAILABLE,
        )
    )

    assert calendar.next_available_at(sunday) == emergency_open


def test_returns_none_when_no_opening_found() -> None:
    calendar = ResourceCalendar(name="Closed Resource")

    assert calendar.next_available_at(
        datetime(2026, 7, 19, 8, 0),
        search_days=3,
    ) is None


def test_invalid_search_days_is_rejected() -> None:
    with pytest.raises(ValueError):
        make_calendar().next_available_at(
            datetime(2026, 7, 19, 8, 0),
            search_days=-1,
        )
