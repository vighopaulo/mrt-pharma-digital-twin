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
