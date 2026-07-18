from dataclasses import dataclass
from core.enums import ConstraintSense
from core.exceptions import DomainValidationError

@dataclass(frozen=True, slots=True)
class DecisionConstraint:
    name: str
    sense: ConstraintSense
    value: float
    unit: str

    def __post_init__(self) -> None:
        if not self.name.strip(): raise DomainValidationError("Constraint name cannot be empty.")
        if not self.unit.strip(): raise DomainValidationError("Constraint unit cannot be empty.")

    def is_satisfied(self, observed_value: float, tolerance: float = 1e-9) -> bool:
        if self.sense is ConstraintSense.MAXIMUM: return observed_value <= self.value + tolerance
        if self.sense is ConstraintSense.MINIMUM: return observed_value >= self.value - tolerance
        return abs(observed_value - self.value) <= tolerance
