# Build 22.0 — Simulation Engine Loop and Event Handlers

## Added

- Initial `SimulationEngine`.
- Event-handler registration.
- Deterministic `step()` execution.
- Continuous `run()` execution.
- Optional end-time and maximum-event limits.
- Automatic simulation-clock advancement.
- Follow-up event scheduling from handlers.
- Unit and integration tests for event execution and chaining.

## Deferred

- Random variate generation.
- Resource queues and contention.
- Metrics collection.
- Pause, resume, and checkpoints.
