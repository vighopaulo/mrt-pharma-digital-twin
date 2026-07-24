from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from .benchmark_project import BenchmarkProject
from .benchmark_query import BenchmarkQuery


@dataclass
class BenchmarkLibrary:
    """In-memory collection of benchmark projects."""

    projects: list[BenchmarkProject] = field(default_factory=list)

    def __post_init__(self) -> None:
        ids = [project.id for project in self.projects]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate benchmark project IDs.")

    def add(self, project: BenchmarkProject) -> None:
        if self.get(project.id) is not None:
            raise ValueError(f"Benchmark project {project.id} already exists.")
        self.projects.append(project)

    def get(self, project_id: UUID) -> BenchmarkProject | None:
        return next((p for p in self.projects if p.id == project_id), None)

    def remove(self, project_id: UUID) -> BenchmarkProject:
        for index, project in enumerate(self.projects):
            if project.id == project_id:
                return self.projects.pop(index)
        raise KeyError(f"Benchmark project {project_id} not found.")

    def snapshot(self) -> tuple[BenchmarkProject, ...]:
        return tuple(self.projects)

    def filtered(self, query: BenchmarkQuery) -> tuple[BenchmarkProject, ...]:
        countries = {query.normalize(v) for v in query.countries}
        facilities = {query.normalize(v) for v in query.facility_types}
        project_types = {query.normalize(v) for v in query.project_types}

        def matches(project: BenchmarkProject) -> bool:
            if query.verified_only and not project.is_verified:
                return False
            if countries and (
                project.country is None
                or query.normalize(project.country) not in countries
            ):
                return False
            if facilities and (
                project.facility_type is None
                or query.normalize(project.facility_type) not in facilities
            ):
                return False
            if project_types and (
                project.project_type is None
                or query.normalize(project.project_type) not in project_types
            ):
                return False
            return True

        return tuple(project for project in self.projects if matches(project))
