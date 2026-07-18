from dataclasses import dataclass, field
from uuid import UUID, uuid4
from core.enums import CarrierStatus
from core.exceptions import DomainValidationError

@dataclass(slots=True)
class Carrier:
    name: str
    payload_capacity_kg: float
    unit_cost: float
    status: CarrierStatus = CarrierStatus.AVAILABLE
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip(): raise DomainValidationError("Carrier name cannot be empty.")
        if self.payload_capacity_kg <= 0: raise DomainValidationError("Payload capacity must be greater than zero.")
        if self.unit_cost < 0: raise DomainValidationError("Carrier cost cannot be negative.")
