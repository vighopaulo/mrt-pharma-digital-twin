from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol, TypeVar

from mrt.simulation.checkpoint_manager import CheckpointManager
from mrt.simulation.rollback_manager import RollbackManager
from mrt.simulation.simulation_transaction import (
    SimulationTransaction,
    TransactionStatus,
)


T = TypeVar("T")


class SupportsSimulationState(Protocol):
    """Minimal interface required for transaction-aware execution."""

    def export_state(self) -> dict[str, Any]:
        ...

    def import_state(self, state: dict[str, Any]) -> None:
        ...


@dataclass(frozen=True, slots=True)
class TransactionExecutionResult:
    transaction_name: str
    status: TransactionStatus
    value: Any = None
    rollback_resources: tuple[str, ...] = ()
    error: Exception | None = None


@dataclass(slots=True)
class TransactionalSimulationEngine:
    """Adds transactional execution to a simulation engine.

    The wrapped engine only needs to expose export_state() and
    import_state(). Existing SimulationEngine implementations can adopt
    this interface without changing their event-loop behavior.
    """

    engine: SupportsSimulationState
    checkpoint_manager: CheckpointManager
    rollback_manager: RollbackManager

    def __post_init__(self) -> None:
        if not hasattr(self.engine, "export_state"):
            raise TypeError("engine must define export_state().")
        if not hasattr(self.engine, "import_state"):
            raise TypeError("engine must define import_state().")
        if not isinstance(self.checkpoint_manager, CheckpointManager):
            raise TypeError(
                "checkpoint_manager must be a CheckpointManager."
            )
        if not isinstance(self.rollback_manager, RollbackManager):
            raise TypeError("rollback_manager must be a RollbackManager.")

    def execute(
        self,
        transaction_name: str,
        operation: Callable[[], T],
        *,
        rollback_resources: list[str] | None = None,
        reraise: bool = False,
    ) -> TransactionExecutionResult:
        if not isinstance(transaction_name, str):
            raise TypeError("transaction_name must be a string.")
        if not transaction_name.strip():
            raise ValueError("transaction_name cannot be empty.")
        if not callable(operation):
            raise TypeError("operation must be callable.")

        resources = list(rollback_resources or [])
        transaction = SimulationTransaction(
            name=transaction_name,
            checkpoint_manager=self.checkpoint_manager,
            rollback_manager=self.rollback_manager,
        )

        transaction.begin(self.engine.export_state())

        try:
            value = operation()
        except Exception as error:
            restored_state, actions = transaction.rollback(resources)
            self.engine.import_state(restored_state)

            result = TransactionExecutionResult(
                transaction_name=transaction_name,
                status=transaction.status,
                rollback_resources=tuple(
                    action.resource_name for action in actions
                ),
                error=error,
            )

            if reraise:
                raise
            return result

        transaction.commit()
        return TransactionExecutionResult(
            transaction_name=transaction_name,
            status=transaction.status,
            value=value,
        )
