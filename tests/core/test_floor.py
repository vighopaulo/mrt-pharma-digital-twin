import pytest

from mrt.core.entities.floor import Floor
from mrt.core.entities.room import Room


def test_floor_adds_room() -> None:
    floor = Floor(level=1)
    room = Room(name="PET Suite")
    floor.add_room(room)

    assert floor.room_count == 1
    assert floor.get_room("pet suite") is room
    assert room.floor_id == floor.id


def test_floor_rejects_duplicate_room_name() -> None:
    floor = Floor(level=1, rooms=[Room(name="Hot Lab")])

    with pytest.raises(ValueError):
        floor.add_room(Room(name="hot lab"))


def test_room_cannot_belong_to_two_floors() -> None:
    room = Room(name="Uptake 1")
    first = Floor(level=1)
    second = Floor(level=2)
    first.add_room(room)

    with pytest.raises(ValueError):
        second.add_room(room)


def test_remove_room_clears_ownership() -> None:
    room = Room(name="Uptake 1")
    floor = Floor(level=1, rooms=[room])

    removed = floor.remove_room("Uptake 1")

    assert removed is room
    assert room.floor_id is None
    assert floor.room_count == 0
