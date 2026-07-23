"""Deterministic discovery of project-signature sections."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Mapping

from ..evidence import Evidence
from ..project_signature import ProjectSignature
from .discovery_context import DiscoveryContext
from .signature_discovery_result import SignatureDiscoveryResult


class SignatureDiscoveryEngine:
    """
    Build a ProjectSignature from normalized project information.

    Build 63 deliberately uses deterministic mapping rather than AI.
    Later builds may add adapters for files, databases, simulation output,
    and RAG retrieval without changing this engine's public result model.
    """

    SECTION_TO_ATTRIBUTE: Mapping[str, str] = {
        "spatial": "spatial",
        "workflow": "workflow",
        "resources": "resources",
        "equipment": "equipment",
        "transport": "transport",
        "radiation": "radiation",
        "economics": "economics",
        "metrics": "metrics",
    }

    SECTION_ALIASES: Mapping[str, str] = {
        "resource": "resources",
        "economic": "economics",
        "operational_metrics": "metrics",
    }

    def discover(
        self,
        context: DiscoveryContext,
    ) -> SignatureDiscoveryResult:
        """Discover initialized signature sections and supporting evidence."""

        normalized_data, warnings = self._normalize_sections(context.data)
        signature = ProjectSignature(project_id=context.project_id)

        discovered: list[str] = []
        missing: list[str] = []
        observations: dict[str, Mapping[str, Any]] = {}

        for section_name, attribute_name in self.SECTION_TO_ATTRIBUTE.items():
            section_data = normalized_data.get(section_name, {})

            if not isinstance(section_data, Mapping):
                raise TypeError(
                    f"Discovery section '{section_name}' must be a mapping."
                )

            meaningful = self._meaningful_values(section_data)
            if not meaningful:
                missing.append(section_name)
                continue

            current_section = getattr(signature, attribute_name)
            setattr(
                signature,
                attribute_name,
                replace(current_section, is_initialized=True),
            )
            observations[section_name] = dict(meaningful)
            discovered.append(section_name)

            for field_name, value in meaningful.items():
                signature.evidence.add(
                    Evidence(
                        title=f"{section_name}.{field_name}",
                        source_type=context.source_type,
                        value=value,
                        source_reference=context.source_reference,
                        description=(
                            "Discovered from normalized project input."
                        ),
                        metadata={
                            **dict(context.metadata),
                            "signature_section": section_name,
                            "field_name": field_name,
                        },
                    )
                )

        return SignatureDiscoveryResult(
            signature=signature,
            discovered_sections=tuple(discovered),
            missing_sections=tuple(missing),
            observations=observations,
            warnings=tuple(warnings),
        )

    def _normalize_sections(
        self,
        raw_data: Mapping[str, Any],
    ) -> tuple[dict[str, Any], list[str]]:
        normalized: dict[str, Any] = {}
        warnings: list[str] = []

        for raw_name, value in raw_data.items():
            section_name = self.SECTION_ALIASES.get(raw_name, raw_name)

            if section_name not in self.SECTION_TO_ATTRIBUTE:
                warnings.append(
                    f"Ignored unrecognized discovery section: {raw_name}"
                )
                continue

            if section_name in normalized:
                raise ValueError(
                    "Multiple inputs resolve to discovery section "
                    f"'{section_name}'."
                )

            normalized[section_name] = value

        return normalized, warnings

    @staticmethod
    def _meaningful_values(
        section_data: Mapping[str, Any],
    ) -> dict[str, Any]:
        """
        Remove absent values while preserving valid zero and False values.

        Zero is important for greenfield cases such as initial cyclotron
        capacity equal to zero.
        """

        return {
            key: value
            for key, value in section_data.items()
            if value is not None and value != ""
        }
