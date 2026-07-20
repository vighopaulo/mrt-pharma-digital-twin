class StepControl:
    """Controller for advancing one simulation event at a time."""

    def __init__(self):
        self.processed_steps = 0
        self.last_step_result = None

    def step(self, callback=None):
        result = callback() if callback is not None else None
        self.processed_steps += 1
        self.last_step_result = result
        return result

    def reset(self):
        self.processed_steps = 0
        self.last_step_result = None

    def status(self):
        return {
            "processed_steps": self.processed_steps,
            "last_step_result": self.last_step_result,
            "build": "48",
        }
