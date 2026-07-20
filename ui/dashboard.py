from ui.throughput_monitor import ThroughputMonitor

def render_dashboard():
    monitor = ThroughputMonitor()
    print(monitor.status())
