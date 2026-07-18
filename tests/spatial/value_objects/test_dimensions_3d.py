import math

import pytest

from mrt.spatial.value_objects.dimensions_3d import Dimensions3D


def test_dimensions_are_stored() -> None:
    dimensions = Dimensions3D(4.0, 3.0, 2.5)

    assert dimensions.length_m == 4.0
    assert dimensions.width_m == 3.0
    assert dimensions.height_m == 2.5


def test_footprint_area_is_calculated() -> None:
    dimensions = Dimensions3D(4.0, 3.0, 2.5)

    assert dimensions.footprint_area_m2 == 12.0


def test_volume_is_calculated() -> None:
    dimensions = Dimensions3D(4.0, 3.0, 2.5)

    assert dimensions.volume_m3 == 30.0


@pytest.mark.parametrize(
    ("length_m", "width_m", "height_m"),
    [
        (0.0, 3.0, 2.0),
        (-1.0, 3.0, 2.0),
        (4.0, 0.0, 2.0),
        (4.0, -1.0, 2.0),
        (4.0, 3.0, 0.0),
        (4.0, 3.0, -1.0),
    ],
)
def test_non_positive_dimensions_are_rejected(
    length_m: float,
    width_m: float,
    height_m: float,
) -> None:
    with pytest.raises(ValueError):
        Dimensions3D(length_m, width_m, height_m)


@pytest.mark.parametrize("invalid_value", [math.inf, -math.inf, math.nan])
def test_non_finite_dimensions_are_rejected(invalid_value: float) -> None:
    with pytest.raises(ValueError):
        Dimensions3D(invalid_value, 3.0, 2.0)


def test_object_fits_within_larger_container() -> None:
    equipment = Dimensions3D(2.0, 1.5, 2.2)
    room = Dimensions3D(5.0, 4.0, 3.0)

    assert equipment.fits_within(room)


def test_object_does_not_fit_when_one_axis_exceeds_container() -> None:
    equipment = Dimensions3D(2.0, 1.5, 3.2)
    room = Dimensions3D(5.0, 4.0, 3.0)

    assert not equipment.fits_within(room)


def test_fits_within_rejects_invalid_container_type() -> None:
    dimensions = Dimensions3D(2.0, 1.5, 2.2)

    with pytest.raises(TypeError):
        dimensions.fits_within(object())  # type: ignore[arg-type]


def test_dimensions_are_immutable() -> None:
    dimensions = Dimensions3D(4.0, 3.0, 2.5)

    with pytest.raises(Exception):
        dimensions.length_m = 5.0  # type: ignore[misc]
