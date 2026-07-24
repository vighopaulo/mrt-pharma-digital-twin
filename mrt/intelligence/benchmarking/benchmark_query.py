from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkQuery:
    """Filters and limits controlling benchmark retrieval."""

    limit: int = 5
    minimum_similarity: float = 0.0
    countries: tuple[str, ...] = ()
    facility_types: tuple[str, ...] = ()
    project_types: tuple[str, ...] = ()
    verified_only: bool = False

    def __post_init__(self) -> None:
        if self.limit <= 0:
            raise ValueError("limit must be positive.")
        if not 0.0 <= self.minimum_similarity <= 1.0:
            raise ValueError("minimum_similarity must be between 0 and 1.")

    @staticmethod
    def normalize(value: str) -> str:
        return value.strip().casefold()
