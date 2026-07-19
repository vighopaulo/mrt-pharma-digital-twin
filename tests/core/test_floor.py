from uuid import UUID

import pytest

from mrt.core.entities.floor import Floor


def test_floor_stores_level_and_name() -> None:
    floor = Floor(level=2, name="Imaging")

    assert floor.level == 2
    assert floor.name == "Imaging"


def test_floor_receives_unique_identifier() -> None:
    first = Floor(level=1)
    second = Floor(level=2)

    assert isinstance(first.id, UUID)
    assert isinstance(second.id, UUID)
    assert first.id != second.id


@pytest.mark.parametrize(
    ("level", "expected"),
    [
        (0, "Ground Floor"),
        (1, "Floor 1"),
        (7, "Floor 7"),
        (-1, "Basement 1"),
        (-3, "Basement 3"),
    ],
)
def test_display_name_fallback(level: int, expected: str) -> None:
    assert Floor(level=level).display_name == expected


def test_display_name_prefers_explicit_name() -> None:
    assert Floor(level=3, name="Theranostics").display_name == "Theranostics"


def test_name_is_trimmed() -> None:
    floor = Floor(level=4, name="  Nuclear Medicine  ")

    assert floor.name == "Nuclear Medicine"


@pytest.mark.parametrize("invalid_name", ["", " ", "\t", "\n"])
def test_blank_name_is_rejected(invalid_name: str) -> None:
    with pytest.raises(ValueError):
        Floor(level=1, name=invalid_name)


@pytest.mark.parametrize("invalid_level", [1.0, "1", True, None])
def test_non_integer_level_is_rejected(invalid_level: object) -> None:
    with pytest.raises(TypeError):
        Floor(level=invalid_level)  # type: ignore[arg-type]
