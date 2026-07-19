# Build 23.0 – Stochastic Duration Distributions

## Added
- Reproducible `SimulationRandomSource`.
- Fixed, uniform, triangular, and truncated-normal duration distributions.
- Validation of distribution parameters.
- Deterministic seeded random sequences.
- Unit tests for bounds, validation, and reproducibility.
- Integration test for a seeded stochastic workflow.

---

# Build 24.0 – Arrival Process Framework

## Added
- Initial `ArrivalProcess` framework.
- Initial `ArrivalDistribution` abstraction.
- Deterministic arrival scheduling.
- Stochastic inter-arrival scheduling.
- Integration with the simulation event queue.
- Unit and integration tests.

## Deferred
- Resource queues and contention.
- Metrics collection and utilization.
- Pause, resume, and simulation checkpoints.

# Build 25.0 — Resource Queue Management

## Added

- `ResourceQueue` for constrained-resource waiting lines.
- FIFO and priority queue disciplines.
- Queue-capacity enforcement.
- Waiting-time calculation.
- Maximum queue-length tracking.
- `ResourcePool` and `ResourceUnit` allocation models.
- Resource acquisition, exhaustion, and release behavior.
- Unit and integration tests for queueing and resource assignment.

## Deferred

- Automatic queue-to-resource dispatch events.
- Resource calendars and availability windows.
- Queue metrics aggregation and utilization reporting.
- Multi-resource acquisition and deadlock prevention.