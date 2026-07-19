from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class Building:
    name: str
    floors: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))

    def add_floor(self, floor_name: str) -> None:
        if floor_name not in self.floors:
            self.floors.append(floor_name)

    @property
    def floor_count(self) -> int:
        return len(self.floors)
