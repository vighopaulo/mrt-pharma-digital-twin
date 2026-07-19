from __future__ import annotations

from copy import deepcopy
from typing import Any

from mrt.simulation.engine_state import EngineState


class SimulationEngineStateMixin:
    """Adds native export/import behavior to an existing SimulationEngine.

    The host class is expected to expose:
    - `clock`
    - `event_queue`

    Optional engine-specific fields can be included by overriding
    `_export_engine_metadata()` and `_import_engine_metadata()`.
    """

    clock: Any
    event_queue: Any

    def _export_engine_metadata(self) -> dict[str, Any]:
        return {}

    def _import_engine_metadata(self, metadata: dict[str, Any]) -> None:
        if not isinstance(metadata, dict):
            raise TypeError("metadata must be a dictionary.")

    def export_state(self) -> dict[str, Any]:
        state = EngineState(
            clock=deepcopy(self.clock),
            event_queue=deepcopy(self.event_queue),
            metadata=deepcopy(self._export_engine_metadata()),
        )
        return state.to_dict()

    def import_state(self, payload: dict[str, Any]) -> None:
        state = EngineState.from_dict(payload)
        self.clock = deepcopy(state.clock)
        self.event_queue = deepcopy(state.event_queue)
        self._import_engine_metadata(deepcopy(state.metadata))
