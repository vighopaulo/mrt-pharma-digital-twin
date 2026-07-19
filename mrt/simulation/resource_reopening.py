from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from mrt.simulation.resource_calendar import ResourceCalendar


@dataclass(frozen=True, slots=True)
class ResourceReopening:
    resource_name: str
    reopens_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.resource_name, str):
            raise TypeError("resource_name must be a string.")
        if not self.resource_name.strip():
            raise ValueError("resource_name cannot be empty.")
        if not isinstance(self.reopens_at, datetime):
            raise TypeError("reopens_at must be a datetime.")


def calculate_resource_reopening(
    resource_name: str,
    calendar: ResourceCalendar,
    requested_at: datetime,
    search_days: int = 14,
) -> ResourceReopening | None:
    if not isinstance(calendar, ResourceCalendar):
        raise TypeError("calendar must be a ResourceCalendar.")
    next_time = calendar.next_available_at(
        requested_at,
        search_days=search_days,
    )
    if next_time is None:
        return None
    return ResourceReopening(
        resource_name=resource_name.strip(),
        reopens_at=next_time,
    )
