"""Aggregate similarity result models."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from .similarity_score import SectionSimilarityScore


@dataclass(frozen=True)
class SimilarityResult:
    """Explainable weighted similarity between two projects."""

    reference_project_id: UUID | None
    candidate_project_id: UUID | None
    overall_score: float
    section_scores: tuple[SectionSimilarityScore, ...]
    explanation: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.overall_score <= 1.0:
            raise ValueError("Overall similarity score must be between 0 and 1.")

    @property
    def percentage(self) -> float:
        return self.overall_score * 100.0

    def score_for(self, section: str) -> SectionSimilarityScore | None:
        return next(
            (score for score in self.section_scores if score.section == section),
            None,
        )
