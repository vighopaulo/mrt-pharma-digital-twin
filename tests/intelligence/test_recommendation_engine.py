from uuid import uuid4

import pytest

from mrt.intelligence.benchmarking import BenchmarkEngine, BenchmarkLibrary, BenchmarkProject
from mrt.intelligence.discovery import DiscoveryContext, SignatureDiscoveryEngine
from mrt.intelligence.recommendations import (
    RecommendationCategory,
    RecommendationEngine,
    RecommendationPriority,
)


def signature(data):
    return SignatureDiscoveryEngine().discover(
        DiscoveryContext(project_id=uuid4(), data=data)
    ).signature


def benchmark(name, data):
    return BenchmarkProject(name=name, signature=signature(data), is_verified=True)


def test_engine_generates_ranked_benchmark_backed_recommendations():
    reference = signature({
        "equipment": {"pet_ct_count": 1},
        "metrics": {"patients_per_day": 20},
        "resources": {"staff_count": 6},
        "transport": {"transport_time_min": 8},
        "radiation": {"worker_exposure_usv_per_gbq": 60},
        "economics": {"operating_cost": 1000},
    })
    library = BenchmarkLibrary([
        benchmark("A", {
            "equipment": {"pet_ct_count": 3},
            "metrics": {"patients_per_day": 40},
            "resources": {"staff_count": 10},
            "transport": {"transport_time_min": 4},
            "radiation": {"worker_exposure_usv_per_gbq": 10},
            "economics": {"operating_cost": 700},
        }),
        benchmark("B", {
            "equipment": {"pet_ct_count": 2},
            "metrics": {"patients_per_day": 36},
            "resources": {"staff_count": 9},
            "transport": {"transport_time_min": 5},
            "radiation": {"worker_exposure_usv_per_gbq": 12},
            "economics": {"operating_cost": 750},
        }),
    ])
    matches = BenchmarkEngine(library).retrieve(reference)
    result = RecommendationEngine().generate(reference, matches)

    assert result.count == 6
    assert result.benchmark_count == 2
    assert result.recommendations[0].priority >= result.recommendations[-1].priority
    assert any(r.category is RecommendationCategory.EQUIPMENT for r in result.recommendations)
    assert any(r.category is RecommendationCategory.RADIATION for r in result.recommendations)


def test_no_gap_produces_no_recommendation():
    reference = signature({"equipment": {"pet_ct_count": 3}})
    matches = BenchmarkEngine(BenchmarkLibrary([
        benchmark("A", {"equipment": {"pet_ct_count": 2}})
    ])).retrieve(reference)
    result = RecommendationEngine().generate(reference, matches)
    assert result.count == 0


def test_limit_and_confidence_filter():
    reference = signature({
        "equipment": {"pet_ct_count": 1},
        "metrics": {"patients_per_day": 10},
    })
    matches = BenchmarkEngine(BenchmarkLibrary([
        benchmark("A", {
            "equipment": {"pet_ct_count": 3},
            "metrics": {"patients_per_day": 30},
        })
    ])).retrieve(reference)

    result = RecommendationEngine().generate(
        reference, matches, limit=1, minimum_confidence=0.0
    )
    assert result.count == 1


def test_invalid_controls_raise():
    reference = signature({})
    engine = RecommendationEngine()
    with pytest.raises(ValueError):
        engine.generate(reference, (), limit=0)
    with pytest.raises(ValueError):
        engine.generate(reference, (), minimum_confidence=1.1)


def test_recommendation_action_score_is_bounded():
    reference = signature({"radiation": {"worker_exposure_usv_per_gbq": 50}})
    matches = BenchmarkEngine(BenchmarkLibrary([
        benchmark("A", {"radiation": {"worker_exposure_usv_per_gbq": 5}})
    ])).retrieve(reference)
    rec = RecommendationEngine().generate(reference, matches).recommendations[0]
    assert 0.0 <= rec.action_score <= 1.0
    assert rec.priority is RecommendationPriority.CRITICAL


def test_result_by_priority_returns_sorted_copy():
    reference = signature({
        "equipment": {"pet_ct_count": 1},
        "metrics": {"patients_per_day": 10},
    })
    matches = BenchmarkEngine(BenchmarkLibrary([
        benchmark("A", {
            "equipment": {"pet_ct_count": 3},
            "metrics": {"patients_per_day": 30},
        })
    ])).retrieve(reference)
    result = RecommendationEngine().generate(reference, matches)
    ordered = result.by_priority()
    assert len(ordered) == result.count
    assert ordered[0].priority >= ordered[-1].priority
