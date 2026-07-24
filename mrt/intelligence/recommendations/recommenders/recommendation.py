from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping
from uuid import UUID, uuid4

from .recommendation_category import RecommendationCategory
from .recommendation_priority import RecommendationPriority


@dataclass(frozen=True)
class Recommendation:
    """One explainable, benchmark-supported recommendation."""

    title: str
    description: str
    category: RecommendationCategory
    priority: RecommendationPriority
    confidence: float
    expected_impact: float
    implementation_difficulty: float
    rationale: str

    id: UUID = field(default_factory=uuid4)
    estimated_cost: float | None = None
    implementation_time_days: int | None = None
    supporting_benchmark_ids: tuple[UUID, ...] = ()
    supporting_sources: tuple[str, ...] = ()
    evidence: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Recommendation title must not be empty.")
        if not self.description.strip():
            raise ValueError("Recommendation description must not be empty.")
        for name, value in (
            ("confidence", self.confidence),
            ("expected_impact", self.expected_impact),
            ("implementation_difficulty", self.implementation_difficulty),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1.")

    @property
    def action_score(self) -> float:
        """Prioritize impact and confidence while discounting difficulty."""
        return (
            self.expected_impact
            * self.confidence
            * (1.0 - 0.5 * self.implementation_difficulty)
        )
