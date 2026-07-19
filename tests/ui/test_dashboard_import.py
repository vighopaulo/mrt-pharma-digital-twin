"""Import tests for the Build 41 Streamlit dashboard."""

from ui.dashboard import render_dashboard
from ui.layout import configure_page
from ui.sidebar import render_sidebar


def test_dashboard_components_are_callable() -> None:
    assert callable(render_dashboard)
    assert callable(configure_page)
    assert callable(render_sidebar)
