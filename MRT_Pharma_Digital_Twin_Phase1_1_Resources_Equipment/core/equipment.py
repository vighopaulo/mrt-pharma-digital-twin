from dataclasses import dataclass, field

from core.exceptions import DomainValidationError
from core.resources import Resource


@dataclass(slots=True)
class Cyclotron(Resource):
    maximum_beam_current_ua: float = 0.0
    production_hours_per_day: float = 0.0
    radionuclide_symbols: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.maximum_beam_current_ua < 0:
            raise DomainValidationError("Beam current cannot be negative.")
        if not 0 <= self.production_hours_per_day <= 24:
            raise DomainValidationError("Production hours must be between 0 and 24.")

    @property
    def is_brand_new_uncommissioned(self) -> bool:
        return self.maximum_beam_current_ua == 0 or self.production_hours_per_day == 0


@dataclass(slots=True)
class Scanner(Resource):
    modality: str = "PET"
    scans_per_hour: float = 1.0
    operating_hours_per_day: float = 8.0
    utilization_target: float = 0.80

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.modality.strip():
            raise DomainValidationError("Scanner modality cannot be empty.")
        if self.scans_per_hour <= 0:
            raise DomainValidationError("Scans per hour must be greater than zero.")
        if not 0 < self.operating_hours_per_day <= 24:
            raise DomainValidationError("Operating hours must be between 0 and 24.")
        if not 0 < self.utilization_target <= 1:
            raise DomainValidationError("Utilization target must be within (0, 1].")

    @property
    def nominal_daily_capacity(self) -> float:
        return (
            self.quantity
            * self.scans_per_hour
            * self.operating_hours_per_day
            * self.utilization_target
        )
