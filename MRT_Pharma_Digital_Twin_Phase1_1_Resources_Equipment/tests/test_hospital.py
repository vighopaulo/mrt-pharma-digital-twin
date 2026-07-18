from core.assets import ExistingAsset
from core.enums import NodeType, ProjectType, RoomType
from core.hospital import Hospital
from core.rooms import ClinicalRoom
from core.spatial import SpatialNode


def test_hospital_accepts_rooms_nodes_and_assets() -> None:
    hospital = Hospital(
        name="Example Medical Center",
        project_type=ProjectType.EXISTING_HOSPITAL,
        country="United States",
        city="Newark",
    )
    hospital.add_node(
        SpatialNode("Radiopharmacy Node", NodeType.RADIOPHARMACY, 0, 0, 0)
    )
    hospital.add_room(
        ClinicalRoom("Radiopharmacy", RoomType.RADIOPHARMACY, floor=1, area_m2=75)
    )
    hospital.add_asset(ExistingAsset("Existing PET Scanner", "PET scanner"))

    assert len(hospital.nodes) == 1
    assert len(hospital.rooms) == 1
    assert len(hospital.existing_assets) == 1
