"""Configurable section weights for project comparison."""

from __future__ import annotations

from dataclasses import dataclass, fields


@dataclass(frozen=True)
class SimilarityWeights:
    """Relative importance assigned to each ProjectSignature section."""

    spatial: float = 1.0
    workflow: float = 1.0
    resources: float = 1.0
    equipment: float = 1.0
    transport: float = 1.0
    radiation: float = 1.0
    economics: float = 1.0
    metrics: float = 1.0

    def __post_init__(self) -> None:
        values = [getattr(self, item.name) for item in fields(self)]
        if any(value < 0 for value in values):
            raise ValueError("Similarity weights must not be negative.")
        if sum(values) <= 0:
            raise ValueError("At least one similarity weight must be positive.")

    def for_section(self, section: str) -> float:
        if not hasattr(self, section):
            raise KeyError(f"Unknown similarity section: {section}")
        return float(getattr(self, section))
