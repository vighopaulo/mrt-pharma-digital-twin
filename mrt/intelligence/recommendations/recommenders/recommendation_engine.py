from __future__ import annotations

from collections.abc import Iterable

from ..benchmarking import BenchmarkResult
from ..project_signature import ProjectSignature
from .recommendation_result import RecommendationResult
from .recommenders import (
    EconomicRecommender,
    EquipmentRecommender,
    RadiationRecommender,
    StaffingRecommender,
    ThroughputRecommender,
    TransportRecommender,
)


class RecommendationEngine:
    """Generate and rank evidence-backed recommendations."""

    def __init__(self, recommenders: Iterable[object] | None = None) -> None:
        self.recommenders = tuple(recommenders or (
            ThroughputRecommender(),
            EquipmentRecommender(),
            StaffingRecommender(),
            TransportRecommender(),
            RadiationRecommender(),
            EconomicRecommender(),
        ))

    def generate(
        self,
        reference: ProjectSignature,
        benchmarks: Iterable[BenchmarkResult],
        *,
        limit: int | None = None,
        minimum_confidence: float = 0.0,
    ) -> RecommendationResult:
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be between 0 and 1.")
        if limit is not None and limit <= 0:
            raise ValueError("limit must be positive.")

        benchmark_tuple = tuple(benchmarks)
        recommendations = [
            recommendation
            for recommender in self.recommenders
            for recommendation in recommender.recommend(reference, benchmark_tuple)
            if recommendation.confidence >= minimum_confidence
        ]
        recommendations.sort(
            key=lambda item: (
                int(item.priority),
                item.action_score,
                item.confidence,
            ),
            reverse=True,
        )
        if limit is not None:
            recommendations = recommendations[:limit]

        explanation = (
            f"Generated {len(recommendations)} recommendation(s) "
            f"from {len(benchmark_tuple)} benchmark project(s)."
        )
        return RecommendationResult(
            project_id=reference.project_id,
            recommendations=tuple(recommendations),
            benchmark_count=len(benchmark_tuple),
            explanation=explanation,
        )
