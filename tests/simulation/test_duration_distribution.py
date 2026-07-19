from random import Random

import pytest

from mrt.simulation.duration_distribution import DurationDistribution


def test_fixed_distribution_returns_constant_value() -> None:
    distribution = DurationDistribution.fixed(30)

    assert distribution.sample_seconds(Random(1)) == 30.0
    assert distribution.sample_seconds(Random(999)) == 30.0


def test_uniform_distribution_stays_inside_bounds() -> None:
    distribution = DurationDistribution.uniform(10, 20)
    random_source = Random(42)

    values = [
        distribution.sample_seconds(random_source)
        for _ in range(100)
    ]

    assert all(10 <= value <= 20 for value in values)


def test_triangular_distribution_stays_inside_bounds() -> None:
    distribution = DurationDistribution.triangular(10, 15, 25)
    random_source = Random(42)

    values = [
        distribution.sample_seconds(random_source)
        for _ in range(100)
    ]

    assert all(10 <= value <= 25 for value in values)


def test_normal_distribution_is_clamped_to_minimum() -> None:
    distribution = DurationDistribution.normal(
        mean_seconds=1,
        standard_deviation_seconds=100,
        minimum_seconds=0,
    )
    random_source = Random(2)

    values = [
        distribution.sample_seconds(random_source)
        for _ in range(50)
    ]

    assert all(value >= 0 for value in values)


def test_same_seed_reproduces_same_sequence() -> None:
    distribution = DurationDistribution.uniform(5, 15)
    first = Random(123)
    second = Random(123)

    first_values = [
        distribution.sample_seconds(first)
        for _ in range(10)
    ]
    second_values = [
        distribution.sample_seconds(second)
        for _ in range(10)
    ]

    assert first_values == second_values


def test_invalid_uniform_bounds_are_rejected() -> None:
    with pytest.raises(ValueError):
        DurationDistribution.uniform(20, 10)


def test_invalid_triangular_mode_is_rejected() -> None:
    with pytest.raises(ValueError):
        DurationDistribution.triangular(10, 30, 20)


def test_zero_normal_standard_deviation_is_rejected() -> None:
    with pytest.raises(ValueError):
        DurationDistribution.normal(10, 0)
