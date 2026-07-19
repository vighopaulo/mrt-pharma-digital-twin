from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4

from mrt.core.entities.equipment import Equipment
from mrt.core.entities.room import Room
from mrt.core.entities.staff import Staff


class WorkflowStepStatus(StrEnum):
    """Lifecycle states for one operational workflow step."""

    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class WorkflowStep:
    """
    Represents one ordered operational activity in a clinical workflow.

    A step may optionally reference the room, equipment, and staff member
    required to execute it. Queueing, stochastic duration distributions,
    resource calendars, and simulation-event generation are added later.
    """

    name: str
    sequence: int
    planned_duration_minutes: float
    room: Room | None = None
    equipment: Equipment | None = None
    staff: Staff | None = None
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.name = self._normalize_required(self.name, "name")

        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int):
            raise TypeError("sequence must be an integer.")
        if self.sequence < 1:
            raise ValueError("sequence must be greater than or equal to 1.")

        if isinstance(self.planned_duration_minutes, bool) or not isinstance(
            self.planned_duration_minutes,
            (int, float),
        ):
            raise TypeError(
                "planned_duration_minutes must be a number."
            )
        if self.planned_duration_minutes <= 0:
            raise ValueError(
                "planned_duration_minutes must be greater than zero."
            )
        self.planned_duration_minutes = float(
            self.planned_duration_minutes
        )

        if self.room is not None and not isinstance(self.room, Room):
            raise TypeError("room must be a Room instance or None.")
        if self.equipment is not None and not isinstance(
            self.equipment,
            Equipment,
        ):
            raise TypeError(
                "equipment must be an Equipment instance or None."
            )
        if self.staff is not None and not isinstance(self.staff, Staff):
            raise TypeError("staff must be a Staff instance or None.")

        if not isinstance(self.status, WorkflowStepStatus):
            raise TypeError("status must be a WorkflowStepStatus.")

        if (
            self.room is not None
            and self.equipment is not None
            and self.equipment.room_id is not None
            and self.equipment.room_id != self.room.id
        ):
            raise ValueError(
                "assigned equipment belongs to a different room."
            )

    @staticmethod
    def _normalize_required(value: str, field_name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string.")

        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field_name} cannot be empty or whitespace.")

        return normalized

    @property
    def display_name(self) -> str:
        """Return a concise user-facing workflow-step label."""
        return (
            f"{self.sequence}. {self.name} "
            f"({self.planned_duration_minutes:g} min) "
            f"[{self.status.value}]"
        )

    def mark_ready(self) -> None:
        """Mark a pending step as ready for execution."""
        if self.status != WorkflowStepStatus.PENDING:
            raise ValueError("only a pending step can be marked ready.")
        self.status = WorkflowStepStatus.READY

    def start(self) -> None:
        """Start a ready workflow step."""
        if self.status != WorkflowStepStatus.READY:
            raise ValueError("only a ready step can be started.")
        self.status = WorkflowStepStatus.IN_PROGRESS

    def complete(self) -> None:
        """Complete a workflow step currently in progress."""
        if self.status != WorkflowStepStatus.IN_PROGRESS:
            raise ValueError(
                "only an in-progress step can be completed."
            )
        self.status = WorkflowStepStatus.COMPLETED

    def cancel(self) -> None:
        """Cancel a workflow step that has not completed."""
        if self.status == WorkflowStepStatus.COMPLETED:
            raise ValueError("a completed step cannot be cancelled.")
        self.status = WorkflowStepStatus.CANCELLED
