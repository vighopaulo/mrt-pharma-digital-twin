"""Root aggregate for project-level intelligence."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from .evidence import ConfidenceAssessment, EvidenceCollection
from .signatures.economic_signature import EconomicSignature
from .signatures.equipment_signature import EquipmentSignature
from .signatures.operational_metrics import OperationalMetrics
from .signatures.radiation_signature import RadiationSignature
from .signatures.resource_signature import ResourceSignature
from .signatures.spatial_signature import SpatialSignature
from .signatures.transport_signature import TransportSignature
from .signatures.workflow_signature import WorkflowSignature

@dataclass
class ProjectSignature:
    id: UUID = field(default_factory=uuid4)
    project_id: UUID | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "7.0"
    spatial: SpatialSignature = field(default_factory=SpatialSignature)
    workflow: WorkflowSignature = field(default_factory=WorkflowSignature)
    resources: ResourceSignature = field(default_factory=ResourceSignature)
    equipment: EquipmentSignature = field(default_factory=EquipmentSignature)
    transport: TransportSignature = field(default_factory=TransportSignature)
    radiation: RadiationSignature = field(default_factory=RadiationSignature)
    economics: EconomicSignature = field(default_factory=EconomicSignature)
    metrics: OperationalMetrics = field(default_factory=OperationalMetrics)
    evidence: EvidenceCollection = field(default_factory=EvidenceCollection)

    @property
    def confidence(self) -> ConfidenceAssessment:
        return self.evidence.confidence()
