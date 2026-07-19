from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from mrt.simulation.checkpoint_manager import CheckpointManager
from mrt.simulation.rollback_manager import RollbackAction, RollbackManager


class TransactionStatus(StrEnum):
    ACTIVE = "active"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"


@dataclass(slots=True)
class SimulationTransaction:
    """Coordinates checkpoint, commit, and rollback behavior."""

    name: str
    checkpoint_manager: CheckpointManager
    rollback_manager: RollbackManager
    status: TransactionStatus = TransactionStatus.ACTIVE

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("name must be a string.")
        if not self.name.strip():
            raise ValueError("name cannot be empty.")
        if not isinstance(self.checkpoint_manager, CheckpointManager):
            raise TypeError(
                "checkpoint_manager must be a CheckpointManager."
            )
        if not isinstance(self.rollback_manager, RollbackManager):
            raise TypeError("rollback_manager must be a RollbackManager.")

    def begin(self, state: dict[str, Any]) -> None:
        if self.status != TransactionStatus.ACTIVE:
            raise RuntimeError("transaction is no longer active.")
        self.checkpoint_manager.create(self.name, state)

    def commit(self) -> None:
        if self.status != TransactionStatus.ACTIVE:
            raise RuntimeError("only active transactions can be committed.")
        self.status = TransactionStatus.COMMITTED

    def rollback(
        self,
        allocations: list[str],
    ) -> tuple[dict[str, Any], list[RollbackAction]]:
        if self.status != TransactionStatus.ACTIVE:
            raise RuntimeError("only active transactions can be rolled back.")

        restored_state = self.checkpoint_manager.restore(self.name)
        actions = self.rollback_manager.rollback(allocations)
        self.status = TransactionStatus.ROLLED_BACK
        return restored_state, actions
