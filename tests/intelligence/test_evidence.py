from uuid import uuid4
import pytest
from mrt.intelligence.evidence import ConfidenceLevel, Evidence, EvidenceCollection, EvidenceSourceType
from mrt.intelligence.project_signature import ProjectSignature

def test_evidence_rejects_blank_title():
    with pytest.raises(ValueError):
        Evidence("   ", EvidenceSourceType.USER_INPUT, 1)

def test_evidence_rejects_invalid_scores():
    with pytest.raises(ValueError):
        Evidence("Invalid", EvidenceSourceType.USER_INPUT, 10, reliability=1.1)

def test_evidence_weighted_score():
    item = Evidence("Volume", EvidenceSourceType.IMPORTED_FILE, 12000, reliability=0.8, relevance=0.5)
    assert item.weighted_score == pytest.approx(0.4)

def test_collection_behaviour():
    a = Evidence("Schedule", EvidenceSourceType.IMPORTED_FILE, {"slots": 20})
    b = Evidence("Scanner", EvidenceSourceType.EQUIPMENT_CATALOG, {"model": "PET/CT"})
    collection = EvidenceCollection()
    collection.add(a)
    collection.add(b)
    assert collection.count == 2
    assert collection.get(a.id) == a
    assert collection.by_source_type(EvidenceSourceType.EQUIPMENT_CATALOG) == (b,)
    assert collection.remove(a.id) == a

def test_duplicate_rejected():
    item = Evidence("Duplicate", EvidenceSourceType.USER_INPUT, True)
    collection = EvidenceCollection([item])
    with pytest.raises(ValueError):
        collection.add(item)

def test_collection_confidence():
    collection = EvidenceCollection([
        Evidence("A", EvidenceSourceType.USER_INPUT, 1, reliability=0.8, relevance=0.5),
        Evidence("B", EvidenceSourceType.SYSTEM_DERIVED, 2, reliability=1.0, relevance=0.8),
    ])
    result = collection.confidence()
    assert result.score == pytest.approx(0.6)
    assert result.level == ConfidenceLevel.HIGH
    assert result.evidence_count == 2

def test_project_signature_confidence():
    signature = ProjectSignature(project_id=uuid4())
    signature.evidence.add(Evidence(
        "Annual report", EvidenceSourceType.EXTERNAL_PUBLICATION,
        {"patients": 5000}, reliability=0.9, relevance=0.9,
    ))
    assert signature.confidence.score == pytest.approx(0.81)
    assert signature.confidence.level == ConfidenceLevel.VERY_HIGH
