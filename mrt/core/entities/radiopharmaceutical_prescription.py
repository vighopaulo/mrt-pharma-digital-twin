from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from mrt.core.entities.treatment_plan import TreatmentPlan


class PrescriptionStatus(StrEnum):
    """Lifecycle states for a radiopharmaceutical prescription."""

    DRAFT = "draft"
    APPROVED = "approved"
    PREPARED = "prepared"
    ADMINISTERED = "administered"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class RadiopharmaceuticalPrescription:
    """
    Represents a prescribed radiopharmaceutical activity for a treatment plan.

    This initial entity records the prescribed product, activity, calibration
    time, administration route, and lifecycle state. Physical decay, production
    batches, dispensing, transport, assay results, and residual activity are
    introduced in later builds.
    """

    treatment_plan: TreatmentPlan
    radiopharmaceutical_name: str
    activity_mbq: float
    calibration_at: datetime
    administration_route: str = "intravenous"
    notes: str | None = None
    status: PrescriptionStatus = PrescriptionStatus.DRAFT
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.treatment_plan, TreatmentPlan):
            raise TypeError(
                "treatment_plan must be a TreatmentPlan instance."
            )

        self.radiopharmaceutical_name = self._normalize_required(
            self.radiopharmaceutical_name,
            "radiopharmaceutical_name",
        )
        self.administration_route = self._normalize_required(
            self.administration_route,
            "administration_route",
        )
        self.notes = self._normalize_optional(self.notes, "notes")

        if isinstance(self.activity_mbq, bool) or not isinstance(
            self.activity_mbq,
            (int, float),
        ):
            raise TypeError("activity_mbq must be a number.")
        if self.activity_mbq <= 0:
            raise ValueError("activity_mbq must be greater than zero.")
        self.activity_mbq = float(self.activity_mbq)

        if not isinstance(self.calibration_at, datetime):
            raise TypeError("calibration_at must be a datetime.")

        if not isinstance(self.status, PrescriptionStatus):
            raise TypeError("status must be a PrescriptionStatus.")

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
    def treatment_plan_id(self) -> UUID:
        return self.treatment_plan.id

    @property
    def patient_id(self) -> UUID:
        return self.treatment_plan.patient_id

    @property
    def activity_gbq(self) -> float:
        """Return prescribed activity in gigabecquerels."""
        return self.activity_mbq / 1000.0

    @property
    def display_name(self) -> str:
        return (
            f"{self.radiopharmaceutical_name} "
            f"{self.activity_mbq:g} MBq — "
            f"{self.treatment_plan.patient.display_name} "
            f"[{self.status.value}]"
        )

    def approve(self) -> None:
        """Approve a draft prescription."""
        if self.status != PrescriptionStatus.DRAFT:
            raise ValueError("only a draft prescription can be approved.")
        self.status = PrescriptionStatus.APPROVED

    def mark_prepared(self) -> None:
        """Mark an approved prescription as prepared."""
        if self.status != PrescriptionStatus.APPROVED:
            raise ValueError(
                "only an approved prescription can be marked prepared."
            )
        self.status = PrescriptionStatus.PREPARED

    def mark_administered(self) -> None:
        """Mark a prepared prescription as administered."""
        if self.status != PrescriptionStatus.PREPARED:
            raise ValueError(
                "only a prepared prescription can be administered."
            )
        self.status = PrescriptionStatus.ADMINISTERED

    def cancel(self) -> None:
        """Cancel a prescription that has not been administered."""
        if self.status == PrescriptionStatus.ADMINISTERED:
            raise ValueError(
                "an administered prescription cannot be cancelled."
            )
        self.status = PrescriptionStatus.CANCELLED
