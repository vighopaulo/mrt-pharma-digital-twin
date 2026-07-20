from ui.throughput_monitor import ThroughputMonitor

def test_throughput_monitor():
    monitor = ThroughputMonitor()
    monitor.start(0)
    monitor.record_completion(30,5)
    assert monitor.status()["completed"] == 5
    assert monitor.rate_per_hour() == 10.0
