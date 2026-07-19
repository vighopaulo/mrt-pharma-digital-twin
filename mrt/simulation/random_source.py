from __future__ import annotations

from dataclasses import dataclass, field
from random import Random


@dataclass(slots=True)
class SimulationRandomSource:
    """Provides reproducible random streams for simulation experiments."""

    seed: int | None = None
    _random: Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.seed is not None:
            if isinstance(self.seed, bool) or not isinstance(self.seed, int):
                raise TypeError("seed must be an integer or None.")
        self._random = Random(self.seed)

    @property
    def random(self) -> Random:
        return self._random

    def reset(self) -> None:
        self._random.seed(self.seed)

    def reseed(self, seed: int | None) -> None:
        if seed is not None:
            if isinstance(seed, bool) or not isinstance(seed, int):
                raise TypeError("seed must be an integer or None.")
        self.seed = seed
        self._random.seed(seed)
