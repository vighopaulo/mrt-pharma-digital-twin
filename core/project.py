from dataclasses import dataclass, field
from uuid import UUID, uuid4
from core.decision_constraints import DecisionConstraint
from core.exceptions import DomainValidationError
from core.hospital import Hospital
from core.mrt_network import MRTNetwork

@dataclass(slots=True)
class Project:
    name: str
    hospital: Hospital
    mrt_network: MRTNetwork | None = None
    constraints: list[DecisionConstraint] = field(default_factory=list)
    description: str = ""
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip(): raise DomainValidationError("Project name cannot be empty.")

    def add_constraint(self, constraint: DecisionConstraint) -> None:
        if any(x.name == constraint.name for x in self.constraints): raise DomainValidationError(f"Constraint '{constraint.name}' already exists.")
        self.constraints.append(constraint)
