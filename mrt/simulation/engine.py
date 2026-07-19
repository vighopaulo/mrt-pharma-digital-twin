from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from mrt.simulation.clock import SimulationClock
from mrt.simulation.event import SimulationEvent
from mrt.simulation.event_queue import SimulationEventQueue
from mrt.simulation.simulation_engine_state import (
    SimulationEngineStateMixin,
)

EventHandler = Callable[[SimulationEvent, "SimulationEngine"], None]

@dataclass(slots=True)
class SimulationEngine(SimulationEngineStateMixin):
    clock: SimulationClock
    event_queue: SimulationEventQueue = field(default_factory=SimulationEventQueue)
    _handlers: dict[str, EventHandler] = field(default_factory=dict, init=False, repr=False)
    processed_event_count: int = field(default=0, init=False)
    is_running: bool = field(default=False, init=False)

    def _export_engine_metadata(self) -> dict:
        return {
            "processed_event_count": self.processed_event_count,
            "is_running": self.is_running,
        }

    def _import_engine_metadata(self, metadata: dict) -> None:
        super()._import_engine_metadata(metadata)
        self.processed_event_count = metadata["processed_event_count"]
        self.is_running = metadata["is_running"]

    def register_handler(self, event_type: str, handler: EventHandler) -> None:
        event_type = event_type.strip()
        if not event_type:
            raise ValueError("event_type cannot be empty.")
        if not callable(handler):
            raise TypeError("handler must be callable.")
        if event_type in self._handlers:
            raise ValueError(f"handler already registered for {event_type}.")
        self._handlers[event_type] = handler

    def schedule(self, event: SimulationEvent) -> None:
        if event.scheduled_at < self.clock.current_time:
            raise ValueError("cannot schedule an event in the past.")
        self.event_queue.schedule(event)

    def step(self) -> SimulationEvent:
        event = self.event_queue.peek()
        handler = self._handlers.get(event.event_type)
        if handler is None:
            raise KeyError(f"no handler registered for {event.event_type}.")
        event = self.event_queue.pop_next()
        self.clock.advance_to(event.scheduled_at)
        handler(event, self)
        self.processed_event_count += 1
        return event

    def run(self, until: datetime | None = None, max_events: int | None = None) -> int:
        if until is not None and until < self.clock.current_time:
            raise ValueError("until cannot be earlier than current time.")
        if max_events is not None and max_events < 0:
            raise ValueError("max_events cannot be negative.")
        processed = 0
        self.is_running = True
        try:
            while not self.event_queue.is_empty:
                if max_events is not None and processed >= max_events:
                    break
                if until is not None and self.event_queue.peek().scheduled_at > until:
                    break
                self.step()
                processed += 1
            if until is not None and self.clock.current_time < until:
                self.clock.advance_to(until)
        finally:
            self.is_running = False
        return processed
