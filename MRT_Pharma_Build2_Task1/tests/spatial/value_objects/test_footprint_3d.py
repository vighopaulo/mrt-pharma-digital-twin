import pytest

from mrt.spatial.value_objects.footprint_3d import Footprint3D


def test_area():
    assert Footprint3D(20.0, 10.0).area_m2 == 200.0


def test_invalid_length():
    with pytest.raises(ValueError):
        Footprint3D(0.0, 10.0)


def test_invalid_width():
    with pytest.raises(ValueError):
        Footprint3D(20.0, 0.0)


def test_can_accommodate():
    fp = Footprint3D(20.0, 10.0)
    assert fp.can_accommodate(150.0)
    assert not fp.can_accommodate(250.0)
