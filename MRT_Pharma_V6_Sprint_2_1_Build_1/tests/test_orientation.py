import math
import pytest

from mrt_pharma.domain.spatial.orientation import Orientation3D


def test_yaw_normalization() -> None:
    orientation = Orientation3D(yaw_deg=450.0)
    assert orientation.yaw_deg == 90.0


def test_signed_pitch_and_roll_normalization() -> None:
    orientation = Orientation3D(pitch_deg=190.0, roll_deg=-190.0)
    assert orientation.pitch_deg == -170.0
    assert orientation.roll_deg == 170.0


def test_forward_vector_on_positive_x_axis() -> None:
    vector = Orientation3D().forward_vector()
    assert math.isclose(vector[0], 1.0, abs_tol=1e-12)
    assert math.isclose(vector[1], 0.0, abs_tol=1e-12)
    assert math.isclose(vector[2], 0.0, abs_tol=1e-12)


def test_forward_vector_on_positive_y_axis() -> None:
    vector = Orientation3D(yaw_deg=90.0).forward_vector()
    assert math.isclose(vector[0], 0.0, abs_tol=1e-12)
    assert math.isclose(vector[1], 1.0, abs_tol=1e-12)
    assert math.isclose(vector[2], 0.0, abs_tol=1e-12)


def test_rotation_returns_new_normalized_orientation() -> None:
    base = Orientation3D(yaw_deg=350.0)
    rotated = base.rotated(yaw_delta_deg=20.0)
    assert rotated.yaw_deg == 10.0
    assert base.yaw_deg == 350.0


def test_rejects_nan() -> None:
    with pytest.raises(ValueError):
        Orientation3D(yaw_deg=float("nan"))
