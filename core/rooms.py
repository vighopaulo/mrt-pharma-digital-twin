from dataclasses import dataclass, field
from uuid import UUID, uuid4
from core.enums import RoomType
from core.exceptions import DomainValidationError

@dataclass(slots=True)
class ClinicalRoom:
    name: str
    room_type: RoomType
    floor: int
    area_m2: float
    node_id: UUID | None = None
    existing: bool = True
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip(): raise DomainValidationError("Room name cannot be empty.")
        if self.area_m2 <= 0: raise DomainValidationError("Room area must be greater than zero.")
