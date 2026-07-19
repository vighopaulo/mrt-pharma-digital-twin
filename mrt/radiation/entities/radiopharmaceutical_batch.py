from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from mrt.radiation.entities.radionuclide import Radionuclide


class BatchStatus(StrEnum):
    """Lifecycle states for one radiopharmaceutical production batch."""

    CREATED = "created"
    RELEASED = "released"
    DEPLETED = "depleted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class RadiopharmaceuticalBatch:
    """
    Represents one produced batch of radiopharmaceutical activity.

    The batch links a product name to a radionuclide and a calibrated activity.
    Dose dispensing, quality-control records, transport assignments, and
    patient-level administrations are introduced in later builds.
    """

    batch_number: str
    product_name: str
    radionuclide: Radionuclide
    initial_activity_mbq: float
    calibration_at: datetime
    produced_at: datetime
    expiration_at: datetime | None = None
    status: BatchStatus = BatchStatus.CREATED
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.batch_number = self._normalize_required(
            self.batch_number,
            "batch_number",
        )
        self.product_name = self._normalize_required(
            self.product_name,
            "product_name",
        )

        if not isinstance(self.radionuclide, Radionuclide):
            raise TypeError("radionuclide must be a Radionuclide instance.")

        if isinstance(self.initial_activity_mbq, bool) or not isinstance(
            self.initial_activity_mbq,
            (int, float),
        ):
            raise TypeError("initial_activity_mbq must be a number.")
        if self.initial_activity_mbq <= 0:
            raise ValueError(
                "initial_activity_mbq must be greater than zero."
            )
        self.initial_activity_mbq = float(self.initial_activity_mbq)

        if not isinstance(self.calibration_at, datetime):
            raise TypeError("calibration_at must be a datetime.")
        if not isinstance(self.produced_at, datetime):
            raise TypeError("produced_at must be a datetime.")
        if self.produced_at > self.calibration_at:
            raise ValueError(
                "produced_at cannot occur after calibration_at."
            )

        if self.expiration_at is not None:
            if not isinstance(self.expiration_at, datetime):
                raise TypeError("expiration_at must be a datetime or None.")
            if self.expiration_at <= self.produced_at:
                raise ValueError(
                    "expiration_at must occur after produced_at."
                )

        if not isinstance(self.status, BatchStatus):
            raise TypeError("status must be a BatchStatus.")

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
        return (
            f"{self.product_name} — Batch {self.batch_number} "
            f"[{self.status.value}]"
        )

    def activity_at(self, at_time: datetime) -> float:
        """Return calculated activity in MBq at a requested time."""
        if not isinstance(at_time, datetime):
            raise TypeError("at_time must be a datetime.")
        if at_time < self.calibration_at:
            raise ValueError(
                "at_time cannot precede calibration_at."
            )

        elapsed_minutes = (
            at_time - self.calibration_at
        ).total_seconds() / 60.0

        return self.radionuclide.remaining_activity_mbq(
            self.initial_activity_mbq,
            elapsed_minutes,
        )

    def remaining_fraction_at(self, at_time: datetime) -> float:
        """Return the fraction of calibrated activity remaining."""
        return self.activity_at(at_time) / self.initial_activity_mbq

    def is_expired_at(self, at_time: datetime) -> bool:
        """Return whether the batch has passed its explicit expiry time."""
        if not isinstance(at_time, datetime):
            raise TypeError("at_time must be a datetime.")

        return (
            self.expiration_at is not None
            and at_time >= self.expiration_at
        )

    def release(self) -> None:
        """Release a newly created batch for operational use."""
        if self.status != BatchStatus.CREATED:
            raise ValueError("only a created batch can be released.")
        self.status = BatchStatus.RELEASED

    def mark_depleted(self) -> None:
        """Mark a released batch as depleted."""
        if self.status != BatchStatus.RELEASED:
            raise ValueError("only a released batch can be depleted.")
        self.status = BatchStatus.DEPLETED

    def mark_expired(self) -> None:
        """Mark a nonterminal batch as expired."""
        if self.status in {
            BatchStatus.DEPLETED,
            BatchStatus.CANCELLED,
        }:
            raise ValueError(
                "a depleted or cancelled batch cannot be marked expired."
            )
        self.status = BatchStatus.EXPIRED

    def cancel(self) -> None:
        """Cancel a batch that has not been depleted or expired."""
        if self.status in {
            BatchStatus.DEPLETED,
            BatchStatus.EXPIRED,
        }:
            raise ValueError(
                "a depleted or expired batch cannot be cancelled."
            )
        self.status = BatchStatus.CANCELLED
