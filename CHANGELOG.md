# Build 11.0 — Clinical Case Entity

## Added

- Initial `ClinicalCase` domain entity.
- UUID-based clinical-case identity.
- Direct linkage to a `Patient` and that patient's `TreatmentPlan`.
- Explicit inbound, internal, and outbound case origins.
- Created, admitted, in-treatment, completed, and cancelled lifecycle states.
- Optional external case reference.
- Controlled admit, start-treatment, complete, and cancel operations.
- Unit tests for identity, validation, patient-plan consistency, origin handling, display behavior, and lifecycle transitions.

## Deferred

- Clinical-case financial value.
- Accommodation class and private-suite pricing.
- Payer and reimbursement rules.
- Resource reservations and detailed workflow events.
