from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from mrt.core.entities.patient import Patient


class TreatmentPlanStatus(StrEnum):
    """Supported lifecycle states for an initial treatment plan."""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class TreatmentPlan:
    """
    Represents a clinical plan created for a patient.

    This initial entity stores identity, patient linkage, scheduling metadata,
    lifecycle status, and notes. Procedure steps, radionuclide prescription,
    resource assignment, workflow execution, and financial value are added in
    later builds.
    """

    patient: Patient
    treatment_name: str
    scheduled_at: datetime | None = None
    notes: str | None = None
    status: TreatmentPlanStatus = TreatmentPlanStatus.DRAFT
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.patient, Patient):
            raise TypeError("patient must be a Patient instance.")

        self.treatment_name = self._normalize_required(
            self.treatment_name,
            "treatment_name",
        )
        self.notes = self._normalize_optional(self.notes, "notes")

        if self.scheduled_at is not None and not isinstance(
            self.scheduled_at,
            datetime,
        ):
            raise TypeError("scheduled_at must be a datetime or None.")

        if not isinstance(self.status, TreatmentPlanStatus):
            raise TypeError("status must be a TreatmentPlanStatus.")

        if (
            self.status == TreatmentPlanStatus.SCHEDULED
            and self.scheduled_at is None
        ):
            raise ValueError(
                "scheduled_at is required when status is scheduled."
            )

    @staticmethod
    def _normalize_required(value: str, field_name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string.")

        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field_name} cannot be empty or whitespace.")

        return normalized

    @staticmethod
    def _normalize_optional(
        value: str | None,
        field_name: str,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string or None.")

        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field_name} cannot be empty or whitespace.")

        return normalized

    @property
    def patient_id(self) -> UUID:
        """Return the linked patient's stable identifier."""
        return self.patient.id

    @property
    def display_name(self) -> str:
        """Return a concise user-facing treatment-plan label."""
        return (
            f"{self.treatment_name} — "
            f"{self.patient.display_name} "
            f"[{self.status.value}]"
        )

    def schedule(self, scheduled_at: datetime) -> None:
        """Schedule the plan for a specific date and time."""
        if not isinstance(scheduled_at, datetime):
            raise TypeError("scheduled_at must be a datetime.")

        if self.status in {
            TreatmentPlanStatus.COMPLETED,
            TreatmentPlanStatus.CANCELLED,
        }:
            raise ValueError(
                "a completed or cancelled treatment plan cannot be scheduled."
            )

        self.scheduled_at = scheduled_at
        self.status = TreatmentPlanStatus.SCHEDULED

    def start(self) -> None:
        """Mark a scheduled treatment plan as in progress."""
        if self.status != TreatmentPlanStatus.SCHEDULED:
            raise ValueError(
                "only a scheduled treatment plan can be started."
            )

        self.status = TreatmentPlanStatus.IN_PROGRESS

    def complete(self) -> None:
        """Mark an in-progress treatment plan as completed."""
        if self.status != TreatmentPlanStatus.IN_PROGRESS:
            raise ValueError(
                "only an in-progress treatment plan can be completed."
            )

        self.status = TreatmentPlanStatus.COMPLETED

    def cancel(self) -> None:
        """Cancel a treatment plan that has not been completed."""
        if self.status == TreatmentPlanStatus.COMPLETED:
            raise ValueError("a completed treatment plan cannot be cancelled.")

        self.status = TreatmentPlanStatus.CANCELLED
