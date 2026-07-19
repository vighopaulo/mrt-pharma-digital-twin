from mrt.simulation.deadlock_detector import detect_cyclic_deadlocks


def test_detects_cyclic_deadlock() -> None:
    deadlocks = detect_cyclic_deadlocks(
        (
            ("patient-1", "patient-2"),
            ("patient-2", "patient-1"),
        )
    )

    assert len(deadlocks) == 1


def test_returns_empty_for_noncyclic_waits() -> None:
    deadlocks = detect_cyclic_deadlocks(
        (
            ("patient-1", "patient-2"),
            ("patient-2", "patient-3"),
        )
    )

    assert deadlocks == ()
