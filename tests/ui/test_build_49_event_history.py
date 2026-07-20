from ui.event_history import EventHistory

def test_event_history():
    h=EventHistory(max_entries=2)
    h.record("arrival",1,"P1")
    h.record("scan",2,"P1")
    h.record("exit",3,"P1")
    assert len(h.recent())==2
    h.clear()
    assert h.status()["recorded_events"]==0
