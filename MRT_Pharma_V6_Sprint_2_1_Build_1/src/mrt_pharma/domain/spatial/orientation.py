from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin


@dataclass(frozen=True, slots=True)
class Orientation3D:
    """Yaw, pitch, and roll orientation expressed in degrees.

    Yaw rotates around the vertical Z axis.
    Pitch rotates around the lateral Y axis.
    Roll rotates around the longitudinal X axis.
    """

    yaw_deg: float = 0.0
    pitch_deg: float = 0.0
    roll_deg: float = 0.0

    def __post_init__(self) -> None:
        for name, value in (
            ("yaw_deg", self.yaw_deg),
            ("pitch_deg", self.pitch_deg),
            ("roll_deg", self.roll_deg),
        ):
            if not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be numeric.")
            if value != value:
                raise ValueError(f"{name} cannot be NaN.")

        object.__setattr__(self, "yaw_deg", self._normalize(self.yaw_deg))
        object.__setattr__(self, "pitch_deg", self._normalize_signed(self.pitch_deg))
        object.__setattr__(self, "roll_deg", self._normalize_signed(self.roll_deg))

    @staticmethod
    def _normalize(angle: float) -> float:
        return float(angle) % 360.0

    @staticmethod
    def _normalize_signed(angle: float) -> float:
        normalized = (float(angle) + 180.0) % 360.0 - 180.0
        return 180.0 if normalized == -180.0 else normalized

    def forward_vector(self) -> tuple[float, float, float]:
        """Return a unit forward vector derived from yaw and pitch."""
        yaw = radians(self.yaw_deg)
        pitch = radians(self.pitch_deg)
        return (
            cos(pitch) * cos(yaw),
            cos(pitch) * sin(yaw),
            sin(pitch),
        )

    def rotated(self, yaw_delta_deg: float = 0.0, pitch_delta_deg: float = 0.0, roll_delta_deg: float = 0.0) -> "Orientation3D":
        """Return a new orientation after applying angular offsets."""
        return Orientation3D(
            yaw_deg=self.yaw_deg + yaw_delta_deg,
            pitch_deg=self.pitch_deg + pitch_delta_deg,
            roll_deg=self.roll_deg + roll_delta_deg,
        )
