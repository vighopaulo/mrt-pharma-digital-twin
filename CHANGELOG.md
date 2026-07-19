# Build 15.0 — Radionuclide Entity and Decay Model

## Added

- Immutable `Radionuclide` radiation-domain entity.
- Radionuclide symbol, name, and half-life in minutes.
- Radioactive decay constant calculation.
- Remaining-activity fraction after elapsed time.
- Remaining activity calculation in MBq.
- Inverse calculation for time required to reach a target fraction.
- Unit tests for half-life behavior, activity decay, validation, immutability, and display formatting.

## Deferred

- Standard radionuclide knowledge library.
- Linkage from prescriptions to radionuclide objects.
- Decay during production, dispensing, transport, and patient workflow.
- Daughter products and multi-stage decay chains.
