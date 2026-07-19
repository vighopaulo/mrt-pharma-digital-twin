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


# Build 26.0 — Automatic Resource Dispatch

## Added

- `ResourceDispatcher` for automatic queue-to-resource assignment.
- `ResourceAssignment` records for traceable allocation history.
- Single and bulk dispatch operations.
- Automatic assignment when a resource is released.
- Waiting-time capture at the point of assignment.
- Entity-to-assignment lookup.
- Unit and integration tests for dispatch behavior.

## Deferred

- Resource calendars and shift availability.
- Dispatch event generation inside `SimulationEngine`.
- Multi-resource acquisition.
- Deadlock prevention and reservation policies.


# Build 27.0 — Resource Calendars and Availability

## Added

- `ResourceCalendar` for weekly operating schedules.
- `DailyOperatingWindow` for regular hours.
- `AvailabilityWindow` for overrides.
- Available, unavailable, and maintenance states.
- Support for after-hours and weekend closure.
- Support for emergency opening windows.
- Unit and integration tests for schedule-aware dispatch.

## Deferred

- Calendar-aware dispatch inside `ResourceDispatcher`.
- Staff shifts and break schedules.
- Holiday calendars.
- Recurring maintenance rules.

# Build 28.0 — Calendar-Aware Resource Dispatch

## Added

- Optional `ResourceCalendar` linkage in `ResourceDispatcher`.
- Dispatch eligibility checks against operating schedules.
- Automatic blocking during after-hours and maintenance periods.
- Queue preservation when dispatch is unavailable.
- Resource release without reassignment during closed periods.
- Deferred assignment when the calendar reopens.
- Unit and integration tests for calendar-aware dispatch.

## Deferred

- Automatic next-opening-time calculation.
- Staff shifts and break schedules.
- Holiday calendars.
- Simulation events for opening and closing resources.

# Build 29.0 — Next Availability and Reopening Events

## Added

- `ResourceCalendar.next_available_at()` calculation.
- Search across future operating days.
- Weekend and after-hours reopening logic.
- Emergency availability override support.
- `ResourceReopening` value object.
- Reopening calculation helper.
- Unit and integration tests for delayed dispatch at reopening.

## Deferred

- Automatic scheduling of reopening events in `SimulationEngine`.
- Holiday calendars.
- Recurring maintenance rules.
- Time-zone-aware resource calendars.

