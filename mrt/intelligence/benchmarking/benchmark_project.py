from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping
from uuid import UUID, uuid4

from ..project_signature import ProjectSignature


@dataclass(frozen=True)
class BenchmarkProject:
    """A comparable project with traceable source metadata."""

    name: str
    signature: ProjectSignature
    id: UUID = field(default_factory=uuid4)
    country: str | None = None
    region: str | None = None
    facility_type: str | None = None
    project_type: str | None = None
    source_reference: str | None = None
    source_title: str | None = None
    source_url: str | None = None
    image_url: str | None = None
    profile_url: str | None = None
    is_verified: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Benchmark project name must not be empty.")
        if not isinstance(self.signature, ProjectSignature):
            raise TypeError("signature must be a ProjectSignature.")
