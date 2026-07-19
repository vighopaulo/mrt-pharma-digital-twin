from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class EngineState:
    """Serializable snapshot of SimulationEngine execution state."""

    clock: Any
    event_queue: Any
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "clock": deepcopy(self.clock),
            "event_queue": deepcopy(self.event_queue),
            "metadata": deepcopy(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "EngineState":
        if not isinstance(payload, Mapping):
            raise TypeError("payload must be a mapping.")

        required = {"clock", "event_queue", "metadata"}
        missing = required.difference(payload)
        if missing:
            raise ValueError(
                f"engine state is missing required fields: {sorted(missing)}"
            )

        metadata = payload["metadata"]
        if not isinstance(metadata, dict):
            raise TypeError("metadata must be a dictionary.")

        return cls(
            clock=deepcopy(payload["clock"]),
            event_queue=deepcopy(payload["event_queue"]),
            metadata=deepcopy(metadata),
        )
