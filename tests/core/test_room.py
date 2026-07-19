from uuid import UUID

import pytest

from mrt.core.entities.room import Room


def test_room_stores_name_and_type() -> None:
    room = Room(name="PET Scanner 1", room_type="Imaging")

    assert room.name == "PET Scanner 1"
    assert room.room_type == "Imaging"


def test_room_receives_unique_identifier() -> None:
    first = Room(name="Uptake 1")
    second = Room(name="Uptake 2")

    assert isinstance(first.id, UUID)
    assert isinstance(second.id, UUID)
    assert first.id != second.id


def test_room_name_is_trimmed() -> None:
    room = Room(name="  Hot Lab  ")

    assert room.name == "Hot Lab"


def test_room_type_is_trimmed() -> None:
    room = Room(name="Suite 1", room_type="  Theranostics  ")

    assert room.room_type == "Theranostics"


@pytest.mark.parametrize("invalid_name", ["", " ", "\t", "\n"])
def test_blank_room_name_is_rejected(invalid_name: str) -> None:
    with pytest.raises(ValueError):
        Room(name=invalid_name)


@pytest.mark.parametrize("invalid_type", ["", " ", "\t", "\n"])
def test_blank_room_type_is_rejected(invalid_type: str) -> None:
    with pytest.raises(ValueError):
        Room(name="Room 1", room_type=invalid_type)


def test_display_name_without_room_type() -> None:
    room = Room(name="Waste Holding")

    assert room.display_name == "Waste Holding"


def test_display_name_with_room_type() -> None:
    room = Room(name="Suite 3", room_type="Private Therapy")

    assert room.display_name == "Suite 3 (Private Therapy)"
