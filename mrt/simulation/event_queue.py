from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from heapq import heappop, heappush
from itertools import count

from mrt.simulation.event import (
    SimulationEvent,
    SimulationEventStatus,
)


@dataclass(slots=True)
class SimulationEventQueue:
    """
    Priority queue for discrete-event simulation.

    Events are executed chronologically. When timestamps are equal, lower
    numeric priority values execute first. Insertion order is used as a final
    deterministic tie-breaker.
    """

    _heap: list[tuple[datetime, int, int, SimulationEvent]] = field(
        default_factory=list,
        init=False,
        repr=False,
    )
    _sequence: count = field(default_factory=count, init=False, repr=False)

    @property
    def event_count(self) -> int:
        return sum(
            1
            for _, _, _, event in self._heap
            if event.status == SimulationEventStatus.SCHEDULED
        )

    @property
    def is_empty(self) -> bool:
        return self.event_count == 0

    def schedule(self, event: SimulationEvent) -> None:
        if not isinstance(event, SimulationEvent):
            raise TypeError("event must be a SimulationEvent instance.")

        if event.status != SimulationEventStatus.SCHEDULED:
            raise ValueError("only scheduled events can be added to the queue.")

        heappush(
            self._heap,
            (
                event.scheduled_at,
                event.priority,
                next(self._sequence),
                event,
            ),
        )

    def peek(self) -> SimulationEvent:
        self._discard_cancelled()
        if not self._heap:
            raise IndexError("simulation event queue is empty.")
        return self._heap[0][3]

    def pop_next(self) -> SimulationEvent:
        self._discard_cancelled()
        if not self._heap:
            raise IndexError("simulation event queue is empty.")

        _, _, _, event = heappop(self._heap)
        event.mark_executed()
        return event

    def cancel(self, event: SimulationEvent) -> None:
        if not isinstance(event, SimulationEvent):
            raise TypeError("event must be a SimulationEvent instance.")
        event.cancel()

    def clear(self) -> None:
        self._heap.clear()

    def _discard_cancelled(self) -> None:
        while (
            self._heap
            and self._heap[0][3].status
            == SimulationEventStatus.CANCELLED
        ):
            heappop(self._heap)
