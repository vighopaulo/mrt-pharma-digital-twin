from mrt.simulation.checkpoint_manager import CheckpointManager

def test_checkpoint_restore():
    mgr=CheckpointManager()
    state={"scanner":"busy","queue":[1,2]}
    mgr.create("cp1",state)
    state["queue"].append(3)
    restored=mgr.restore("cp1")
    assert restored["queue"]==[1,2]
