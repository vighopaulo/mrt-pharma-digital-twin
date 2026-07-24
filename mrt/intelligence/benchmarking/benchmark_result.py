from __future__ import annotations

from dataclasses import dataclass

from ..similarity import SimilarityResult
from .benchmark_project import BenchmarkProject


@dataclass(frozen=True)
class BenchmarkResult:
    """One ranked benchmark match."""

    rank: int
    project: BenchmarkProject
    similarity: SimilarityResult

    @property
    def score(self) -> float:
        return self.similarity.overall_score

    @property
    def percentage(self) -> float:
        return self.similarity.percentage

    @property
    def display_url(self) -> str | None:
        """Link used by a later result-display layer."""
        return self.project.profile_url or self.project.source_url
