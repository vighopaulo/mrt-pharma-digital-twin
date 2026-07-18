from dataclasses import dataclass, field
from math import sqrt
from uuid import UUID, uuid4
from core.enums import NodeType, RouteType
from core.exceptions import DomainValidationError

@dataclass(frozen=True, slots=True)
class SpatialNode:
    name: str
    node_type: NodeType
    x_m: float
    y_m: float
    z_m: float = 0.0
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip(): raise DomainValidationError("Node name cannot be empty.")

    def euclidean_distance_to(self, other: "SpatialNode") -> float:
        return sqrt((self.x_m-other.x_m)**2 + (self.y_m-other.y_m)**2 + (self.z_m-other.z_m)**2)

@dataclass(frozen=True, slots=True)
class RouteSegment:
    name: str
    start_node_id: UUID
    end_node_id: UUID
    length_m: float
    route_type: RouteType = RouteType.HORIZONTAL
    cost_per_m: float = 0.0
    energy_kwh_per_carrier_m: float = 0.0
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip(): raise DomainValidationError("Route segment name cannot be empty.")
        if self.start_node_id == self.end_node_id: raise DomainValidationError("A segment must connect different nodes.")
        if self.length_m <= 0: raise DomainValidationError("Route length must be greater than zero.")
        if self.cost_per_m < 0: raise DomainValidationError("Cost per metre cannot be negative.")
        if self.energy_kwh_per_carrier_m < 0: raise DomainValidationError("Energy intensity cannot be negative.")

    @property
    def capex(self) -> float:
        return self.length_m * self.cost_per_m

    def trip_energy_kwh(self, carrier_trips: int = 1) -> float:
        if carrier_trips < 0: raise DomainValidationError("Carrier trips cannot be negative.")
        return self.length_m * self.energy_kwh_per_carrier_m * carrier_trips
