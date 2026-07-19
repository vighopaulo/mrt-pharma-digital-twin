from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from mrt.core.entities.room import Room


@dataclass(slots=True)
class Floor:
    """Represents one physical level within a building."""

    level: int
    name: str | None = None
    rooms: list[Room] = field(default_factory=list)
    building_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if isinstance(self.level, bool) or not isinstance(self.level, int):
            raise TypeError("level must be an integer.")

        if self.name is not None:
            if not isinstance(self.name, str):
                raise TypeError("name must be a string or None.")
            normalized_name = self.name.strip()
            if not normalized_name:
                raise ValueError("name cannot be empty or whitespace.")
            self.name = normalized_name

        initial_rooms = list(self.rooms)
        self.rooms = []
        for room in initial_rooms:
            self.add_room(room)

    @property
    def display_name(self) -> str:
        if self.name is not None:
            return self.name
        if self.level == 0:
            return "Ground Floor"
        if self.level < 0:
            return f"Basement {abs(self.level)}"
        return f"Floor {self.level}"

    @property
    def room_count(self) -> int:
        return len(self.rooms)

    def add_room(self, room: Room) -> None:
        if not isinstance(room, Room):
            raise TypeError("room must be a Room instance.")

        if any(existing.id == room.id for existing in self.rooms):
            raise ValueError("room is already assigned to this floor.")

        if any(existing.name.casefold() == room.name.casefold() for existing in self.rooms):
            raise ValueError(f"floor already contains a room named {room.name!r}.")

        if room.floor_id is not None and room.floor_id != self.id:
            raise ValueError("room already belongs to another floor.")

        room.floor_id = self.id
        self.rooms.append(room)

    def get_room(self, name: str) -> Room:
        normalized = name.strip().casefold()
        for room in self.rooms:
            if room.name.casefold() == normalized:
                return room
        raise KeyError(f"no room named {name!r} exists on this floor.")

    def remove_room(self, name: str) -> Room:
        room = self.get_room(name)
        self.rooms.remove(room)
        room.floor_id = None
        return room
