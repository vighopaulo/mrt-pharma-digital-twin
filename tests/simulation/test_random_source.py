from mrt.simulation.random_source import SimulationRandomSource


def test_reset_reproduces_original_sequence() -> None:
    source = SimulationRandomSource(seed=123)
    first = [source.random.random() for _ in range(5)]

    source.reset()
    second = [source.random.random() for _ in range(5)]

    assert first == second


def test_reseed_changes_sequence() -> None:
    source = SimulationRandomSource(seed=123)
    first = [source.random.random() for _ in range(3)]

    source.reseed(456)
    second = [source.random.random() for _ in range(3)]

    assert first != second
