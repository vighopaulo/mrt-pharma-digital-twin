from ui.resource_monitor import get_resource_snapshot

def test_snapshot():
    s = get_resource_snapshot()
    assert s["resource_monitor"] == "active"
