from dataclasses import dataclass
from math import exp, log
from core.exceptions import DomainValidationError

@dataclass(frozen=True, slots=True)
class Radionuclide:
    name: str
    symbol: str
    half_life_minutes: float

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.symbol.strip(): raise DomainValidationError("Name and symbol are required.")
        if self.half_life_minutes <= 0: raise DomainValidationError("Half-life must be greater than zero.")

    @property
    def decay_constant_per_minute(self) -> float:
        return log(2.0) / self.half_life_minutes

    def retained_fraction(self, elapsed_minutes: float) -> float:
        if elapsed_minutes < 0: raise DomainValidationError("Elapsed time cannot be negative.")
        return exp(-self.decay_constant_per_minute * elapsed_minutes)

    def remaining_activity(self, initial_activity: float, elapsed_minutes: float) -> float:
        if initial_activity < 0: raise DomainValidationError("Initial activity cannot be negative.")
        return initial_activity * self.retained_fraction(elapsed_minutes)
