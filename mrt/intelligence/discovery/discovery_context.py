"""Input context for project-signature discovery."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping
from uuid import UUID

from ..evidence import EvidenceSourceType


@dataclass(frozen=True)
class DiscoveryContext:
    """
    Normalized input supplied to the signature-discovery engine.

    ``data`` is organized into signature sections such as ``spatial``,
    ``workflow``, ``resources``, and ``equipment``. Each section must be a
    mapping of field names to values.
    """

    data: Mapping[str, Any]
    project_id: UUID | None = None
    source_type: EvidenceSourceType = EvidenceSourceType.USER_INPUT
    source_reference: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.data, Mapping):
            raise TypeError("DiscoveryContext data must be a mapping.")

    def section(self, name: str) -> Mapping[str, Any]:
        """Return one section as a mapping, or an empty mapping."""

        value = self.data.get(name, {})
        if value is None:
            return {}
        if not isinstance(value, Mapping):
            raise TypeError(
                f"Discovery section '{name}' must be a mapping."
            )
        return value
