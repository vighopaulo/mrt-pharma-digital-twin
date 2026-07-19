"""Main dashboard view for the MRT Pharma Digital Twin."""
import streamlit as st
from ui.engine_adapter import EngineView

def render_dashboard(view: EngineView) -> None:
    st.title("MRT Pharma Digital Twin")
    st.caption("Engineering simulation and operational decision-support platform")
    a, b, c, d = st.columns(4)
    a.metric("Simulation Status", view.status)
    b.metric("Current Time", f"{view.current_time:,.2f} min")
    c.metric("Processed Events", f"{view.processed_events:,}")
    d.metric("Event Queue Size", f"{view.queue_size:,}")
    st.subheader("Simulation Controls")
    x, y, z = st.columns(3)
    with x:
        st.button("▶ Start", use_container_width=True, disabled=True)
    with y:
        st.button("⏸ Pause", use_container_width=True, disabled=True)
    with z:
        st.button("↻ Reset", use_container_width=True, disabled=True)
    if view.available:
        st.success("SimulationEngine connected in read-only mode.")
    else:
        st.warning(view.message or "SimulationEngine is unavailable.")
    st.caption("Interactive controls are enabled in Build 45.")
