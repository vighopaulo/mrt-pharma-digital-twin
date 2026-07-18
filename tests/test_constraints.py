from core.decision_constraints import DecisionConstraint
from core.enums import ConstraintSense

def test_maximum_constraint() -> None:
    c = DecisionConstraint("CAPEX ceiling", ConstraintSense.MAXIMUM, 50_000_000, "USD")
    assert c.is_satisfied(49_000_000)
    assert not c.is_satisfied(51_000_000)
