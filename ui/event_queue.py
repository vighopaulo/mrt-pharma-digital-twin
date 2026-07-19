"""Read-only event queue monitor for the Streamlit dashboard."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Iterable

import streamlit as st


def _event_queue(engine: Any) -> Iterable[Any]:
    """Return the first event queue exposed by the engine."""
    if engine is None:
        return ()

    for name in ("event_queue", "queue", "_event_queue", "events"):
        if not hasattr(engine, name):
            continue

        queue = getattr(engine, name)

        if callable(queue):
            try:
                queue = queue()
            except TypeError:
                continue

        if queue is None:
            continue

        if hasattr(queue, "queue"):
            queue = getattr(queue, "queue")

        try:
            return tuple(queue)
        except TypeError:
            continue

    return ()


def _event_value(event: Any, names: tuple[str, ...], default: Any = "") -> Any:
    """Read an event attribute or dictionary value using common names."""
    if isinstance(event, dict):
        for name in names:
            if name in event:
                return event[name]
        return default

    for name in names:
        if hasattr(event, name):
            value = getattr(event, name)
            if callable(value):
                try:
                    value = value()
                except TypeError:
                    continue
            return value

    return default


def event_rows(engine: Any, limit: int = 25) -> list[dict[str, Any]]:
    """Normalize pending events into table rows."""
    rows: list[dict[str, Any]] = []

    for index, event in enumerate(_event_queue(engine)):
        if index >= limit:
            break

        if is_dataclass(event):
            raw = asdict(event)
        elif isinstance(event, dict):
            raw = event
        else:
            raw = {}

        rows.append(
            {
                "Position": index + 1,
                "Time": _event_value(
                    event,
                    ("time", "timestamp", "scheduled_time", "event_time"),
                    raw.get("time", ""),
                ),
                "Priority": _event_value(
                    event,
                    ("priority", "rank"),
                    raw.get("priority", ""),
                ),
                "Event Type": _event_value(
                    event,
                    ("event_type", "type", "name", "kind"),
                    type(event).__name__,
                ),
                "Entity": _event_value(
                    event,
                    ("entity_id", "patient_id", "resource_id", "entity"),
                    "",
                ),
            }
        )

    return rows


def render_event_queue(engine: Any, limit: int = 25) -> None:
    """Render a live read-only view of pending simulation events."""
    st.subheader("Live Event Queue")

    rows = event_rows(engine, limit=limit)

    if not rows:
        st.info("No pending events are currently available.")
        return

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        f"Showing {len(rows)} pending event"
        f"{'s' if len(rows) != 1 else ''}; read-only monitor."
    )
