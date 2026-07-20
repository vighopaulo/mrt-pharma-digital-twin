from ui.simulation_controls import SimulationControls

def test_controls():
 c=SimulationControls();c.start();assert c.status()['simulation_state']=='running';c.pause();assert c.status()['simulation_state']=='paused';c.reset();assert c.status()['simulation_state']=='stopped'
