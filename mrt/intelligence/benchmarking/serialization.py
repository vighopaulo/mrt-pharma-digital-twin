from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from ..discovery import DiscoveryContext, SignatureDiscoveryEngine
from .benchmark_library import BenchmarkLibrary
from .benchmark_project import BenchmarkProject


class BenchmarkLibrarySerializer:
    """JSON import/export for portable benchmark libraries."""

    @staticmethod
    def dump(library: BenchmarkLibrary, path: str | Path) -> None:
        projects: list[dict[str, Any]] = []
        for project in library.snapshot():
            observations: dict[str, dict[str, Any]] = {}
            for evidence in project.signature.evidence.snapshot():
                section = evidence.metadata.get("signature_section")
                field_name = evidence.metadata.get("field_name")
                if isinstance(section, str) and isinstance(field_name, str):
                    observations.setdefault(section, {})[field_name] = evidence.value

            projects.append({
                "id": str(project.id),
                "name": project.name,
                "project_id": (
                    str(project.signature.project_id)
                    if project.signature.project_id else None
                ),
                "country": project.country,
                "region": project.region,
                "facility_type": project.facility_type,
                "project_type": project.project_type,
                "source_reference": project.source_reference,
                "source_title": project.source_title,
                "source_url": project.source_url,
                "image_url": project.image_url,
                "profile_url": project.profile_url,
                "is_verified": project.is_verified,
                "metadata": dict(project.metadata),
                "observations": observations,
            })

        Path(path).write_text(
            json.dumps({"projects": projects}, indent=2, default=str),
            encoding="utf-8",
        )

    @staticmethod
    def load(path: str | Path) -> BenchmarkLibrary:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        discoverer = SignatureDiscoveryEngine()
        library = BenchmarkLibrary()

        for record in payload.get("projects", []):
            project_id = record.get("project_id")
            signature = discoverer.discover(
                DiscoveryContext(
                    project_id=UUID(project_id) if project_id else None,
                    data=record.get("observations", {}),
                )
            ).signature

            library.add(BenchmarkProject(
                id=UUID(record["id"]),
                name=record["name"],
                signature=signature,
                country=record.get("country"),
                region=record.get("region"),
                facility_type=record.get("facility_type"),
                project_type=record.get("project_type"),
                source_reference=record.get("source_reference"),
                source_title=record.get("source_title"),
                source_url=record.get("source_url"),
                image_url=record.get("image_url"),
                profile_url=record.get("profile_url"),
                is_verified=bool(record.get("is_verified", False)),
                metadata=record.get("metadata", {}),
            ))

        return library
