from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(slots=True)
class Room:
    """
    Represents an enclosed clinical, technical, or operational space.

    This initial entity stores identity and descriptive metadata only.
    Geometry, capacity, occupancy, shielding, and equipment assignment
    are introduced in later builds.
    """

    name: str
    room_type: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        normalized_name = self.name.strip()
        if not normalized_name:
            raise ValueError("name cannot be empty or whitespace.")
        self.name = normalized_name

        if self.room_type is not None:
            normalized_type = self.room_type.strip()
            if not normalized_type:
                raise ValueError("room_type cannot be empty or whitespace.")
            self.room_type = normalized_type

    @property
    def display_name(self) -> str:
        """Return a user-facing room label."""
        if self.room_type is None:
            return self.name

        return f"{self.name} ({self.room_type})"
