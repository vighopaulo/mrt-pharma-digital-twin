"""Collections of traceable evidence."""
from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID
from .confidence import ConfidenceAssessment
from .evidence import Evidence, EvidenceSourceType

@dataclass
class EvidenceCollection:
    items: list[Evidence] = field(default_factory=list)

    def __post_init__(self) -> None:
        ids = [item.id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("EvidenceCollection contains duplicate evidence IDs.")

    def add(self, evidence: Evidence) -> None:
        if self.get(evidence.id) is not None:
            raise ValueError(f"Evidence {evidence.id} already exists.")
        self.items.append(evidence)

    def remove(self, evidence_id: UUID) -> Evidence:
        for index, item in enumerate(self.items):
            if item.id == evidence_id:
                return self.items.pop(index)
        raise KeyError(f"Evidence {evidence_id} was not found.")

    def get(self, evidence_id: UUID) -> Evidence | None:
        return next((item for item in self.items if item.id == evidence_id), None)

    def by_source_type(self, source_type: EvidenceSourceType) -> tuple[Evidence, ...]:
        return tuple(item for item in self.items if item.source_type == source_type)

    @property
    def count(self) -> int:
        return len(self.items)

    def confidence(self) -> ConfidenceAssessment:
        if not self.items:
            return ConfidenceAssessment(0.0, "No evidence has been collected.", 0)
        score = sum(item.weighted_score for item in self.items) / len(self.items)
        return ConfidenceAssessment(
            score,
            "Arithmetic mean of each evidence item's reliability and relevance product.",
            len(self.items),
        )

    def snapshot(self) -> tuple[Evidence, ...]:
        return tuple(self.items)
