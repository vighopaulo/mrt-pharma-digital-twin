from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from mrt.core.entities.floor import Floor


@dataclass(slots=True)
class Building:
    """Represents a building that owns an ordered collection of floors."""

    name: str
    floors: list[Floor] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("name must be a string.")

        normalized_name = self.name.strip()
        if not normalized_name:
            raise ValueError("name cannot be empty or whitespace.")
        self.name = normalized_name

        initial_floors = list(self.floors)
        self.floors = []
        for floor in initial_floors:
            self.add_floor(floor)

    @property
    def floor_count(self) -> int:
        return len(self.floors)

    def add_floor(self, floor: Floor) -> None:
        if not isinstance(floor, Floor):
            raise TypeError("floor must be a Floor instance.")

        if any(existing.id == floor.id for existing in self.floors):
            raise ValueError("floor is already assigned to this building.")

        if any(existing.level == floor.level for existing in self.floors):
            raise ValueError(
                f"building already contains a floor at level {floor.level}."
            )

        if floor.building_id is not None and floor.building_id != self.id:
            raise ValueError("floor already belongs to another building.")

        floor.building_id = self.id
        self.floors.append(floor)
        self.floors.sort(key=lambda item: item.level)

    def get_floor(self, level: int) -> Floor:
        for floor in self.floors:
            if floor.level == level:
                return floor
        raise KeyError(f"no floor exists at level {level}.")

    def remove_floor(self, level: int) -> Floor:
        floor = self.get_floor(level)
        self.floors.remove(floor)
        floor.building_id = None
        return floor
