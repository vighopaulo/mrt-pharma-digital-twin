import pytest

from mrt.simulation.checkpoint_manager import CheckpointManager
from mrt.simulation.rollback_manager import RollbackManager
from mrt.simulation.simulation_transaction import TransactionStatus
from mrt.simulation.transactional_engine import (
    TransactionalSimulationEngine,
)


class FakeSimulationEngine:
    def __init__(self) -> None:
        self.state = {
            "clock": 0.0,
            "queue": ["patient-1"],
            "completed": [],
        }

    def export_state(self) -> dict:
        return {
            "clock": self.state["clock"],
            "queue": list(self.state["queue"]),
            "completed": list(self.state["completed"]),
        }

    def import_state(self, state: dict) -> None:
        self.state = state


def make_engine() -> tuple[
    FakeSimulationEngine,
    TransactionalSimulationEngine,
]:
    engine = FakeSimulationEngine()
    wrapper = TransactionalSimulationEngine(
        engine=engine,
        checkpoint_manager=CheckpointManager(),
        rollback_manager=RollbackManager(),
    )
    return engine, wrapper


def test_successful_operation_commits() -> None:
    engine, wrapper = make_engine()

    def operation() -> str:
        engine.state["queue"].remove("patient-1")
        engine.state["completed"].append("patient-1")
        engine.state["clock"] = 15.0
        return "complete"

    result = wrapper.execute("treatment-1", operation)

    assert result.status == TransactionStatus.COMMITTED
    assert result.value == "complete"
    assert engine.state["completed"] == ["patient-1"]


def test_failed_operation_restores_engine_state() -> None:
    engine, wrapper = make_engine()

    def operation() -> None:
        engine.state["queue"].clear()
        engine.state["clock"] = 10.0
        raise RuntimeError("scanner failure")

    result = wrapper.execute(
        "treatment-1",
        operation,
        rollback_resources=["PET-1", "Tech-1"],
    )

    assert result.status == TransactionStatus.ROLLED_BACK
    assert isinstance(result.error, RuntimeError)
    assert result.rollback_resources == ("PET-1", "Tech-1")
    assert engine.state == {
        "clock": 0.0,
        "queue": ["patient-1"],
        "completed": [],
    }


def test_reraise_restores_state_before_error_propagates() -> None:
    engine, wrapper = make_engine()

    def operation() -> None:
        engine.state["clock"] = 99.0
        raise ValueError("invalid event")

    with pytest.raises(ValueError):
        wrapper.execute(
            "event-1",
            operation,
            rollback_resources=["PET-1"],
            reraise=True,
        )

    assert engine.state["clock"] == 0.0


def test_empty_transaction_name_is_rejected() -> None:
    _, wrapper = make_engine()

    with pytest.raises(ValueError):
        wrapper.execute("", lambda: None)
