from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from mrt.core.entities.equipment import Equipment


@dataclass(slots=True)
class Room:
    """Represents an enclosed space that owns installed equipment."""

    name: str
    room_type: str | None = None
    equipment: list[Equipment] = field(default_factory=list)
    floor_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.name = self._normalize_required(self.name, "name")
        self.room_type = self._normalize_optional(self.room_type, "room_type")

        initial_equipment = list(self.equipment)
        self.equipment = []
        for item in initial_equipment:
            self.add_equipment(item)

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
        if self.room_type is None:
            return self.name
        return f"{self.name} ({self.room_type})"

    @property
    def equipment_count(self) -> int:
        return len(self.equipment)

    def add_equipment(self, item: Equipment) -> None:
        if not isinstance(item, Equipment):
            raise TypeError("item must be an Equipment instance.")

        if any(existing.id == item.id for existing in self.equipment):
            raise ValueError("equipment is already assigned to this room.")

        if any(existing.name.casefold() == item.name.casefold() for existing in self.equipment):
            raise ValueError(
                f"room already contains equipment named {item.name!r}."
            )

        if item.room_id is not None and item.room_id != self.id:
            raise ValueError("equipment already belongs to another room.")

        item.room_id = self.id
        self.equipment.append(item)

    def get_equipment(self, name: str) -> Equipment:
        normalized = name.strip().casefold()
        for item in self.equipment:
            if item.name.casefold() == normalized:
                return item
        raise KeyError(f"no equipment named {name!r} exists in this room.")

    def remove_equipment(self, name: str) -> Equipment:
        item = self.get_equipment(name)
        self.equipment.remove(item)
        item.room_id = None
        return item
