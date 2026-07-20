from ui.event_history import EventHistory

def render_dashboard():
    history=EventHistory()
    print(history.status())
