from ui.step_control import StepControl


def test_single_step_increments_counter():
    controller = StepControl()
    controller.step()
    assert controller.status()["processed_steps"] == 1


def test_step_returns_and_records_callback_result():
    controller = StepControl()
    result = controller.step(lambda: "event-processed")
    assert result == "event-processed"
    assert controller.status()["last_step_result"] == "event-processed"


def test_reset_clears_step_state():
    controller = StepControl()
    controller.step(lambda: 42)
    controller.reset()
    assert controller.status()["processed_steps"] == 0
    assert controller.status()["last_step_result"] is None
