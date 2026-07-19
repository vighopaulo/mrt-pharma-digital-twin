"""Streamlit entry point for the MRT Pharma Digital Twin."""

from __future__ import annotations

import streamlit as st

from ui.dashboard import render_dashboard
from ui.engine_adapter import create_engine, read_engine
from ui.layout import configure_page
from ui.sidebar import render_sidebar


def _session_engine():
    """Create one engine instance per Streamlit session."""
    if "simulation_engine" not in st.session_state:
        engine, error = create_engine()
        st.session_state.simulation_engine = engine
        st.session_state.simulation_engine_error = error
    return st.session_state.simulation_engine


def main() -> None:
    """Run the Streamlit application."""
    configure_page()
    selected_page = render_sidebar()

    engine = _session_engine()
    view = read_engine(engine)

    if not view.available and st.session_state.get("simulation_engine_error"):
        view = type(view)(
            status=view.status,
            current_time=view.current_time,
            processed_events=view.processed_events,
            queue_size=view.queue_size,
            available=False,
            message=st.session_state.simulation_engine_error,
        )

    if selected_page == "Dashboard":
        render_dashboard(view, engine)


if __name__ == "__main__":
    main()
