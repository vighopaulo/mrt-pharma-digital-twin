from .resource_monitor import get_resource_snapshot

def render_dashboard():
    snapshot = get_resource_snapshot()
    print("=== Resource Monitor ===")
    for k,v in snapshot.items():
        print(f"{k}: {v}")
