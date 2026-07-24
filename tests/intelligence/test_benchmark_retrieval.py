from pathlib import Path
from uuid import uuid4

import pytest

from mrt.intelligence.benchmarking import (
    BenchmarkEngine,
    BenchmarkLibrary,
    BenchmarkProject,
    BenchmarkQuery,
)
from mrt.intelligence.benchmarking.serialization import BenchmarkLibrarySerializer
from mrt.intelligence.discovery import DiscoveryContext, SignatureDiscoveryEngine


def signature(data):
    return SignatureDiscoveryEngine().discover(
        DiscoveryContext(project_id=uuid4(), data=data)
    ).signature


def project(name, data, **kwargs):
    return BenchmarkProject(name=name, signature=signature(data), **kwargs)


def test_library_operations():
    item = project("Hospital A", {"metrics": {"patients_per_day": 20}})
    library = BenchmarkLibrary()
    library.add(item)
    assert library.get(item.id) == item
    with pytest.raises(ValueError):
        library.add(item)
    assert library.remove(item.id) == item


def test_retrieval_ranks_closest_first():
    reference = signature({"metrics": {"patients_per_day": 20}})
    close = project("Close", {"metrics": {"patients_per_day": 19}})
    far = project("Far", {"metrics": {"patients_per_day": 5}})
    results = BenchmarkEngine(BenchmarkLibrary([far, close])).retrieve(reference)
    assert [result.project.name for result in results] == ["Close", "Far"]
    assert results[0].score > results[1].score


def test_filters_and_verified_only():
    library = BenchmarkLibrary([
        project(
            "Nigeria Greenfield",
            {"spatial": {"building_count": 2}},
            country="Nigeria",
            facility_type="Cancer hospital",
            project_type="Greenfield",
            is_verified=True,
        ),
        project(
            "US Retrofit",
            {"spatial": {"building_count": 2}},
            country="United States",
            facility_type="Cancer hospital",
            project_type="Retrofit",
            is_verified=True,
        ),
    ])
    results = BenchmarkEngine(library).retrieve(
        signature({"spatial": {"building_count": 2}}),
        BenchmarkQuery(
            countries=("nigeria",),
            project_types=("greenfield",),
            verified_only=True,
        ),
    )
    assert len(results) == 1
    assert results[0].project.name == "Nigeria Greenfield"


def test_limit_and_minimum_similarity():
    library = BenchmarkLibrary([
        project("Exact", {"metrics": {"patients_per_day": 20}}),
        project("Near", {"metrics": {"patients_per_day": 19}}),
        project("Far", {"metrics": {"patients_per_day": 2}}),
    ])
    results = BenchmarkEngine(library).retrieve(
        signature({"metrics": {"patients_per_day": 20}}),
        BenchmarkQuery(limit=1, minimum_similarity=0.8),
    )
    assert len(results) == 1
    assert results[0].project.name == "Exact"


def test_display_url_prefers_profile_url():
    item = project(
        "Linked",
        {"equipment": {"pet_ct_count": 2}},
        source_url="https://example.org/source",
        profile_url="https://app.example.org/benchmark/linked",
    )
    result = BenchmarkEngine(BenchmarkLibrary([item])).retrieve(
        signature({"equipment": {"pet_ct_count": 2}})
    )[0]
    assert result.display_url == "https://app.example.org/benchmark/linked"


def test_serialization_round_trip(tmp_path: Path):
    original = project(
        "Round Trip",
        {
            "equipment": {"pet_ct_count": 2, "cyclotron_count": 0},
            "metrics": {"patients_per_day": 18},
        },
        country="Nigeria",
        image_url="https://example.org/hospital.jpg",
        profile_url="https://app.example.org/benchmark/round-trip",
        metadata={"beds": 450},
    )
    path = tmp_path / "benchmarks.json"
    BenchmarkLibrarySerializer.dump(BenchmarkLibrary([original]), path)
    restored = BenchmarkLibrarySerializer.load(path).snapshot()[0]
    assert restored.name == "Round Trip"
    assert restored.country == "Nigeria"
    assert restored.image_url.endswith(".jpg")
    assert restored.profile_url.endswith("round-trip")
    assert restored.metadata["beds"] == 450
    assert restored.signature.evidence.count == 3


def test_query_validation():
    with pytest.raises(ValueError):
        BenchmarkQuery(limit=0)
    with pytest.raises(ValueError):
        BenchmarkQuery(minimum_similarity=1.1)
