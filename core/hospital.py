from dataclasses import dataclass, field
from uuid import UUID, uuid4
from core.assets import ExistingAsset
from core.enums import ProjectType
from core.exceptions import DomainValidationError
from core.rooms import ClinicalRoom
from core.spatial import SpatialNode

@dataclass(slots=True)
class Hospital:
    name: str
    project_type: ProjectType
    country: str
    city: str
    rooms: list[ClinicalRoom] = field(default_factory=list)
    nodes: list[SpatialNode] = field(default_factory=list)
    existing_assets: list[ExistingAsset] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip(): raise DomainValidationError("Hospital name cannot be empty.")
        if not self.country.strip() or not self.city.strip(): raise DomainValidationError("Hospital city and country are required.")

    def add_room(self, room: ClinicalRoom) -> None:
        if any(x.id == room.id for x in self.rooms): raise DomainValidationError("Room already exists.")
        self.rooms.append(room)

    def add_node(self, node: SpatialNode) -> None:
        if any(x.id == node.id for x in self.nodes): raise DomainValidationError("Node already exists.")
        self.nodes.append(node)

    def add_asset(self, asset: ExistingAsset) -> None:
        if any(x.id == asset.id for x in self.existing_assets): raise DomainValidationError("Asset already exists.")
        self.existing_assets.append(asset)
