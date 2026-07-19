from math import isclose

import pytest

from mrt.radiation.entities.radionuclide import Radionuclide


def make_f18() -> Radionuclide:
    return Radionuclide(
        symbol="F-18",
        name="Fluorine-18",
        half_life_minutes=109.77,
    )


def test_radionuclide_stores_normalized_fields() -> None:
    radionuclide = Radionuclide(
        symbol="  F-18  ",
        name="  Fluorine-18  ",
        half_life_minutes=109.77,
    )

    assert radionuclide.symbol == "F-18"
    assert radionuclide.name == "Fluorine-18"
    assert radionuclide.half_life_minutes == 109.77


@pytest.mark.parametrize("invalid_value", [0, -1, -0.5])
def test_non_positive_half_life_is_rejected(
    invalid_value: float,
) -> None:
    with pytest.raises(ValueError):
        Radionuclide("F-18", "Fluorine-18", invalid_value)


@pytest.mark.parametrize("invalid_value", ["109.77", None, True])
def test_non_numeric_half_life_is_rejected(
    invalid_value: object,
) -> None:
    with pytest.raises(TypeError):
        Radionuclide(
            "F-18",
            "Fluorine-18",
            invalid_value,  # type: ignore[arg-type]
        )


def test_remaining_fraction_at_zero_is_one() -> None:
    assert make_f18().remaining_fraction(0) == 1.0


def test_remaining_fraction_after_one_half_life_is_half() -> None:
    radionuclide = make_f18()

    assert isclose(
        radionuclide.remaining_fraction(radionuclide.half_life_minutes),
        0.5,
        rel_tol=1e-12,
    )


def test_remaining_fraction_after_two_half_lives_is_quarter() -> None:
    radionuclide = make_f18()

    assert isclose(
        radionuclide.remaining_fraction(
            2 * radionuclide.half_life_minutes
        ),
        0.25,
        rel_tol=1e-12,
    )


def test_remaining_activity_mbq() -> None:
    radionuclide = make_f18()

    assert isclose(
        radionuclide.remaining_activity_mbq(
            initial_activity_mbq=400,
            elapsed_minutes=radionuclide.half_life_minutes,
        ),
        200.0,
        rel_tol=1e-12,
    )


def test_zero_initial_activity_remains_zero() -> None:
    assert make_f18().remaining_activity_mbq(0, 60) == 0.0


def test_negative_elapsed_time_is_rejected() -> None:
    with pytest.raises(ValueError):
        make_f18().remaining_fraction(-1)


def test_negative_activity_is_rejected() -> None:
    with pytest.raises(ValueError):
        make_f18().remaining_activity_mbq(-1, 10)


def test_elapsed_time_for_half_fraction_equals_half_life() -> None:
    radionuclide = make_f18()

    assert isclose(
        radionuclide.elapsed_minutes_for_fraction(0.5),
        radionuclide.half_life_minutes,
        rel_tol=1e-12,
    )


@pytest.mark.parametrize("invalid_fraction", [0, -0.1, 1.1])
def test_invalid_remaining_fraction_is_rejected(
    invalid_fraction: float,
) -> None:
    with pytest.raises(ValueError):
        make_f18().elapsed_minutes_for_fraction(invalid_fraction)


def test_radionuclide_is_immutable() -> None:
    radionuclide = make_f18()

    with pytest.raises(Exception):
        radionuclide.half_life_minutes = 120  # type: ignore[misc]


def test_display_name() -> None:
    radionuclide = make_f18()

    assert (
        radionuclide.display_name
        == "F-18 — Fluorine-18 (t½ 109.77 min)"
    )
