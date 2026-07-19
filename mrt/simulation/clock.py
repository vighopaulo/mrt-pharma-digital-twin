from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(slots=True)
class SimulationClock:
    """Tracks the current logical time of a simulation run."""

    current_time: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.current_time, datetime):
            raise TypeError("current_time must be a datetime.")

    def advance_to(self, target_time: datetime) -> None:
        if not isinstance(target_time, datetime):
            raise TypeError("target_time must be a datetime.")

        if target_time < self.current_time:
            raise ValueError("simulation clock cannot move backward.")

        self.current_time = target_time

    def advance_by(self, delta: timedelta) -> None:
        if not isinstance(delta, timedelta):
            raise TypeError("delta must be a timedelta.")

        if delta.total_seconds() < 0:
            raise ValueError("simulation clock cannot move backward.")

        self.current_time += delta
