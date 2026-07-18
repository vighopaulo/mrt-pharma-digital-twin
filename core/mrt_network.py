from dataclasses import dataclass, field
from uuid import UUID, uuid4
from core.carriers import Carrier
from core.exceptions import DomainValidationError
from core.spatial import RouteSegment, SpatialNode

@dataclass(slots=True)
class MRTNetwork:
    name: str
    nodes: dict[UUID, SpatialNode] = field(default_factory=dict)
    segments: dict[UUID, RouteSegment] = field(default_factory=dict)
    carriers: list[Carrier] = field(default_factory=list)
    station_costs: dict[UUID, float] = field(default_factory=dict)
    central_equipment_cost: float = 0.0
    integration_cost: float = 0.0
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip(): raise DomainValidationError("Network name cannot be empty.")
        if self.central_equipment_cost < 0 or self.integration_cost < 0: raise DomainValidationError("Network costs cannot be negative.")

    def add_node(self, node: SpatialNode, station_cost: float = 0.0) -> None:
        if station_cost < 0: raise DomainValidationError("Station cost cannot be negative.")
        if node.id in self.nodes: raise DomainValidationError("Node already exists in network.")
        self.nodes[node.id] = node
        if station_cost: self.station_costs[node.id] = station_cost

    def add_segment(self, segment: RouteSegment) -> None:
        if segment.id in self.segments: raise DomainValidationError("Segment already exists in network.")
        if segment.start_node_id not in self.nodes or segment.end_node_id not in self.nodes: raise DomainValidationError("Both nodes must exist in network.")
        self.segments[segment.id] = segment

    def add_carrier(self, carrier: Carrier) -> None:
        if any(x.id == carrier.id for x in self.carriers): raise DomainValidationError("Carrier already exists.")
        self.carriers.append(carrier)

    @property
    def installed_length_m(self) -> float:
        return sum(x.length_m for x in self.segments.values())

    @property
    def pathway_capex(self) -> float:
        return sum(x.capex for x in self.segments.values())

    @property
    def carrier_capex(self) -> float:
        return sum(x.unit_cost for x in self.carriers)

    @property
    def station_capex(self) -> float:
        return sum(self.station_costs.values())

    @property
    def total_capex(self) -> float:
        return self.pathway_capex + self.station_capex + self.carrier_capex + self.central_equipment_cost + self.integration_cost

    def annual_trip_energy_kwh(self, trips_by_segment: dict[UUID, int]) -> float:
        if set(trips_by_segment) - set(self.segments): raise DomainValidationError("Unknown segment ID in energy calculation.")
        return sum(self.segments[sid].trip_energy_kwh(trips) for sid, trips in trips_by_segment.items())
