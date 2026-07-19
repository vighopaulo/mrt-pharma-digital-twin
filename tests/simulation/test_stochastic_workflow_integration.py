from datetime import datetime, timedelta

from mrt.simulation.clock import SimulationClock
from mrt.simulation.duration_distribution import DurationDistribution
from mrt.simulation.engine import SimulationEngine
from mrt.simulation.event import SimulationEvent
from mrt.simulation.random_source import SimulationRandomSource


def test_seeded_stochastic_workflow_is_reproducible() -> None:
    start = datetime(2026, 7, 19, 8, 0)
    duration = DurationDistribution.uniform(300, 600)

    def run_once() -> list[datetime]:
        random_source = SimulationRandomSource(seed=77)
        engine = SimulationEngine(SimulationClock(start))
        timeline: list[datetime] = []

        def arrival(
            event: SimulationEvent,
            active_engine: SimulationEngine,
        ) -> None:
            timeline.append(active_engine.clock.current_time)
            sampled_seconds = duration.sample_seconds(
                random_source.random
            )
            active_engine.schedule(
                SimulationEvent(
                    scheduled_at=event.scheduled_at
                    + timedelta(seconds=sampled_seconds),
                    priority=1,
                    event_type="complete",
                )
            )

        def complete(
            _: SimulationEvent,
            active_engine: SimulationEngine,
        ) -> None:
            timeline.append(active_engine.clock.current_time)

        engine.register_handler("arrival", arrival)
        engine.register_handler("complete", complete)
        engine.schedule(
            SimulationEvent(
                scheduled_at=start,
                priority=1,
                event_type="arrival",
            )
        )
        engine.run()
        return timeline

    assert run_once() == run_once()
