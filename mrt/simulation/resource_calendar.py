from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import StrEnum


class AvailabilityStatus(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"


@dataclass(frozen=True, slots=True)
class AvailabilityWindow:
    start_at: datetime
    end_at: datetime
    status: AvailabilityStatus = AvailabilityStatus.AVAILABLE
    label: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.start_at, datetime):
            raise TypeError("start_at must be a datetime.")
        if not isinstance(self.end_at, datetime):
            raise TypeError("end_at must be a datetime.")
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be later than start_at.")
        if not isinstance(self.status, AvailabilityStatus):
            raise TypeError("status must be an AvailabilityStatus.")
        if not isinstance(self.label, str):
            raise TypeError("label must be a string.")

    def contains(self, moment: datetime) -> bool:
        if not isinstance(moment, datetime):
            raise TypeError("moment must be a datetime.")
        return self.start_at <= moment < self.end_at


@dataclass(frozen=True, slots=True)
class DailyOperatingWindow:
    start_time: time
    end_time: time

    def __post_init__(self) -> None:
        if not isinstance(self.start_time, time):
            raise TypeError("start_time must be a time.")
        if not isinstance(self.end_time, time):
            raise TypeError("end_time must be a time.")
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time.")

    def contains(self, moment: datetime) -> bool:
        if not isinstance(moment, datetime):
            raise TypeError("moment must be a datetime.")
        return self.start_time <= moment.time() < self.end_time


@dataclass(slots=True)
class ResourceCalendar:
    name: str
    weekly_schedule: dict[int, tuple[DailyOperatingWindow, ...]] = field(
        default_factory=dict
    )
    overrides: list[AvailabilityWindow] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("name must be a string.")
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("name cannot be empty.")

        normalized: dict[int, tuple[DailyOperatingWindow, ...]] = {}
        for weekday, windows in self.weekly_schedule.items():
            if isinstance(weekday, bool) or not isinstance(weekday, int):
                raise TypeError("weekday keys must be integers.")
            if weekday < 0 or weekday > 6:
                raise ValueError("weekday must be between 0 and 6.")
            if not isinstance(windows, tuple):
                raise TypeError("weekly schedule values must be tuples.")
            if not all(isinstance(window, DailyOperatingWindow) for window in windows):
                raise TypeError("all windows must be DailyOperatingWindow.")
            normalized[weekday] = tuple(
                sorted(windows, key=lambda window: window.start_time)
            )
        self.weekly_schedule = normalized

        if not all(isinstance(item, AvailabilityWindow) for item in self.overrides):
            raise TypeError("all overrides must be AvailabilityWindow instances.")

    def add_override(self, window: AvailabilityWindow) -> None:
        if not isinstance(window, AvailabilityWindow):
            raise TypeError("window must be an AvailabilityWindow.")
        self.overrides.append(window)
        self.overrides.sort(key=lambda item: item.start_at)

    def status_at(self, moment: datetime) -> AvailabilityStatus:
        if not isinstance(moment, datetime):
            raise TypeError("moment must be a datetime.")

        matching = [window for window in self.overrides if window.contains(moment)]
        if matching:
            return matching[-1].status

        for window in self.weekly_schedule.get(moment.weekday(), ()):
            if window.contains(moment):
                return AvailabilityStatus.AVAILABLE

        return AvailabilityStatus.UNAVAILABLE

    def is_available(self, moment: datetime) -> bool:
        return self.status_at(moment) == AvailabilityStatus.AVAILABLE

    def has_operating_day(self, day: date) -> bool:
        if not isinstance(day, date):
            raise TypeError("day must be a date.")
        return bool(self.weekly_schedule.get(day.weekday(), ()))

    def next_available_at(
        self,
        moment: datetime,
        search_days: int = 14,
    ) -> datetime | None:
        if not isinstance(moment, datetime):
            raise TypeError("moment must be a datetime.")
        if isinstance(search_days, bool) or not isinstance(search_days, int):
            raise TypeError("search_days must be an integer.")
        if search_days < 0:
            raise ValueError("search_days cannot be negative.")

        if self.is_available(moment):
            return moment

        candidates: list[datetime] = []

        for override in self.overrides:
            if (
                override.status == AvailabilityStatus.AVAILABLE
                and override.end_at > moment
            ):
                candidate = max(moment, override.start_at)
                if self.is_available(candidate):
                    candidates.append(candidate)

        start_day = moment.date()
        for offset in range(search_days + 1):
            current_day = start_day + timedelta(days=offset)
            for window in self.weekly_schedule.get(current_day.weekday(), ()):
                candidate = datetime.combine(current_day, window.start_time)
                if candidate < moment:
                    continue
                if self.is_available(candidate):
                    candidates.append(candidate)

        return min(candidates) if candidates else None
