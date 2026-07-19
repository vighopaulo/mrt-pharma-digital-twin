from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol


class SupportsStateExport(Protocol):
    def export_state(self) -> dict[str, Any]:
        ...


@dataclass(frozen=True, slots=True)
class SimulationSnapshot:
    name: str
    created_at: datetime
    trigger_value: int
    state: dict[str, Any]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("snapshot name cannot be empty.")
        if self.trigger_value < 0:
            raise ValueError("trigger_value cannot be negative.")


@dataclass(slots=True)
class SimulationSnapshotManager:
    """Creates periodic in-memory snapshots from an exportable engine."""

    interval: int
    max_snapshots: int | None = None
    snapshots: list[SimulationSnapshot] = field(default_factory=list)
    _last_trigger_value: int | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if isinstance(self.interval, bool) or not isinstance(self.interval, int):
            raise TypeError("interval must be an integer.")
        if self.interval <= 0:
            raise ValueError("interval must be greater than zero.")
        if self.max_snapshots is not None:
            if isinstance(self.max_snapshots, bool) or not isinstance(
                self.max_snapshots,
                int,
            ):
                raise TypeError("max_snapshots must be an integer or None.")
            if self.max_snapshots <= 0:
                raise ValueError("max_snapshots must be greater than zero.")

    @property
    def latest(self) -> SimulationSnapshot | None:
        if not self.snapshots:
            return None
        return self.snapshots[-1]

    def should_snapshot(self, trigger_value: int) -> bool:
        if isinstance(trigger_value, bool) or not isinstance(trigger_value, int):
            raise TypeError("trigger_value must be an integer.")
        if trigger_value < 0:
            raise ValueError("trigger_value cannot be negative.")
        if trigger_value == 0:
            return False
        if trigger_value % self.interval != 0:
            return False
        return trigger_value != self._last_trigger_value

    def capture(
        self,
        engine: SupportsStateExport,
        trigger_value: int,
        *,
        name: str | None = None,
        created_at: datetime | None = None,
    ) -> SimulationSnapshot:
        if not hasattr(engine, "export_state"):
            raise TypeError("engine must define export_state().")
        if not self.should_snapshot(trigger_value):
            raise ValueError("snapshot is not due for this trigger value.")

        snapshot_name = name or f"snapshot-{trigger_value:08d}"
        timestamp = created_at or datetime.now(timezone.utc)

        snapshot = SimulationSnapshot(
            name=snapshot_name,
            created_at=timestamp,
            trigger_value=trigger_value,
            state=deepcopy(engine.export_state()),
        )
        self.snapshots.append(snapshot)
        self._last_trigger_value = trigger_value
        self._apply_retention_policy()
        return snapshot

    def capture_if_due(
        self,
        engine: SupportsStateExport,
        trigger_value: int,
    ) -> SimulationSnapshot | None:
        if not self.should_snapshot(trigger_value):
            return None
        return self.capture(engine, trigger_value)

    def _apply_retention_policy(self) -> None:
        if self.max_snapshots is None:
            return
        overflow = len(self.snapshots) - self.max_snapshots
        if overflow > 0:
            del self.snapshots[:overflow]
