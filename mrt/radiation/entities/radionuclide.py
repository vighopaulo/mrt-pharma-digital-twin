from __future__ import annotations

from dataclasses import dataclass
from math import exp, log


@dataclass(frozen=True, slots=True)
class Radionuclide:
    """
    Represents the physical decay properties of one radionuclide.

    Half-life is stored in minutes so short-lived PET and longer-lived
    therapeutic radionuclides can use one consistent internal unit.
    """

    symbol: str
    name: str
    half_life_minutes: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "symbol",
            self._normalize_required(self.symbol, "symbol"),
        )
        object.__setattr__(
            self,
            "name",
            self._normalize_required(self.name, "name"),
        )

        if isinstance(self.half_life_minutes, bool) or not isinstance(
            self.half_life_minutes,
            (int, float),
        ):
            raise TypeError("half_life_minutes must be a number.")

        if self.half_life_minutes <= 0:
            raise ValueError(
                "half_life_minutes must be greater than zero."
            )

        object.__setattr__(
            self,
            "half_life_minutes",
            float(self.half_life_minutes),
        )

    @staticmethod
    def _normalize_required(value: str, field_name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string.")

        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field_name} cannot be empty or whitespace.")

        return normalized

    @property
    def decay_constant_per_minute(self) -> float:
        """Return the radioactive decay constant in inverse minutes."""
        return log(2.0) / self.half_life_minutes

    def remaining_fraction(self, elapsed_minutes: float) -> float:
        """
        Return the fraction of activity remaining after elapsed time.

        At zero minutes the result is 1.0. After one half-life it is 0.5.
        """
        elapsed = self._validate_elapsed_minutes(elapsed_minutes)
        return exp(-self.decay_constant_per_minute * elapsed)

    def remaining_activity_mbq(
        self,
        initial_activity_mbq: float,
        elapsed_minutes: float,
    ) -> float:
        """Return remaining activity in MBq after elapsed time."""
        initial = self._validate_activity(initial_activity_mbq)
        return initial * self.remaining_fraction(elapsed_minutes)

    def elapsed_minutes_for_fraction(
        self,
        remaining_fraction: float,
    ) -> float:
        """
        Return elapsed minutes required to reach a remaining fraction.

        The fraction must be greater than zero and no greater than one.
        """
        if isinstance(remaining_fraction, bool) or not isinstance(
            remaining_fraction,
            (int, float),
        ):
            raise TypeError("remaining_fraction must be a number.")

        fraction = float(remaining_fraction)
        if fraction <= 0 or fraction > 1:
            raise ValueError(
                "remaining_fraction must be greater than 0 and at most 1."
            )

        return -log(fraction) / self.decay_constant_per_minute

    @staticmethod
    def _validate_elapsed_minutes(value: float) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("elapsed_minutes must be a number.")

        elapsed = float(value)
        if elapsed < 0:
            raise ValueError("elapsed_minutes cannot be negative.")

        return elapsed

    @staticmethod
    def _validate_activity(value: float) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("initial_activity_mbq must be a number.")

        activity = float(value)
        if activity < 0:
            raise ValueError("initial_activity_mbq cannot be negative.")

        return activity

    @property
    def display_name(self) -> str:
        """Return a concise user-facing radionuclide label."""
        return (
            f"{self.symbol} — {self.name} "
            f"(t½ {self.half_life_minutes:g} min)"
        )
