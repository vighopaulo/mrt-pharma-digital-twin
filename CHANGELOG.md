# Build 21.0 — Simulation Clock and Event Queue

## Added

- Initial `SimulationEvent` entity.
- Deterministic event ordering by time, priority, and insertion order.
- Event payload support for simulation data.
- Scheduled, executed, and cancelled event states.
- Initial `SimulationEventQueue` priority queue.
- Event scheduling, peeking, cancellation, and chronological execution.
- Initial `SimulationClock` with forward-only time advancement.
- Unit tests for event validation, deterministic ordering, cancellation, execution, and clock behavior.

## Deferred

- Event handlers and simulation engine loop.
- Metrics collection.
- Random variate generation.
- Resource queues and utilization tracking.
- Pause, resume, and simulation checkpoints.
