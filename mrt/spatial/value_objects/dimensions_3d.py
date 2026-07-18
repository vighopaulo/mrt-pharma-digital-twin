from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class Dimensions3D:
    """
    Immutable physical dimensions of a three-dimensional object.

    Units:
        length_m: metres
        width_m: metres
        height_m: metres
        footprint_area_m2: square metres
        volume_m3: cubic metres
    """

    length_m: float
    width_m: float
    height_m: float

    def __post_init__(self) -> None:
        values = {
            "length_m": self.length_m,
            "width_m": self.width_m,
            "height_m": self.height_m,
        }

        for name, value in values.items():
            if not isfinite(value):
                raise ValueError(f"{name} must be a finite number.")
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero.")

    @property
    def footprint_area_m2(self) -> float:
        """Return the object's horizontal footprint area."""
        return self.length_m * self.width_m

    @property
    def volume_m3(self) -> float:
        """Return the object's enclosed rectangular volume."""
        return self.length_m * self.width_m * self.height_m

    def fits_within(self, container: "Dimensions3D") -> bool:
        """
        Return True when this object fits inside the supplied container
        without rotation.
        """
        if not isinstance(container, Dimensions3D):
            raise TypeError("container must be a Dimensions3D instance.")

        return (
            self.length_m <= container.length_m
            and self.width_m <= container.width_m
            and self.height_m <= container.height_m
        )
