"""Main dashboard view for the MRT Pharma Digital Twin."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.engine_adapter import EngineView
from ui.event_queue import render_event_queue


def render_dashboard(view: EngineView, engine: Any = None) -> None:
    """Render live simulation state and the pending-event monitor."""
    st.title("MRT Pharma Digital Twin")
    st.caption("Engineering simulation and operational decision-support platform")

    status_col, time_col, processed_col, queue_col = st.columns(4)
    status_col.metric("Simulation Status", view.status)
    time_col.metric("Current Time", f"{view.current_time:,.2f} min")
    processed_col.metric("Processed Events", f"{view.processed_events:,}")
    queue_col.metric("Event Queue Size", f"{view.queue_size:,}")

    st.subheader("Simulation Controls")
    start_col, pause_col, reset_col = st.columns(3)

    with start_col:
        st.button("▶ Start", use_container_width=True, disabled=True)
    with pause_col:
        st.button("⏸ Pause", use_container_width=True, disabled=True)
    with reset_col:
        st.button("↻ Reset", use_container_width=True, disabled=True)

    if view.available:
        st.success("SimulationEngine connected in read-only mode.")
    else:
        st.warning(view.message or "SimulationEngine is unavailable.")

    render_event_queue(engine)
    st.caption("Interactive controls are enabled in Build 45.")
