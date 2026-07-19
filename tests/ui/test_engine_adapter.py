from ui.engine_adapter import create_engine, read_engine

class FakeQueue:
    def __len__(self):
        return 3

class FakeEngine:
    status = "running"
    current_time = 12.5
    processed_event_count = 8
    event_queue = FakeQueue()

def test_read_engine_normalizes_live_state():
    view = read_engine(FakeEngine())
    assert view.available is True
    assert view.status == "Running"
    assert view.current_time == 12.5
    assert view.processed_events == 8
    assert view.queue_size == 3

def test_read_engine_handles_missing_engine():
    view = read_engine(None)
    assert view.available is False
    assert view.status == "Unavailable"

def test_create_engine_accepts_factory():
    engine, error = create_engine(FakeEngine)
    assert isinstance(engine, FakeEngine)
    assert error == ""

def test_create_engine_reports_factory_failure():
    def failing_factory():
        raise RuntimeError("boom")
    engine, error = create_engine(failing_factory)
    assert engine is None
    assert "RuntimeError: boom" in error
