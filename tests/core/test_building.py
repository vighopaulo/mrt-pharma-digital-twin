import pytest

from mrt.core.entities.building import Building
from mrt.core.entities.floor import Floor


def test_building_adds_and_orders_floors() -> None:
    building = Building("Cancer Center")
    building.add_floor(Floor(level=2))
    building.add_floor(Floor(level=0))

    assert [floor.level for floor in building.floors] == [0, 2]
    assert building.floor_count == 2


def test_building_rejects_duplicate_floor_level() -> None:
    building = Building("Cancer Center")
    building.add_floor(Floor(level=1))

    with pytest.raises(ValueError):
        building.add_floor(Floor(level=1))


def test_floor_cannot_belong_to_two_buildings() -> None:
    floor = Floor(level=0)
    first = Building("A")
    second = Building("B")
    first.add_floor(floor)

    with pytest.raises(ValueError):
        second.add_floor(floor)


def test_remove_floor_clears_ownership() -> None:
    floor = Floor(level=0)
    building = Building("Cancer Center", floors=[floor])

    removed = building.remove_floor(0)

    assert removed is floor
    assert floor.building_id is None
    assert building.floor_count == 0
