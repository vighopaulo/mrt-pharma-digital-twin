"""Tests for deterministic project-signature discovery."""

from uuid import uuid4

import pytest

from mrt.intelligence.discovery import (
    DiscoveryContext,
    SignatureDiscoveryEngine,
)
from mrt.intelligence.evidence import EvidenceSourceType


def test_discovers_sections_and_creates_evidence() -> None:
    project_id = uuid4()
    context = DiscoveryContext(
        project_id=project_id,
        source_type=EvidenceSourceType.IMPORTED_FILE,
        source_reference="hospital-input.csv",
        data={
            "spatial": {
                "building_count": 3,
                "maximum_route_m": 510,
            },
            "equipment": {
                "pet_ct_count": 2,
                "cyclotron_count": 1,
            },
        },
    )

    result = SignatureDiscoveryEngine().discover(context)

    assert result.signature.project_id == project_id
    assert result.signature.spatial.is_initialized is True
    assert result.signature.equipment.is_initialized is True
    assert result.signature.workflow.is_initialized is False
    assert result.discovered_sections == ("spatial", "equipment")
    assert "workflow" in result.missing_sections
    assert result.signature.evidence.count == 4
    assert result.confidence.score == pytest.approx(1.0)


def test_preserves_zero_and_false_as_meaningful_greenfield_values() -> None:
    result = SignatureDiscoveryEngine().discover(
        DiscoveryContext(
            data={
                "equipment": {
                    "cyclotron_count": 0,
                    "existing_facility": False,
                }
            }
        )
    )

    assert result.signature.equipment.is_initialized is True
    assert result.observations["equipment"]["cyclotron_count"] == 0
    assert result.observations["equipment"]["existing_facility"] is False
    assert result.signature.evidence.count == 2


def test_ignores_none_and_blank_values() -> None:
    result = SignatureDiscoveryEngine().discover(
        DiscoveryContext(
            data={
                "transport": {
                    "route_length_m": None,
                    "mode": "",
                }
            }
        )
    )

    assert result.signature.transport.is_initialized is False
    assert result.discovered_sections == ()
    assert result.signature.evidence.count == 0


def test_supports_section_aliases() -> None:
    result = SignatureDiscoveryEngine().discover(
        DiscoveryContext(
            data={
                "resource": {"technologist_count": 4},
                "economic": {"capital_budget_usd": 2_000_000},
                "operational_metrics": {"patients_per_day": 18},
            }
        )
    )

    assert result.signature.resources.is_initialized is True
    assert result.signature.economics.is_initialized is True
    assert result.signature.metrics.is_initialized is True


def test_reports_unknown_sections_without_failing() -> None:
    result = SignatureDiscoveryEngine().discover(
        DiscoveryContext(
            data={
                "spatial": {"building_count": 1},
                "weather": {"temperature_c": 25},
            }
        )
    )

    assert result.discovered_sections == ("spatial",)
    assert result.warnings == (
        "Ignored unrecognized discovery section: weather",
    )


def test_rejects_non_mapping_section() -> None:
    context = DiscoveryContext(data={"workflow": 7})

    with pytest.raises(TypeError, match="workflow"):
        SignatureDiscoveryEngine().discover(context)


def test_rejects_alias_collision() -> None:
    context = DiscoveryContext(
        data={
            "resources": {"staff_count": 5},
            "resource": {"staff_count": 6},
        }
    )

    with pytest.raises(ValueError, match="resources"):
        SignatureDiscoveryEngine().discover(context)


def test_result_reports_completeness() -> None:
    complete_data = {
        "spatial": {"value": 1},
        "workflow": {"value": 1},
        "resources": {"value": 1},
        "equipment": {"value": 1},
        "transport": {"value": 1},
        "radiation": {"value": 1},
        "economics": {"value": 1},
        "metrics": {"value": 1},
    }

    result = SignatureDiscoveryEngine().discover(
        DiscoveryContext(data=complete_data)
    )

    assert result.is_complete is True
    assert result.initialized_section_count == 8
    assert result.missing_sections == ()
