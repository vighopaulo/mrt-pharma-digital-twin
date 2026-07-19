from datetime import datetime, timedelta

import pytest

from mrt.simulation.clock import SimulationClock


def test_clock_advances_to_target_time() -> None:
    clock = SimulationClock(datetime(2026, 7, 19, 8, 0))

    clock.advance_to(datetime(2026, 7, 19, 9, 0))

    assert clock.current_time == datetime(2026, 7, 19, 9, 0)


def test_clock_advances_by_duration() -> None:
    clock = SimulationClock(datetime(2026, 7, 19, 8, 0))

    clock.advance_by(timedelta(minutes=30))

    assert clock.current_time == datetime(2026, 7, 19, 8, 30)


def test_clock_cannot_move_backward() -> None:
    clock = SimulationClock(datetime(2026, 7, 19, 8, 0))

    with pytest.raises(ValueError):
        clock.advance_to(datetime(2026, 7, 19, 7, 59))
