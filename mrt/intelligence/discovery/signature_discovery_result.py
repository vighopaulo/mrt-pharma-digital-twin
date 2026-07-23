"""Result object returned by signature discovery."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..evidence import ConfidenceAssessment
from ..project_signature import ProjectSignature


@dataclass(frozen=True)
class SignatureDiscoveryResult:
    """Auditable outcome of one discovery run."""

    signature: ProjectSignature
    discovered_sections: tuple[str, ...]
    missing_sections: tuple[str, ...]
    observations: Mapping[str, Mapping[str, Any]] = field(
        default_factory=dict
    )
    warnings: tuple[str, ...] = ()

    @property
    def confidence(self) -> ConfidenceAssessment:
        return self.signature.confidence

    @property
    def is_complete(self) -> bool:
        return not self.missing_sections

    @property
    def initialized_section_count(self) -> int:
        return len(self.discovered_sections)
