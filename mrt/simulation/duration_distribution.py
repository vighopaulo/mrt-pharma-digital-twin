from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from random import Random


class DurationDistributionType(StrEnum):
    FIXED = "fixed"
    UNIFORM = "uniform"
    TRIANGULAR = "triangular"
    NORMAL = "normal"


@dataclass(frozen=True, slots=True)
class DurationDistribution:
    """
    Defines a duration distribution in seconds.

    Use `sample_seconds()` with a supplied `random.Random` instance to obtain
    reproducible stochastic durations.
    """

    distribution_type: DurationDistributionType
    minimum_seconds: float
    maximum_seconds: float | None = None
    mode_seconds: float | None = None
    mean_seconds: float | None = None
    standard_deviation_seconds: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.distribution_type, DurationDistributionType):
            raise TypeError(
                "distribution_type must be a DurationDistributionType."
            )

        self._validate_nonnegative(
            self.minimum_seconds,
            "minimum_seconds",
        )

        if self.distribution_type == DurationDistributionType.FIXED:
            self._validate_fixed()

        elif self.distribution_type == DurationDistributionType.UNIFORM:
            self._validate_uniform()

        elif self.distribution_type == DurationDistributionType.TRIANGULAR:
            self._validate_triangular()

        elif self.distribution_type == DurationDistributionType.NORMAL:
            self._validate_normal()

    @classmethod
    def fixed(cls, seconds: float) -> "DurationDistribution":
        return cls(
            distribution_type=DurationDistributionType.FIXED,
            minimum_seconds=seconds,
        )

    @classmethod
    def uniform(
        cls,
        minimum_seconds: float,
        maximum_seconds: float,
    ) -> "DurationDistribution":
        return cls(
            distribution_type=DurationDistributionType.UNIFORM,
            minimum_seconds=minimum_seconds,
            maximum_seconds=maximum_seconds,
        )

    @classmethod
    def triangular(
        cls,
        minimum_seconds: float,
        mode_seconds: float,
        maximum_seconds: float,
    ) -> "DurationDistribution":
        return cls(
            distribution_type=DurationDistributionType.TRIANGULAR,
            minimum_seconds=minimum_seconds,
            maximum_seconds=maximum_seconds,
            mode_seconds=mode_seconds,
        )

    @classmethod
    def normal(
        cls,
        mean_seconds: float,
        standard_deviation_seconds: float,
        minimum_seconds: float = 0.0,
    ) -> "DurationDistribution":
        return cls(
            distribution_type=DurationDistributionType.NORMAL,
            minimum_seconds=minimum_seconds,
            mean_seconds=mean_seconds,
            standard_deviation_seconds=standard_deviation_seconds,
        )

    def sample_seconds(self, random_source: Random) -> float:
        if not isinstance(random_source, Random):
            raise TypeError("random_source must be random.Random.")

        if self.distribution_type == DurationDistributionType.FIXED:
            return float(self.minimum_seconds)

        if self.distribution_type == DurationDistributionType.UNIFORM:
            assert self.maximum_seconds is not None
            return random_source.uniform(
                self.minimum_seconds,
                self.maximum_seconds,
            )

        if self.distribution_type == DurationDistributionType.TRIANGULAR:
            assert self.maximum_seconds is not None
            assert self.mode_seconds is not None
            return random_source.triangular(
                self.minimum_seconds,
                self.maximum_seconds,
                self.mode_seconds,
            )

        assert self.mean_seconds is not None
        assert self.standard_deviation_seconds is not None
        sample = random_source.gauss(
            self.mean_seconds,
            self.standard_deviation_seconds,
        )
        return max(float(self.minimum_seconds), sample)

    @staticmethod
    def _validate_nonnegative(value: float, field_name: str) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{field_name} must be numeric.")
        if value < 0:
            raise ValueError(f"{field_name} cannot be negative.")

    def _validate_fixed(self) -> None:
        if any(
            value is not None
            for value in (
                self.maximum_seconds,
                self.mode_seconds,
                self.mean_seconds,
                self.standard_deviation_seconds,
            )
        ):
            raise ValueError(
                "fixed distribution accepts only minimum_seconds."
            )

    def _validate_uniform(self) -> None:
        if self.maximum_seconds is None:
            raise ValueError(
                "uniform distribution requires maximum_seconds."
            )
        self._validate_nonnegative(
            self.maximum_seconds,
            "maximum_seconds",
        )
        if self.maximum_seconds < self.minimum_seconds:
            raise ValueError(
                "maximum_seconds cannot be less than minimum_seconds."
            )

    def _validate_triangular(self) -> None:
        if self.maximum_seconds is None or self.mode_seconds is None:
            raise ValueError(
                "triangular distribution requires mode and maximum."
            )
        self._validate_nonnegative(
            self.maximum_seconds,
            "maximum_seconds",
        )
        self._validate_nonnegative(
            self.mode_seconds,
            "mode_seconds",
        )
        if not (
            self.minimum_seconds
            <= self.mode_seconds
            <= self.maximum_seconds
        ):
            raise ValueError(
                "mode_seconds must lie between minimum and maximum."
            )

    def _validate_normal(self) -> None:
        if (
            self.mean_seconds is None
            or self.standard_deviation_seconds is None
        ):
            raise ValueError(
                "normal distribution requires mean and standard deviation."
            )
        self._validate_nonnegative(
            self.mean_seconds,
            "mean_seconds",
        )
        self._validate_nonnegative(
            self.standard_deviation_seconds,
            "standard_deviation_seconds",
        )
        if self.standard_deviation_seconds == 0:
            raise ValueError(
                "standard_deviation_seconds must be greater than zero."
            )
