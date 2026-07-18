from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Footprint3D:
    """Immutable rectangular footprint."""

    length_m: float
    width_m: float

    def __post_init__(self) -> None:
        if self.length_m <= 0:
            raise ValueError("length_m must be greater than zero.")
        if self.width_m <= 0:
            raise ValueError("width_m must be greater than zero.")

    @property
    def area_m2(self) -> float:
        return self.length_m * self.width_m

    def can_accommodate(self, required_area_m2: float) -> bool:
        if required_area_m2 < 0:
            raise ValueError("required_area_m2 cannot be negative.")
        return self.area_m2 >= required_area_m2
