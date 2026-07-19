import pytest

from mrt.simulation.checkpoint_manager import CheckpointManager
from mrt.simulation.rollback_manager import RollbackManager
from mrt.simulation.simulation_transaction import (
    SimulationTransaction,
    TransactionStatus,
)


def make_transaction() -> SimulationTransaction:
    return SimulationTransaction(
        name="workflow-1",
        checkpoint_manager=CheckpointManager(),
        rollback_manager=RollbackManager(),
    )


def test_begin_creates_recoverable_checkpoint() -> None:
    transaction = make_transaction()
    state = {"scanner": "busy", "queue": ["patient-1"]}

    transaction.begin(state)
    state["queue"].append("patient-2")

    restored, _ = transaction.rollback(["PET-1"])

    assert restored == {
        "scanner": "busy",
        "queue": ["patient-1"],
    }


def test_commit_changes_transaction_status() -> None:
    transaction = make_transaction()
    transaction.begin({"scanner": "idle"})

    transaction.commit()

    assert transaction.status == TransactionStatus.COMMITTED


def test_rollback_returns_recovery_actions() -> None:
    transaction = make_transaction()
    transaction.begin({"scanner": "busy"})

    _, actions = transaction.rollback(["PET-1", "Tech-1"])

    assert transaction.status == TransactionStatus.ROLLED_BACK
    assert [action.resource_name for action in actions] == [
        "PET-1",
        "Tech-1",
    ]


def test_committed_transaction_cannot_rollback() -> None:
    transaction = make_transaction()
    transaction.begin({"scanner": "idle"})
    transaction.commit()

    with pytest.raises(RuntimeError):
        transaction.rollback(["PET-1"])


def test_rolled_back_transaction_cannot_commit() -> None:
    transaction = make_transaction()
    transaction.begin({"scanner": "busy"})
    transaction.rollback(["PET-1"])

    with pytest.raises(RuntimeError):
        transaction.commit()
