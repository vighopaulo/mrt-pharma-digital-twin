"""Weighted and explainable ProjectSignature comparison."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from ..project_signature import ProjectSignature
from .comparators import (
    EconomicComparator,
    EquipmentComparator,
    MetricsComparator,
    RadiationComparator,
    ResourceComparator,
    SpatialComparator,
    TransportComparator,
    WorkflowComparator,
)
from .similarity_result import SimilarityResult
from .similarity_weights import SimilarityWeights


class SimilarityEngine:
    """Compare and rank projects using their evidence-backed observations."""

    def __init__(self, weights: SimilarityWeights | None = None) -> None:
        self.weights = weights or SimilarityWeights()
        self._comparators = (
            SpatialComparator(),
            WorkflowComparator(),
            ResourceComparator(),
            EquipmentComparator(),
            TransportComparator(),
            RadiationComparator(),
            EconomicComparator(),
            MetricsComparator(),
        )

    def compare(
        self,
        reference: ProjectSignature,
        candidate: ProjectSignature,
    ) -> SimilarityResult:
        reference_data = self._observations(reference)
        candidate_data = self._observations(candidate)

        section_scores = tuple(
            comparator.compare(
                reference_data.get(comparator.section_name, {}),
                candidate_data.get(comparator.section_name, {}),
            )
            for comparator in self._comparators
        )

        weighted_total = 0.0
        active_weight = 0.0
        for section_score in section_scores:
            if section_score.compared_fields == 0:
                continue
            weight = self.weights.for_section(section_score.section)
            weighted_total += section_score.score * weight
            active_weight += weight

        overall = weighted_total / active_weight if active_weight else 0.0
        comparable_sections = sum(
            score.compared_fields > 0 for score in section_scores
        )

        explanation = (
            f"Compared {comparable_sections} of 8 signature sections. "
            f"Weighted overall similarity is {overall * 100.0:.1f}%."
        )

        return SimilarityResult(
            reference_project_id=reference.project_id,
            candidate_project_id=candidate.project_id,
            overall_score=overall,
            section_scores=section_scores,
            explanation=explanation,
        )

    def rank(
        self,
        reference: ProjectSignature,
        candidates: Iterable[ProjectSignature],
    ) -> tuple[SimilarityResult, ...]:
        """Return candidates ordered from most to least similar."""

        results = [self.compare(reference, candidate) for candidate in candidates]
        return tuple(
            sorted(
                results,
                key=lambda result: result.overall_score,
                reverse=True,
            )
        )

    @staticmethod
    def _observations(
        signature: ProjectSignature,
    ) -> dict[str, dict[str, Any]]:
        observations: dict[str, dict[str, Any]] = {}

        for evidence in signature.evidence.snapshot():
            section = evidence.metadata.get("signature_section")
            field_name = evidence.metadata.get("field_name")
            if not isinstance(section, str) or not isinstance(field_name, str):
                continue
            observations.setdefault(section, {})[field_name] = evidence.value

        return observations
