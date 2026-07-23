"""Traceable evidence entities used by the intelligence layer."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

class EvidenceSourceType(str, Enum):
    USER_INPUT = "user_input"
    IMPORTED_FILE = "imported_file"
    SYSTEM_DERIVED = "system_derived"
    EQUIPMENT_CATALOG = "equipment_catalog"
    INTERNAL_DATABASE = "internal_database"
    EXTERNAL_PUBLICATION = "external_publication"
    REGULATORY_SOURCE = "regulatory_source"
    VENDOR_DOCUMENTATION = "vendor_documentation"
    WEB_RETRIEVAL = "web_retrieval"

@dataclass(frozen=True)
class Evidence:
    title: str
    source_type: EvidenceSourceType
    value: Any
    id: UUID = field(default_factory=uuid4)
    source_reference: str | None = None
    unit: str | None = None
    description: str | None = None
    observed_at: datetime | None = None
    collected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reliability: float = 1.0
    relevance: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Evidence title must not be empty.")
        if not 0.0 <= self.reliability <= 1.0:
            raise ValueError("Evidence reliability must be between 0.0 and 1.0.")
        if not 0.0 <= self.relevance <= 1.0:
            raise ValueError("Evidence relevance must be between 0.0 and 1.0.")

    @property
    def weighted_score(self) -> float:
        return self.reliability * self.relevance
