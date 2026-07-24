from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from .recommendation import Recommendation


@dataclass(frozen=True)
class RecommendationResult:
    """Ranked recommendation output for one reference project."""

    project_id: UUID | None
    recommendations: tuple[Recommendation, ...]
    benchmark_count: int
    explanation: str

    @property
    def count(self) -> int:
        return len(self.recommendations)

    def by_priority(self) -> tuple[Recommendation, ...]:
        return tuple(
            sorted(
                self.recommendations,
                key=lambda item: (int(item.priority), item.action_score),
                reverse=True,
            )
        )
