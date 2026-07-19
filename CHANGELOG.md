# Build 20.0 — Transport Network and Path Finding

## Added

- Initial `TransportNetwork` graph entity.
- Ownership and management of `TransportRoute` entities.
- Immutable `TransportPath` result object.
- Active-route traversal with optional transport-mode filtering.
- Multi-segment path finding using Dijkstra's algorithm.
- Distance-minimizing and travel-time-minimizing route selection.
- Bidirectional-route traversal.
- Aggregated route count, room sequence, total distance, and nominal travel time.
- Unit and integration tests for routing, filtering, inactive routes, directionality, and transport-request compatibility.

## Deferred

- Congestion and dynamic route weights.
- Guideway capacity and route reservations.
- Elevators, junction controls, and transfer penalties.
- Carrier assignment and fleet dispatch.
- Real-time rerouting.
