from core.carriers import Carrier
from core.enums import NodeType, RouteType
from core.mrt_network import MRTNetwork
from core.spatial import RouteSegment, SpatialNode

def test_network_capex_and_energy() -> None:
    network = MRTNetwork("Hospital MRT", central_equipment_cost=100_000, integration_cost=25_000)
    source = SpatialNode("Radiopharmacy", NodeType.RADIOPHARMACY, 0, 0, 0)
    target = SpatialNode("PET Room", NodeType.CLINICAL_ROOM, 100, 0, 0)
    network.add_node(source, station_cost=20_000)
    network.add_node(target, station_cost=30_000)
    segment = RouteSegment("Main corridor", source.id, target.id, 100, RouteType.HORIZONTAL, 5_000, 0.002)
    network.add_segment(segment)
    network.add_carrier(Carrier("Carrier 1", 5, 40_000))
    assert network.installed_length_m == 100
    assert network.pathway_capex == 500_000
    assert network.total_capex == 715_000
    assert network.annual_trip_energy_kwh({segment.id: 1_000}) == 200
