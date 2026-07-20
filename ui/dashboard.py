from ui.metrics_recorder import MetricsRecorder

def render_dashboard():
    recorder=MetricsRecorder()
    print(recorder.status())
