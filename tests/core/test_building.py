from mrt.core.entities.building import Building

def test_building_add_floor():
    b = Building("Cancer Center")
    b.add_floor("Ground")
    assert b.floor_count == 1
