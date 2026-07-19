from mrt.simulation.checkpoint_manager import CheckpointManager
from mrt.simulation.rollback_manager import RollbackManager
from mrt.simulation.simulation_transaction import (
    SimulationTransaction,
    TransactionStatus,
)


def test_failed_workflow_restores_original_state_and_resources() -> None:
    original_state = {
        "scanner_status": "idle",
        "queue": ["patient-1"],
        "completed": [],
    }

    transaction = SimulationTransaction(
        name="patient-1-treatment",
        checkpoint_manager=CheckpointManager(),
        rollback_manager=RollbackManager(),
    )
    transaction.begin(original_state)

    working_state = {
        "scanner_status": "busy",
        "queue": [],
        "completed": [],
    }

    restored_state, actions = transaction.rollback(
        ["PET-1", "Tech-1"]
    )

    assert working_state != restored_state
    assert restored_state == original_state
    assert len(actions) == 2
    assert transaction.status == TransactionStatus.ROLLED_BACK
