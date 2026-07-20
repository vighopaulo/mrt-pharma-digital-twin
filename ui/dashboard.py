from .step_control import StepControl


def render_dashboard():
    controller = StepControl()
    print(controller.status())
