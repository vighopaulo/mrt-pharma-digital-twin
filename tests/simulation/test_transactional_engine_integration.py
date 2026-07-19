from mrt.simulation.checkpoint_manager import CheckpointManager
from mrt.simulation.rollback_manager import RollbackManager
from mrt.simulation.simulation_transaction import TransactionStatus
from mrt.simulation.transactional_engine import (
    TransactionalSimulationEngine,
)


class WorkflowEngine:
    def __init__(self) -> None:
        self.clock = 0.0
        self.active_patient = None
        self.completed = []

    def export_state(self) -> dict:
        return {
            "clock": self.clock,
            "active_patient": self.active_patient,
            "completed": list(self.completed),
        }

    def import_state(self, state: dict) -> None:
        self.clock = state["clock"]
        self.active_patient = state["active_patient"]
        self.completed = list(state["completed"])


def test_workflow_failure_rolls_back_simulation_state() -> None:
    engine = WorkflowEngine()
    wrapper = TransactionalSimulationEngine(
        engine=engine,
        checkpoint_manager=CheckpointManager(),
        rollback_manager=RollbackManager(),
    )

    def failed_workflow() -> None:
        engine.clock = 12.0
        engine.active_patient = "patient-1"
        raise RuntimeError("resource interruption")

    result = wrapper.execute(
        "patient-1-workflow",
        failed_workflow,
        rollback_resources=["PET-1", "Room-1"],
    )

    assert result.status == TransactionStatus.ROLLED_BACK
    assert engine.clock == 0.0
    assert engine.active_patient is None
    assert engine.completed == []
