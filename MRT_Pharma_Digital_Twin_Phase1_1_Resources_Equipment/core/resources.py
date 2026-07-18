from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4

from core.exceptions import DomainValidationError


class ResourceStatus(StrEnum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


@dataclass(slots=True)
class Resource:
    name: str
    quantity: int = 1
    status: ResourceStatus = ResourceStatus.AVAILABLE
    unit_capex: float = 0.0
    annual_opex: float = 0.0
    id: UUID = uuid4()

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise DomainValidationError("Resource name cannot be empty.")
        if self.quantity < 1:
            raise DomainValidationError("Resource quantity must be at least one.")
        if self.unit_capex < 0 or self.annual_opex < 0:
            raise DomainValidationError("Resource costs cannot be negative.")

    @property
    def total_capex(self) -> float:
        return self.quantity * self.unit_capex

    @property
    def total_annual_opex(self) -> float:
        return self.quantity * self.annual_opex
