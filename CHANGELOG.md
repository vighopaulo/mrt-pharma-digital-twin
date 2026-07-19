# Build 16.0 — Radiopharmaceutical Batch Entity

## Added

- Initial `RadiopharmaceuticalBatch` radiation-domain entity.
- UUID-based batch identity and normalized batch number.
- Direct linkage to a `Radionuclide`.
- Product name, produced time, calibration time, and optional expiry time.
- Calibrated initial activity in MBq.
- Remaining activity and remaining-fraction calculations at a requested time.
- Created, released, depleted, expired, and cancelled lifecycle states.
- Unit tests for identity, validation, decay integration, expiration, display behavior, and lifecycle transitions.

## Deferred

- Production equipment and cyclotron linkage.
- Quality-control records and release criteria.
- Dose dispensing and inventory deductions.
- Transport requests and chain of custody.
