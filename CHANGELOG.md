# Build 10.0 — Treatment Plan Entity

## Added

- Initial `TreatmentPlan` domain entity.
- UUID-based treatment-plan identity.
- Direct linkage from a treatment plan to a `Patient`.
- Required treatment name with optional scheduling and notes metadata.
- Explicit treatment-plan lifecycle states.
- Controlled schedule, start, complete, and cancel operations.
- User-facing treatment-plan display label.
- Unit tests for identity, validation, patient linkage, scheduling, display behavior, and lifecycle transitions.
