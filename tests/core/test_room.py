import pytest

from mrt.core.entities.equipment import Equipment
from mrt.core.entities.room import Room


def test_room_adds_equipment() -> None:
    room = Room(name="PET Suite")
    scanner = Equipment(name="PET 1", equipment_type="PET Scanner")
    room.add_equipment(scanner)

    assert room.equipment_count == 1
    assert room.get_equipment("pet 1") is scanner
    assert scanner.room_id == room.id


def test_room_rejects_duplicate_equipment_name() -> None:
    room = Room(
        name="PET Suite",
        equipment=[Equipment(name="PET 1", equipment_type="PET Scanner")],
    )

    with pytest.raises(ValueError):
        room.add_equipment(
            Equipment(name="pet 1", equipment_type="PET Scanner")
        )


def test_equipment_cannot_belong_to_two_rooms() -> None:
    scanner = Equipment(name="PET 1", equipment_type="PET Scanner")
    first = Room(name="Suite A")
    second = Room(name="Suite B")
    first.add_equipment(scanner)

    with pytest.raises(ValueError):
        second.add_equipment(scanner)


def test_remove_equipment_clears_ownership() -> None:
    scanner = Equipment(name="PET 1", equipment_type="PET Scanner")
    room = Room(name="PET Suite", equipment=[scanner])

    removed = room.remove_equipment("PET 1")

    assert removed is scanner
    assert scanner.room_id is None
    assert room.equipment_count == 0
