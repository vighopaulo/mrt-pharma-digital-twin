from ui.metrics_recorder import MetricsRecorder

def test_metrics_recorder():
    r=MetricsRecorder()
    r.record("queue",1,5)
    r.record("queue",2,3)
    assert r.latest("queue")["value"]==3.0
    r.clear()
    assert r.status()["sample_count"]==0
