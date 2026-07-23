"""Section-level similarity score models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SectionSimilarityScore:
    """Explainable comparison result for one signature section."""

    section: str
    score: float
    compared_fields: int
    matched_fields: int
    missing_fields: tuple[str, ...] = ()
    explanations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("Section similarity score must be between 0 and 1.")
        if self.compared_fields < 0 or self.matched_fields < 0:
            raise ValueError("Field counts must not be negative.")
        if self.matched_fields > self.compared_fields:
            raise ValueError("Matched fields cannot exceed compared fields.")

    @property
    def percentage(self) -> float:
        return self.score * 100.0
