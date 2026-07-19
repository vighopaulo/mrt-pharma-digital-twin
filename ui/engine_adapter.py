"""Read-only adapter between Streamlit and the simulation engine."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable

@dataclass(frozen=True)
class EngineView:
    status: str
    current_time: float
    processed_events: int
    queue_size: int
    available: bool = True
    message: str = ""

def _first_value(obj: Any, names: tuple[str, ...], default: Any) -> Any:
    for name in names:
        if hasattr(obj, name):
            value = getattr(obj, name)
            if callable(value):
                try:
                    value = value()
                except TypeError:
                    continue
            if value is not None:
                return value
    return default

def _queue_size(engine: Any) -> int:
    direct = _first_value(engine, ("event_queue_size", "queue_size", "pending_event_count"), None)
    if direct is not None:
        try:
            return int(direct)
        except (TypeError, ValueError):
            pass
    queue = _first_value(engine, ("event_queue", "queue", "_event_queue", "events"), None)
    if queue is None:
        return 0
    try:
        return len(queue)
    except TypeError:
        pass
    for name in ("qsize", "size"):
        method = getattr(queue, name, None)
        if callable(method):
            try:
                return int(method())
            except (TypeError, ValueError):
                pass
    return 0

def read_engine(engine: Any) -> EngineView:
    if engine is None:
        return EngineView("Unavailable", 0.0, 0, 0, False, "SimulationEngine could not be initialized.")
    status = str(_first_value(engine, ("status", "state", "simulation_status"), "Ready")).title()
    current_time = _first_value(engine, ("current_time", "simulation_time", "now", "time"), 0.0)
    processed = _first_value(engine, ("processed_event_count", "processed_events", "event_count"), 0)
    try:
        current_time = float(current_time)
    except (TypeError, ValueError):
        current_time = 0.0
    try:
        processed = int(processed)
    except (TypeError, ValueError):
        processed = 0
    return EngineView(status, current_time, processed, _queue_size(engine))

def create_engine(factory: Callable[[], Any] | None = None) -> tuple[Any | None, str]:
    try:
        if factory is not None:
            return factory(), ""
        from mrt.simulation.engine import SimulationEngine
        return SimulationEngine(), ""
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"
