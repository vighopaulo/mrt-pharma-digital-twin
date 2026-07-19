from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(slots=True)
class Staff:
    """
    Represents a staff member who can participate in hospital operations.

    This initial entity stores identity and descriptive metadata only.
    Shift schedules, certifications, workload, availability, and radiation
    exposure tracking are introduced in later builds.
    """

    name: str
    role: str
    department: str | None = None
    email: str | None = None
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.name = self._normalize_required(self.name, "name")
        self.role = self._normalize_required(self.role, "role")
        self.department = self._normalize_optional(
            self.department,
            "department",
        )
        self.email = self._normalize_optional(self.email, "email")

        if not isinstance(self.is_active, bool):
            raise TypeError("is_active must be a boolean.")

        if self.email is not None and "@" not in self.email:
            raise ValueError("email must contain '@'.")

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
        """Return a concise user-facing staff label."""
        if self.department is not None:
            return f"{self.name} — {self.role}, {self.department}"

        return f"{self.name} — {self.role}"

    def activate(self) -> None:
        """Mark the staff member as active."""
        self.is_active = True

    def deactivate(self) -> None:
        """Mark the staff member as inactive."""
        self.is_active = False
