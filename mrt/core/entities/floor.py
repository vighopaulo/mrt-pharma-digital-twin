from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(slots=True)
class Floor:
    """
    Represents one physical level within a building.

    The entity intentionally contains only identity and basic floor metadata.
    Room allocation, occupancy, geometry, and resource placement are added in
    later builds.
    """

    level: int
    name: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if isinstance(self.level, bool) or not isinstance(self.level, int):
            raise TypeError("level must be an integer.")

        if self.name is not None:
            normalized_name = self.name.strip()
            if not normalized_name:
                raise ValueError("name cannot be empty or whitespace.")
            self.name = normalized_name

    @property
    def display_name(self) -> str:
        """Return the configured name or a deterministic fallback label."""
        if self.name is not None:
            return self.name

        if self.level == 0:
            return "Ground Floor"

        if self.level < 0:
            return f"Basement {abs(self.level)}"

        return f"Floor {self.level}"
