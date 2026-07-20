from .speed_control import SpeedControl

def render_dashboard():
    s=SpeedControl();print(s.status())
