from mrt.simulation.deadlock_recovery import select_deadlock_victim

def test_selects_victim():
    plan=select_deadlock_victim(["b","a"])
    assert plan.victim=="a"
