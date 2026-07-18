from dataclasses import dataclass, field
from uuid import UUID, uuid4

from core.equipment import Scanner
from core.exceptions import DomainValidationError
from core.rooms import ClinicalRoom


@dataclass(slots=True)
class ClinicalCell:
    name: str
    scanner: Scanner
    rooms: list[ClinicalRoom] = field(default_factory=list)
    injection_positions: int = 1
    uptake_positions: int = 1
    id: UUID = uuid4()

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise DomainValidationError("Clinical Cell name cannot be empty.")
        if self.injection_positions < 1 or self.uptake_positions < 1:
            raise DomainValidationError(
                "Injection and uptake positions must each be at least one."
            )

    @property
    def nominal_daily_scanner_capacity(self) -> float:
        return self.scanner.nominal_daily_capacity
