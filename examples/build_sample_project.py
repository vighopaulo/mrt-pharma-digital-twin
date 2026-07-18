from core import Carrier, ConstraintSense, DecisionConstraint, Hospital, MRTNetwork, NodeType, Project, ProjectType, RouteSegment, RouteType, SpatialNode

def build_sample_project() -> Project:
    hospital = Hospital("Sample Hospital", ProjectType.EXISTING_HOSPITAL, "United States", "Newark")
    source = SpatialNode("Radiopharmacy", NodeType.RADIOPHARMACY, 0, 0, 0)
    target = SpatialNode("PET Scanner 1", NodeType.CLINICAL_ROOM, 120, 0, 0)
    hospital.add_node(source); hospital.add_node(target)
    network = MRTNetwork("Sample MRT Network", central_equipment_cost=250_000, integration_cost=100_000)
    network.add_node(source, 35_000); network.add_node(target, 45_000)
    network.add_segment(RouteSegment("Radiopharmacy to PET", source.id, target.id, 120, RouteType.HORIZONTAL, 6_500, 0.0025))
    network.add_carrier(Carrier("MRT Carrier 1", 5, 50_000))
    project = Project("Sample MRT Expansion", hospital, network)
    project.add_constraint(DecisionConstraint("CAPEX ceiling", ConstraintSense.MAXIMUM, 2_000_000, "USD"))
    return project

if __name__ == "__main__":
    p = build_sample_project(); assert p.mrt_network is not None
    print(f"Installed MRT length: {p.mrt_network.installed_length_m:.1f} m")
    print(f"Estimated MRT CAPEX: ${p.mrt_network.total_capex:,.2f}")
