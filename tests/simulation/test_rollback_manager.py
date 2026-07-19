from mrt.simulation.rollback_manager import RollbackManager

def test_rollback_actions_created():
    actions=RollbackManager().rollback(["PET-1","Tech-1"])
    assert len(actions)==2
    assert actions[0].reason=="deadlock recovery"
