from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from mrt.core.entities.radiopharmaceutical_prescription import (
    RadiopharmaceuticalPrescription,
)
from mrt.radiation.entities.radiopharmaceutical_batch import (
    RadiopharmaceuticalBatch,
)


class DoseStatus(StrEnum):
    """Lifecycle states for one dispensed patient dose."""

    DISPENSED = "dispensed"
    RELEASED = "released"
    IN_TRANSIT = "in_transit"
    RECEIVED = "received"
    ADMINISTERED = "administered"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class RadiopharmaceuticalDose:
    """
    Represents one patient-specific dose dispensed from a production batch.

    The dose links a batch to a prescription and records the calibrated activity
    at dispensing. Transport events, assay records, residual activity, and
    exposure calculations are introduced in later builds.
    """

    dose_reference: str
    prescription: RadiopharmaceuticalPrescription
    batch: RadiopharmaceuticalBatch
    dispensed_activity_mbq: float
    dispensed_at: datetime
    status: DoseStatus = DoseStatus.DISPENSED
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.dose_reference = self._normalize_required(
            self.dose_reference,
            "dose_reference",
        )

        if not isinstance(
            self.prescription,
            RadiopharmaceuticalPrescription,
        ):
            raise TypeError(
                "prescription must be a "
                "RadiopharmaceuticalPrescription instance."
            )

        if not isinstance(self.batch, RadiopharmaceuticalBatch):
            raise TypeError(
                "batch must be a RadiopharmaceuticalBatch instance."
            )

        if isinstance(self.dispensed_activity_mbq, bool) or not isinstance(
            self.dispensed_activity_mbq,
            (int, float),
        ):
            raise TypeError("dispensed_activity_mbq must be a number.")

        if self.dispensed_activity_mbq <= 0:
            raise ValueError(
                "dispensed_activity_mbq must be greater than zero."
            )

        self.dispensed_activity_mbq = float(
            self.dispensed_activity_mbq
        )

        if not isinstance(self.dispensed_at, datetime):
            raise TypeError("dispensed_at must be a datetime.")

        if self.dispensed_at < self.batch.calibration_at:
            raise ValueError(
                "dispensed_at cannot precede batch calibration_at."
            )

        if not isinstance(self.status, DoseStatus):
            raise TypeError("status must be a DoseStatus.")

        available_activity = self.batch.activity_at(self.dispensed_at)
        if self.dispensed_activity_mbq > available_activity:
            raise ValueError(
                "dispensed activity cannot exceed batch activity "
                "available at dispensing time."
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
    def prescription_id(self) -> UUID:
        return self.prescription.id

    @property
    def patient_id(self) -> UUID:
        return self.prescription.patient_id

    @property
    def batch_id(self) -> UUID:
        return self.batch.id

    @property
    def display_name(self) -> str:
        return (
            f"Dose {self.dose_reference} — "
            f"{self.prescription.radiopharmaceutical_name} "
            f"{self.dispensed_activity_mbq:g} MBq "
            f"[{self.status.value}]"
        )

    def activity_at(self, at_time: datetime) -> float:
        """Return remaining patient-dose activity in MBq."""
        if not isinstance(at_time, datetime):
            raise TypeError("at_time must be a datetime.")

        if at_time < self.dispensed_at:
            raise ValueError(
                "at_time cannot precede dispensed_at."
            )

        elapsed_minutes = (
            at_time - self.dispensed_at
        ).total_seconds() / 60.0

        return self.batch.radionuclide.remaining_activity_mbq(
            self.dispensed_activity_mbq,
            elapsed_minutes,
        )

    def release(self) -> None:
        if self.status != DoseStatus.DISPENSED:
            raise ValueError("only a dispensed dose can be released.")
        self.status = DoseStatus.RELEASED

    def start_transport(self) -> None:
        if self.status != DoseStatus.RELEASED:
            raise ValueError("only a released dose can enter transit.")
        self.status = DoseStatus.IN_TRANSIT

    def receive(self) -> None:
        if self.status != DoseStatus.IN_TRANSIT:
            raise ValueError("only an in-transit dose can be received.")
        self.status = DoseStatus.RECEIVED

    def administer(self) -> None:
        if self.status != DoseStatus.RECEIVED:
            raise ValueError("only a received dose can be administered.")
        self.status = DoseStatus.ADMINISTERED

    def cancel(self) -> None:
        if self.status == DoseStatus.ADMINISTERED:
            raise ValueError("an administered dose cannot be cancelled.")
        self.status = DoseStatus.CANCELLED
