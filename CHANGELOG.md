# Build 19.0 — Transport Route Entity

## Added

- Initial `TransportRoute` domain entity.
- UUID-based route identity.
- Directed or bidirectional connection between two rooms.
- Route distance and nominal operating speed.
- Nominal travel-time calculation in seconds and minutes.
- Manual, pneumatic, and MRT route modes.
- Active, inactive, and maintenance availability states.
- Directional connectivity and transport-mode compatibility checks.
- Unit tests for identity, validation, timing, directionality, display behavior, and availability.

## Deferred

- Multi-segment route networks.
- Graph-based shortest-path routing.
- Junctions, elevators, and vertical transitions.
- Congestion and dynamic travel times.
- Carrier assignment and route reservations.
