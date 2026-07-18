from dataclasses import dataclass
from typing import Any

@dataclass
class DecisionConstraint:
    name: str
    value: Any
    constraint_type: str
