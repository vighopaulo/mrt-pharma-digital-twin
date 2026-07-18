from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True, slots=True)
class Coordinates3D:
    """Immutable global Cartesian coordinates expressed in metres."""

    x_m: float
    y_m: float
    z_m: float

    def __post_init__(self) -> None:
        for name, value in (
            ("x_m", self.x_m),
            ("y_m", self.y_m),
            ("z_m", self.z_m),
        ):
            if not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be numeric.")
            if value != value:  # NaN check
                raise ValueError(f"{name} cannot be NaN.")

    def euclidean_distance_to(self, other: "Coordinates3D") -> float:
        """Return straight-line 3D distance in metres."""
        if not isinstance(other, Coordinates3D):
            raise TypeError("other must be a Coordinates3D instance.")

        dx = other.x_m - self.x_m
        dy = other.y_m - self.y_m
        dz = other.z_m - self.z_m
        return sqrt(dx * dx + dy * dy + dz * dz)

    def horizontal_distance_to(self, other: "Coordinates3D") -> float:
        """Return planar X-Y distance in metres."""
        if not isinstance(other, Coordinates3D):
            raise TypeError("other must be a Coordinates3D instance.")

        dx = other.x_m - self.x_m
        dy = other.y_m - self.y_m
        return sqrt(dx * dx + dy * dy)

    def vertical_distance_to(self, other: "Coordinates3D") -> float:
        """Return absolute vertical separation in metres."""
        if not isinstance(other, Coordinates3D):
            raise TypeError("other must be a Coordinates3D instance.")
        return abs(other.z_m - self.z_m)

    def translated(self, dx_m: float = 0.0, dy_m: float = 0.0, dz_m: float = 0.0) -> "Coordinates3D":
        """Return a new point translated by the supplied offsets."""
        return Coordinates3D(
            x_m=self.x_m + dx_m,
            y_m=self.y_m + dy_m,
            z_m=self.z_m + dz_m,
        )
