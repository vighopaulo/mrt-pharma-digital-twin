"""Confidence assessment primitives."""
from dataclasses import dataclass
from enum import Enum

class ConfidenceLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass(frozen=True)
class ConfidenceAssessment:
    score: float
    rationale: str = ""
    evidence_count: int = 0

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0.")
        if self.evidence_count < 0:
            raise ValueError("Evidence count must not be negative.")

    @property
    def level(self) -> ConfidenceLevel:
        if self.score < 0.20:
            return ConfidenceLevel.VERY_LOW
        if self.score < 0.40:
            return ConfidenceLevel.LOW
        if self.score < 0.60:
            return ConfidenceLevel.MODERATE
        if self.score < 0.80:
            return ConfidenceLevel.HIGH
        return ConfidenceLevel.VERY_HIGH
