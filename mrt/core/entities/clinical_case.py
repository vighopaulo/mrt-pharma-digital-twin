from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from mrt.core.entities.patient import Patient
from mrt.core.entities.treatment_plan import TreatmentPlan


class ClinicalCaseOrigin(StrEnum):
    """How the clinical case entered the modeled facility."""

    INBOUND = "inbound"
    INTERNAL = "internal"
    OUTBOUND = "outbound"


class ClinicalCaseStatus(StrEnum):
    """Initial lifecycle states for a clinical case."""

    CREATED = "created"
    ADMITTED = "admitted"
    IN_TREATMENT = "in_treatment"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class ClinicalCase:
    """
    Represents one operational episode of care for a patient.

    The case links a patient to a treatment plan and records how the case
    entered the modeled system. Financial value, accommodation class,
    payer rules, resource reservations, and detailed workflow events are
    introduced in later builds.
    """

    patient: Patient
    treatment_plan: TreatmentPlan
    origin: ClinicalCaseOrigin
    created_at: datetime = field(default_factory=datetime.now)
    external_reference: str | None = None
    status: ClinicalCaseStatus = ClinicalCaseStatus.CREATED
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.patient, Patient):
            raise TypeError("patient must be a Patient instance.")

        if not isinstance(self.treatment_plan, TreatmentPlan):
            raise TypeError(
                "treatment_plan must be a TreatmentPlan instance."
            )

        if self.treatment_plan.patient_id != self.patient.id:
            raise ValueError(
                "treatment_plan must belong to the same patient."
            )

        if not isinstance(self.origin, ClinicalCaseOrigin):
            raise TypeError("origin must be a ClinicalCaseOrigin.")

        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime.")

        if not isinstance(self.status, ClinicalCaseStatus):
            raise TypeError("status must be a ClinicalCaseStatus.")

        if self.external_reference is not None:
            if not isinstance(self.external_reference, str):
                raise TypeError(
                    "external_reference must be a string or None."
                )

            normalized = self.external_reference.strip()
            if not normalized:
                raise ValueError(
                    "external_reference cannot be empty or whitespace."
                )
            self.external_reference = normalized

    @property
    def patient_id(self) -> UUID:
        return self.patient.id

    @property
    def treatment_plan_id(self) -> UUID:
        return self.treatment_plan.id

    @property
    def display_name(self) -> str:
        return (
            f"{self.patient.display_name} — "
            f"{self.treatment_plan.treatment_name} "
            f"[{self.origin.value}/{self.status.value}]"
        )

    def admit(self) -> None:
        """Admit a newly created case into the modeled facility."""
        if self.status != ClinicalCaseStatus.CREATED:
            raise ValueError("only a created case can be admitted.")

        self.status = ClinicalCaseStatus.ADMITTED

    def start_treatment(self) -> None:
        """Start treatment for an admitted case."""
        if self.status != ClinicalCaseStatus.ADMITTED:
            raise ValueError("only an admitted case can start treatment.")

        self.status = ClinicalCaseStatus.IN_TREATMENT

    def complete(self) -> None:
        """Complete a case that is currently in treatment."""
        if self.status != ClinicalCaseStatus.IN_TREATMENT:
            raise ValueError(
                "only an in-treatment case can be completed."
            )

        self.status = ClinicalCaseStatus.COMPLETED

    def cancel(self) -> None:
        """Cancel a case that has not already completed."""
        if self.status == ClinicalCaseStatus.COMPLETED:
            raise ValueError("a completed case cannot be cancelled.")

        self.status = ClinicalCaseStatus.CANCELLED
