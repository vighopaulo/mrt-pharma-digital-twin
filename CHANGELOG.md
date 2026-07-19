# Build 18.0 — Transport Request Entity

## Added

- Initial `TransportRequest` domain entity.
- Direct linkage to a patient-specific radiopharmaceutical dose.
- Origin room, destination room, requested time, and priority.
- Manual, pneumatic, and MRT transport modes.
- Created, dispatched, in-transit, delivered, and cancelled lifecycle states.
- Dispatch and delivery timestamps with completed transport-duration calculation.
- Coordination of dose state with transport-request state.
- Unit tests for linkage, validation, timing, display behavior, and lifecycle transitions.

## Deferred

- Route and guideway selection.
- Travel-time prediction.
- Carrier assignment and fleet capacity.
- Chain-of-custody event history.
- Transport-related decay and radiation exposure.
