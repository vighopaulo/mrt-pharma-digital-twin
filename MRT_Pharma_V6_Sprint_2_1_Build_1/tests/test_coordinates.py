import math
import pytest

from mrt_pharma.domain.spatial.coordinates import Coordinates3D


def test_euclidean_distance() -> None:
    a = Coordinates3D(0.0, 0.0, 0.0)
    b = Coordinates3D(3.0, 4.0, 12.0)
    assert math.isclose(a.euclidean_distance_to(b), 13.0)


def test_horizontal_and_vertical_distance() -> None:
    a = Coordinates3D(1.0, 2.0, 3.0)
    b = Coordinates3D(4.0, 6.0, 11.0)
    assert math.isclose(a.horizontal_distance_to(b), 5.0)
    assert math.isclose(a.vertical_distance_to(b), 8.0)


def test_translation_returns_new_instance() -> None:
    point = Coordinates3D(1.0, 2.0, 3.0)
    moved = point.translated(dx_m=4.0, dy_m=-1.0, dz_m=2.0)
    assert moved == Coordinates3D(5.0, 1.0, 5.0)
    assert point == Coordinates3D(1.0, 2.0, 3.0)


def test_rejects_nan() -> None:
    with pytest.raises(ValueError):
        Coordinates3D(float("nan"), 0.0, 0.0)


def test_rejects_non_coordinate_distance_target() -> None:
    with pytest.raises(TypeError):
        Coordinates3D(0.0, 0.0, 0.0).euclidean_distance_to((1.0, 2.0, 3.0))  # type: ignore[arg-type]
