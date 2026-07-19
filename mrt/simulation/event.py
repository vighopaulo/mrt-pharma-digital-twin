from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class SimulationEventStatus(StrEnum):
    """Lifecycle states for a simulation event."""

    SCHEDULED = "scheduled"
    EXECUTED = "executed"
    CANCELLED = "cancelled"


@dataclass(order=True, slots=True)
class SimulationEvent:
    """
    Represents one event scheduled on the simulation timeline.

    Ordering is based first on event time and then on priority. Lower numeric
    priority values execute before higher values when timestamps are equal.
    """

    scheduled_at: datetime
    priority: int
    event_type: str = field(compare=False)
    payload: dict[str, Any] = field(default_factory=dict, compare=False)
    status: SimulationEventStatus = field(
        default=SimulationEventStatus.SCHEDULED,
        compare=False,
    )
    id: UUID = field(default_factory=uuid4, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.scheduled_at, datetime):
            raise TypeError("scheduled_at must be a datetime.")

        if isinstance(self.priority, bool) or not isinstance(self.priority, int):
            raise TypeError("priority must be an integer.")

        if self.priority < 0:
            raise ValueError("priority cannot be negative.")

        if not isinstance(self.event_type, str):
            raise TypeError("event_type must be a string.")

        normalized = self.event_type.strip()
        if not normalized:
            raise ValueError("event_type cannot be empty or whitespace.")
        self.event_type = normalized

        if not isinstance(self.payload, dict):
            raise TypeError("payload must be a dictionary.")

        if not isinstance(self.status, SimulationEventStatus):
            raise TypeError("status must be a SimulationEventStatus.")

    @property
    def display_name(self) -> str:
        return (
            f"{self.event_type} @ {self.scheduled_at.isoformat()} "
            f"[priority={self.priority}, status={self.status.value}]"
        )

    def mark_executed(self) -> None:
        if self.status != SimulationEventStatus.SCHEDULED:
            raise ValueError("only a scheduled event can be executed.")
        self.status = SimulationEventStatus.EXECUTED

    def cancel(self) -> None:
        if self.status == SimulationEventStatus.EXECUTED:
            raise ValueError("an executed event cannot be cancelled.")
        self.status = SimulationEventStatus.CANCELLED
