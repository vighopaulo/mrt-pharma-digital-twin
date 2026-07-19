# Build 17.0 — Radiopharmaceutical Dose Entity

## Added

- Initial `RadiopharmaceuticalDose` radiation-domain entity.
- UUID-based patient-dose identity and normalized dose reference.
- Direct linkage to a `RadiopharmaceuticalPrescription`, patient, and production batch.
- Dispensed activity and dispensing timestamp.
- Validation that dispensed activity does not exceed batch activity available at dispensing.
- Remaining patient-dose activity calculation after dispensing.
- Dispensed, released, in-transit, received, administered, and cancelled lifecycle states.
- Unit tests for linkage, validation, dose decay, display behavior, and lifecycle transitions.

## Deferred

- Batch inventory deductions.
- Dose assay and residual-activity measurements.
- Transport request linkage and chain-of-custody events.
- Radiation exposure calculations.
