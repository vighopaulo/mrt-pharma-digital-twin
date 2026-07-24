from __future__ import annotations

from ..project_signature import ProjectSignature
from ..similarity import SimilarityEngine
from .benchmark_library import BenchmarkLibrary
from .benchmark_query import BenchmarkQuery
from .benchmark_result import BenchmarkResult


class BenchmarkEngine:
    """Retrieve and rank comparable projects."""

    def __init__(
        self,
        library: BenchmarkLibrary,
        similarity_engine: SimilarityEngine | None = None,
    ) -> None:
        self.library = library
        self.similarity_engine = similarity_engine or SimilarityEngine()

    def retrieve(
        self,
        reference: ProjectSignature,
        query: BenchmarkQuery | None = None,
    ) -> tuple[BenchmarkResult, ...]:
        query = query or BenchmarkQuery()

        scored = []
        for project in self.library.filtered(query):
            similarity = self.similarity_engine.compare(
                reference,
                project.signature,
            )
            if similarity.overall_score >= query.minimum_similarity:
                scored.append((project, similarity))

        scored.sort(
            key=lambda item: (
                item[1].overall_score,
                item[0].is_verified,
                item[0].name.casefold(),
            ),
            reverse=True,
        )

        return tuple(
            BenchmarkResult(rank=index, project=project, similarity=similarity)
            for index, (project, similarity) in enumerate(
                scored[:query.limit],
                start=1,
            )
        )
