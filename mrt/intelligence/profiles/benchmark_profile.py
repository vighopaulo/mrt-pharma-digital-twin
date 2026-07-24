from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Mapping
from uuid import UUID
from .profile_link import ProfileLink
from .profile_source import ProfileSource

@dataclass(frozen=True)
class BenchmarkProfile:
    benchmark_id: UUID
    name: str
    rank: int
    similarity_score: float
    similarity_percentage: float
    country: str | None = None
    region: str | None = None
    facility_type: str | None = None
    project_type: str | None = None
    image_url: str | None = None
    display_url: str | None = None
    summary: str = ""
    similarity_explanation: str = ""
    section_scores: Mapping[str, float] = field(default_factory=dict)
    highlights: tuple[str, ...] = ()
    differences: tuple[str, ...] = ()
    metrics: Mapping[str, Any] = field(default_factory=dict)
    links: tuple[ProfileLink, ...] = ()
    sources: tuple[ProfileSource, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    def __post_init__(self):
        if not self.name.strip(): raise ValueError("Benchmark profile name must not be empty.")
        if self.rank <= 0: raise ValueError("Benchmark profile rank must be positive.")
        if not 0 <= self.similarity_score <= 1: raise ValueError("Similarity score must be between 0 and 1.")
    def to_dict(self):
        return {
            "benchmark_id": str(self.benchmark_id), "name": self.name, "rank": self.rank,
            "similarity_score": self.similarity_score, "similarity_percentage": self.similarity_percentage,
            "country": self.country, "region": self.region, "facility_type": self.facility_type,
            "project_type": self.project_type, "image_url": self.image_url, "display_url": self.display_url,
            "summary": self.summary, "similarity_explanation": self.similarity_explanation,
            "section_scores": dict(self.section_scores), "highlights": list(self.highlights),
            "differences": list(self.differences), "metrics": dict(self.metrics),
            "links": [{"label": x.label, "url": x.url, "link_type": x.link_type.value} for x in self.links],
            "sources": [{"title": x.title, "reference": x.reference, "url": x.url, "date": x.date, "publisher": x.publisher, "verified": x.verified} for x in self.sources],
            "metadata": dict(self.metadata),
        }
