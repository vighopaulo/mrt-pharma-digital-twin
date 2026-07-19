# Build 12.0 — Workflow Step Entity

## Added

- Initial `WorkflowStep` domain entity.
- UUID-based workflow-step identity.
- Ordered sequence number and planned duration.
- Optional room, equipment, and staff assignments.
- Validation that assigned equipment belongs to the assigned room.
- Pending, ready, in-progress, completed, and cancelled lifecycle states.
- Controlled ready, start, complete, and cancel operations.
- Unit tests for identity, validation, resource assignment, display behavior, and lifecycle transitions.

## Deferred

- Stochastic duration distributions.
- Resource calendars and availability.
- Queueing and waiting-time logic.
- Simulation-event generation.
