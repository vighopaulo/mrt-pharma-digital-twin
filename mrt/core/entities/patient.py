from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4


@dataclass(slots=True)
class Patient:
    """
    Represents a patient participating in one or more clinical workflows.

    This initial entity stores identity and basic demographic metadata only.
    Appointments, clinical cases, treatment plans, radionuclide administrations,
    movement, queueing, and financial value are introduced in later builds.
    """

    patient_reference: str
    name: str
    date_of_birth: date | None = None
    sex: str | None = None
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.patient_reference = self._normalize_required(
            self.patient_reference,
            "patient_reference",
        )
        self.name = self._normalize_required(self.name, "name")
        self.sex = self._normalize_optional(self.sex, "sex")

        if self.date_of_birth is not None:
            if not isinstance(self.date_of_birth, date):
                raise TypeError("date_of_birth must be a date or None.")
            if self.date_of_birth > date.today():
                raise ValueError("date_of_birth cannot be in the future.")

        if not isinstance(self.is_active, bool):
            raise TypeError("is_active must be a boolean.")

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
    def display_name(self) -> str:
        """Return a concise user-facing patient label."""
        return f"{self.name} [{self.patient_reference}]"

    def age_on(self, reference_date: date) -> int | None:
        """
        Return age in completed years on the supplied date.

        Returns None when no date of birth is available.
        """
        if not isinstance(reference_date, date):
            raise TypeError("reference_date must be a date.")

        if self.date_of_birth is None:
            return None

        if reference_date < self.date_of_birth:
            raise ValueError("reference_date cannot precede date_of_birth.")

        birthday_passed = (
            reference_date.month,
            reference_date.day,
        ) >= (
            self.date_of_birth.month,
            self.date_of_birth.day,
        )

        return (
            reference_date.year
            - self.date_of_birth.year
            - (0 if birthday_passed else 1)
        )

    def activate(self) -> None:
        """Mark the patient record as active."""
        self.is_active = True

    def deactivate(self) -> None:
        """Mark the patient record as inactive."""
        self.is_active = False
