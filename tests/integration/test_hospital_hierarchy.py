from mrt.core.entities.building import Building
from mrt.core.entities.equipment import Equipment
from mrt.core.entities.floor import Floor
from mrt.core.entities.room import Room


def test_complete_hospital_hierarchy() -> None:
    scanner = Equipment(
        name="PET Scanner 1",
        equipment_type="PET Scanner",
        manufacturer="GE",
        model="Discovery MI",
    )
    pet_suite = Room(
        name="PET Suite",
        room_type="Imaging",
        equipment=[scanner],
    )
    imaging_floor = Floor(
        level=1,
        name="Imaging",
        rooms=[pet_suite],
    )
    hospital = Building(
        name="MRT Cancer Center",
        floors=[imaging_floor],
    )

    assert hospital.floor_count == 1
    assert hospital.get_floor(1) is imaging_floor
    assert imaging_floor.room_count == 1
    assert imaging_floor.get_room("PET Suite") is pet_suite
    assert pet_suite.equipment_count == 1
    assert pet_suite.get_equipment("PET Scanner 1") is scanner
    assert imaging_floor.building_id == hospital.id
    assert pet_suite.floor_id == imaging_floor.id
    assert scanner.room_id == pet_suite.id
