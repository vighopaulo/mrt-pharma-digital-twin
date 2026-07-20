from ui.time_control import TimeControl

def test_time_control():
    tc=TimeControl()
    tc.advance(5)
    assert tc.status()["simulation_time"]==5.0
    tc.reset()
    assert tc.status()["simulation_time"]==0.0
