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

# Build 31.0 — Multi-Resource Scheduling and Contention Resolution

## Added

- `ResourceRequirement` for named resource quantities.
- `MultiResourceRequest` for atomic multi-resource demand.
- `MultiResourceAllocation` for traceable grouped allocation.
- `MultiResourceScheduler` for all-or-nothing acquisition.
- Priority-aware pending request ordering.
- Contention handling without partial allocation.
- Resource release across all allocated pools.
- Unit and integration tests.

## Deferred

- Deadlock detection across competing reservations.
- Reservation timeouts.
- Calendar-aware multi-resource allocation.
- Simulation-engine events for pending requests.

# Build 32.0 — Deadlock Detection and Reservation Timeouts

## Added

- `ResourceReservation` with timeout and status tracking.
- `ReservationManager` for creation, allocation, expiration, and release.
- Pending-request removal when reservations expire.
- `DeadlockRisk` reporting for blocked requests.
- Deadlock-risk detection across pending multi-resource requests.
- Integration between timeout expiration and deadlock-risk clearing.
- Unit and integration tests.

## Deferred

- Cyclic wait-for graph detection.
- Automatic timeout events in `SimulationEngine`.
- Reservation renewal.
- Preemption and priority escalation.



# Build 33.0 — Cyclic Wait-for Graph Detection

## Added

- `WaitForGraph` directed wait-dependency model.
- Wait-edge addition and removal.
- Node removal and graph inspection.
- Depth-first cycle detection.
- Canonical duplicate-cycle suppression.
- `WaitForCycle` and `CyclicDeadlock` records.
- Integration with deadlock detection helpers.
- Unit and integration tests.

## Deferred

- Automatic graph construction from active allocations.
- Deadlock victim selection.
- Preemption and rollback.
- Simulation-engine deadlock events.


# Build 34.0 — Deadlock Victim Selection and Recovery

## Added
- DeadlockRecoveryPlan model.
- Victim selection helper.
- Deterministic recovery strategy foundation.
- Unit tests.

## Deferred
- Cost-based victim scoring.
- Rollback execution.
- Automatic simulation recovery.

# Build 35.0 — Automatic Rollback and Resource Recovery

## Added
- RollbackManager.
- RollbackAction model.
- Automatic rollback foundation for deadlock recovery.
- Unit tests.

## Deferred
- SimulationEngine integration.
- Transaction checkpoints.
- Partial rollback optimization.

# Build 36.0 — Transaction Checkpoints and State Recovery

## Added
- Checkpoint model.
- CheckpointManager.
- Snapshot creation using deep copies.
- State restoration support.
- Unit tests.

## Deferred
- SimulationEngine integration.
- Incremental checkpoints.
- Persistent checkpoint storage.


# Build 37.0 — Simulation Transactions and Commit/Rollback Integration

## Added

- `TransactionStatus` lifecycle model.
- `SimulationTransaction` coordination layer.
- Transaction checkpoint creation.
- Explicit commit behavior.
- Integrated state restoration and resource rollback.
- Protection against invalid post-commit or post-rollback operations.
- Unit and integration tests.

## Deferred

- Automatic transaction creation inside `SimulationEngine`.
- Nested transactions.
- Transaction event logging.
- Persistent recovery journals.



# Build 38.0 — SimulationEngine Transaction Integration

## Added

- `SupportsSimulationState` protocol.
- `TransactionalSimulationEngine` wrapper.
- Transaction-aware operation execution.
- Automatic checkpoint creation before execution.
- Commit on successful completion.
- Engine-state restoration after failed operations.
- Optional exception propagation after rollback.
- Structured `TransactionExecutionResult`.
- Unit and integration tests.

## Deferred

- Native `SimulationEngine.export_state()` implementation.
- Native `SimulationEngine.import_state()` implementation.
- Transaction-aware event-loop execution.
- Persistent transaction audit logging.


# Build 39.0 — Native SimulationEngine State Export and Import

## Added

- `EngineState` snapshot model.
- Deep-copy state serialization.
- Required-field validation during restoration.
- `SimulationEngineStateMixin`.
- Native `export_state()` behavior.
- Native `import_state()` behavior.
- Extension hooks for engine-specific metadata.
- Unit and integration tests.

## Integration Note

Add `SimulationEngineStateMixin` as a base class of the existing
`SimulationEngine`, or copy its export/import methods into the engine
after adapting the attribute names if the engine does not use
`clock` and `event_queue`.

## Deferred

- JSON snapshot persistence.
- Snapshot schema versioning.
- Persistent restart files.
- Incremental snapshots.

# Build 40.0 — Automatic Simulation Snapshots

## Added

- `SimulationSnapshot` immutable snapshot model.
- `SimulationSnapshotManager`.
- Configurable snapshot intervals.
- Automatic snapshot capture when a trigger value is due.
- Duplicate-trigger protection.
- Configurable retention policy.
- Latest-snapshot access.
- Unit and integration tests.

## Deferred

- Persistent JSON snapshot files.
- Automatic hooks inside `SimulationEngine.run()`.
- Snapshot restore and resume.
- Snapshot schema migration.
