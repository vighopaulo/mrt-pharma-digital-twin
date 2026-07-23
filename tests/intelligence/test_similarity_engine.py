"""Tests for the weighted, explainable project similarity engine."""

from uuid import uuid4

import pytest

from mrt.intelligence.discovery import DiscoveryContext, SignatureDiscoveryEngine
from mrt.intelligence.similarity import SimilarityEngine, SimilarityWeights


def signature(project_id, data):
    return SignatureDiscoveryEngine().discover(
        DiscoveryContext(project_id=project_id, data=data)
    ).signature


def test_identical_projects_are_fully_similar() -> None:
    data = {
        "spatial": {"route_length_m": 500, "building_count": 3},
        "equipment": {"pet_ct_count": 2, "cyclotron_count": 0},
    }
    result = SimilarityEngine().compare(
        signature(uuid4(), data),
        signature(uuid4(), data),
    )

    assert result.overall_score == pytest.approx(1.0)
    assert result.score_for("spatial").score == pytest.approx(1.0)
    assert result.score_for("equipment").score == pytest.approx(1.0)


def test_numeric_similarity_scales_with_relative_difference() -> None:
    result = SimilarityEngine().compare(
        signature(uuid4(), {"spatial": {"route_length_m": 500}}),
        signature(uuid4(), {"spatial": {"route_length_m": 400}}),
    )

    assert result.score_for("spatial").score == pytest.approx(0.8)
    assert result.overall_score == pytest.approx(0.8)


def test_categorical_and_boolean_values_compare_exactly() -> None:
    result = SimilarityEngine().compare(
        signature(
            uuid4(),
            {"transport": {"mode": "MRT", "existing": False}},
        ),
        signature(
            uuid4(),
            {"transport": {"mode": "mrt", "existing": True}},
        ),
    )

    assert result.score_for("transport").score == pytest.approx(0.5)


def test_missing_fields_are_reported_but_common_fields_are_scored() -> None:
    result = SimilarityEngine().compare(
        signature(
            uuid4(),
            {"equipment": {"pet_ct_count": 2, "cyclotron_count": 0}},
        ),
        signature(uuid4(), {"equipment": {"pet_ct_count": 2}}),
    )

    score = result.score_for("equipment")
    assert score.score == pytest.approx(1.0)
    assert score.missing_fields == ("cyclotron_count",)


def test_weights_change_overall_similarity() -> None:
    reference = signature(
        uuid4(),
        {
            "spatial": {"route_length_m": 100},
            "equipment": {"pet_ct_count": 2},
        },
    )
    candidate = signature(
        uuid4(),
        {
            "spatial": {"route_length_m": 50},
            "equipment": {"pet_ct_count": 2},
        },
    )

    equal = SimilarityEngine().compare(reference, candidate)
    weighted = SimilarityEngine(
        SimilarityWeights(spatial=3.0, equipment=1.0)
    ).compare(reference, candidate)

    assert equal.overall_score == pytest.approx(0.75)
    assert weighted.overall_score == pytest.approx(0.625)


def test_rank_orders_most_similar_first() -> None:
    reference = signature(
        uuid4(),
        {"metrics": {"patients_per_day": 20}},
    )
    close_id = uuid4()
    far_id = uuid4()

    ranked = SimilarityEngine().rank(
        reference,
        [
            signature(far_id, {"metrics": {"patients_per_day": 5}}),
            signature(close_id, {"metrics": {"patients_per_day": 18}}),
        ],
    )

    assert ranked[0].candidate_project_id == close_id
    assert ranked[1].candidate_project_id == far_id


def test_no_shared_evidence_produces_zero_similarity() -> None:
    result = SimilarityEngine().compare(
        signature(uuid4(), {"spatial": {"building_count": 2}}),
        signature(uuid4(), {"equipment": {"pet_ct_count": 2}}),
    )

    assert result.overall_score == 0.0
    assert "Compared 0 of 8" in result.explanation


def test_sequence_values_use_jaccard_similarity() -> None:
    result = SimilarityEngine().compare(
        signature(
            uuid4(),
            {"workflow": {"isotopes": ["F-18", "Ga-68"]}},
        ),
        signature(
            uuid4(),
            {"workflow": {"isotopes": ["F-18", "C-11"]}},
        ),
    )

    assert result.score_for("workflow").score == pytest.approx(1 / 3)


def test_invalid_weights_are_rejected() -> None:
    with pytest.raises(ValueError):
        SimilarityWeights(spatial=-1.0)

    with pytest.raises(ValueError):
        SimilarityWeights(
            spatial=0,
            workflow=0,
            resources=0,
            equipment=0,
            transport=0,
            radiation=0,
            economics=0,
            metrics=0,
        )
