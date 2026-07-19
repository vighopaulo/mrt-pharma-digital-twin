# Build 14.0 — Radiopharmaceutical Prescription Entity

## Added

- Initial `RadiopharmaceuticalPrescription` domain entity.
- Direct linkage to a `TreatmentPlan` and its patient.
- Prescribed radiopharmaceutical name and activity in MBq.
- Derived activity conversion to GBq.
- Calibration timestamp and administration route.
- Draft, approved, prepared, administered, and cancelled lifecycle states.
- Controlled approve, prepare, administer, and cancel operations.
- Unit tests for identity, validation, linkage, activity conversion, display behavior, and lifecycle transitions.

## Deferred

- Radionuclide physical-decay calculations.
- Production batches and dispensing.
- Dose assay and residual-activity measurements.
- Transport requests and chain of custody.
