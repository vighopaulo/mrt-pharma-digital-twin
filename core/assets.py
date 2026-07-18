from dataclasses import dataclass, field
from uuid import UUID, uuid4
from core.enums import AssetDisposition
from core.exceptions import DomainValidationError

@dataclass(slots=True)
class ExistingAsset:
    name: str
    asset_type: str
    quantity: int = 1
    disposition: AssetDisposition = AssetDisposition.RETAIN
    replacement_value: float = 0.0
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip(): raise DomainValidationError("Asset name cannot be empty.")
        if self.quantity < 1: raise DomainValidationError("Asset quantity must be at least one.")
        if self.replacement_value < 0: raise DomainValidationError("Replacement value cannot be negative.")
