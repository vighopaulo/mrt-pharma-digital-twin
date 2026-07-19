"""Streamlit entry point for the MRT Pharma Digital Twin."""

from ui.dashboard import render_dashboard
from ui.layout import configure_page
from ui.sidebar import render_sidebar


def main() -> None:
    """Run the Streamlit application."""
    configure_page()
    selected_page = render_sidebar()

    if selected_page == "Dashboard":
        render_dashboard()


if __name__ == "__main__":
    main()
