# Build 13.0 — Clinical Workflow Entity

## Added

- Initial `ClinicalWorkflow` domain entity.
- Direct linkage from a workflow to a `ClinicalCase`.
- Ordered ownership of `WorkflowStep` entities.
- Duplicate-sequence protection and deterministic step ordering.
- Planned-duration aggregation across all workflow steps.
- Controlled draft, ready, in-progress, completed, and cancelled states.
- Sequential workflow execution with automatic activation of the next step.
- Unit and integration tests for ordering, validation, execution, duration, and case-workflow coordination.

## Deferred

- Simulation timestamps and event generation.
- Stochastic durations.
- Resource contention and queueing.
- Workflow branching and parallel activities.
