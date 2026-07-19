from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(slots=True)
class Equipment:
    """Represents a physical equipment instance installed in a room."""

    name: str
    equipment_type: str
    manufacturer: str | None = None
    model: str | None = None
    is_active: bool = True
    room_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.name = self._normalize_required(self.name, "name")
        self.equipment_type = self._normalize_required(
            self.equipment_type,
            "equipment_type",
        )
        self.manufacturer = self._normalize_optional(
            self.manufacturer,
            "manufacturer",
        )
        self.model = self._normalize_optional(self.model, "model")

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
    def _normalize_optional(value: str | None, field_name: str) -> str | None:
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
        details = [self.manufacturer, self.model]
        specification = " ".join(part for part in details if part)
        if specification:
            return f"{self.name} ({specification})"
        return self.name

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False
