from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from heapq import heappop, heappush
from itertools import count
from uuid import UUID, uuid4

from mrt.core.entities.room import Room
from mrt.core.entities.transport_request import TransportMode
from mrt.core.entities.transport_route import (
    RouteStatus,
    TransportRoute,
)


class RouteOptimizationCriterion(StrEnum):
    """Supported path-selection objectives."""

    DISTANCE = "distance"
    TRAVEL_TIME = "travel_time"


@dataclass(frozen=True, slots=True)
class TransportPath:
    """Immutable result returned by transport-network path finding."""

    routes: tuple[TransportRoute, ...]
    total_distance_m: float
    total_travel_time_seconds: float

    @property
    def route_count(self) -> int:
        return len(self.routes)

    @property
    def total_travel_time_minutes(self) -> float:
        return self.total_travel_time_seconds / 60.0

    @property
    def room_sequence(self) -> tuple[Room, ...]:
        if not self.routes:
            return ()

        rooms: list[Room] = [self.routes[0].origin_room]
        rooms.extend(route.destination_room for route in self.routes)
        return tuple(rooms)


@dataclass(slots=True)
class TransportNetwork:
    """
    Represents a graph of internal transport routes.

    The network owns route entities and can select an active path between two
    rooms using either total distance or nominal travel time. Congestion,
    capacity reservations, dynamic route weights, and carrier dispatch are
    introduced in later builds.
    """

    name: str
    routes: list[TransportRoute] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("name must be a string.")

        normalized = self.name.strip()
        if not normalized:
            raise ValueError("name cannot be empty or whitespace.")
        self.name = normalized

        initial_routes = list(self.routes)
        self.routes = []
        for route in initial_routes:
            self.add_route(route)

    @property
    def route_count(self) -> int:
        return len(self.routes)

    @property
    def room_count(self) -> int:
        room_ids: set[UUID] = set()
        for route in self.routes:
            room_ids.add(route.origin_room.id)
            room_ids.add(route.destination_room.id)
        return len(room_ids)

    @property
    def display_name(self) -> str:
        return (
            f"{self.name} "
            f"({self.room_count} rooms, {self.route_count} routes)"
        )

    def add_route(self, route: TransportRoute) -> None:
        if not isinstance(route, TransportRoute):
            raise TypeError("route must be a TransportRoute instance.")

        if any(existing.id == route.id for existing in self.routes):
            raise ValueError("transport route is already present.")

        self.routes.append(route)

    def remove_route(self, route_id: UUID) -> TransportRoute:
        for route in self.routes:
            if route.id == route_id:
                self.routes.remove(route)
                return route
        raise KeyError(f"no transport route exists with id {route_id}.")

    def routes_from(
        self,
        room: Room,
        mode: TransportMode | None = None,
        *,
        active_only: bool = True,
    ) -> tuple[TransportRoute, ...]:
        if not isinstance(room, Room):
            raise TypeError("room must be a Room instance.")

        if mode is not None and not isinstance(mode, TransportMode):
            raise TypeError("mode must be a TransportMode or None.")

        matches: list[TransportRoute] = []
        for route in self.routes:
            if active_only and route.status != RouteStatus.ACTIVE:
                continue
            if mode is not None and route.transport_mode != mode:
                continue

            if route.origin_room.id == room.id:
                matches.append(route)
                continue

            if route.is_bidirectional and route.destination_room.id == room.id:
                matches.append(self._reverse_route_view(route))

        return tuple(matches)

    def find_path(
        self,
        origin_room: Room,
        destination_room: Room,
        *,
        mode: TransportMode | None = None,
        criterion: RouteOptimizationCriterion = (
            RouteOptimizationCriterion.TRAVEL_TIME
        ),
    ) -> TransportPath:
        """
        Find the lowest-cost active path using Dijkstra's algorithm.

        Raises KeyError when no compatible active path exists.
        """
        if not isinstance(origin_room, Room):
            raise TypeError("origin_room must be a Room instance.")
        if not isinstance(destination_room, Room):
            raise TypeError("destination_room must be a Room instance.")
        if mode is not None and not isinstance(mode, TransportMode):
            raise TypeError("mode must be a TransportMode or None.")
        if not isinstance(criterion, RouteOptimizationCriterion):
            raise TypeError(
                "criterion must be a RouteOptimizationCriterion."
            )

        if origin_room.id == destination_room.id:
            return TransportPath(
                routes=(),
                total_distance_m=0.0,
                total_travel_time_seconds=0.0,
            )

        queue: list[
            tuple[float, int, UUID, tuple[TransportRoute, ...]]
        ] = []
        sequence = count()
        heappush(
            queue,
            (0.0, next(sequence), origin_room.id, ()),
        )
        best_cost: dict[UUID, float] = {origin_room.id: 0.0}

        while queue:
            cost, _, room_id, path = heappop(queue)

            if cost > best_cost.get(room_id, float("inf")):
                continue

            if room_id == destination_room.id:
                total_distance = sum(
                    route.distance_m for route in path
                )
                total_time = sum(
                    route.nominal_travel_time_seconds for route in path
                )
                return TransportPath(
                    routes=path,
                    total_distance_m=total_distance,
                    total_travel_time_seconds=total_time,
                )

            current_room = self._room_by_id(room_id)
            for route in self.routes_from(
                current_room,
                mode,
                active_only=True,
            ):
                next_room_id = route.destination_room.id
                edge_cost = (
                    route.distance_m
                    if criterion == RouteOptimizationCriterion.DISTANCE
                    else route.nominal_travel_time_seconds
                )
                new_cost = cost + edge_cost

                if new_cost >= best_cost.get(
                    next_room_id,
                    float("inf"),
                ):
                    continue

                best_cost[next_room_id] = new_cost
                heappush(
                    queue,
                    (
                        new_cost,
                        next(sequence),
                        next_room_id,
                        path + (route,),
                    ),
                )

        raise KeyError(
            "no active compatible transport path exists between rooms."
        )

    def _room_by_id(self, room_id: UUID) -> Room:
        for route in self.routes:
            if route.origin_room.id == room_id:
                return route.origin_room
            if route.destination_room.id == room_id:
                return route.destination_room
        raise KeyError(f"no room exists in network with id {room_id}.")

    @staticmethod
    def _reverse_route_view(route: TransportRoute) -> TransportRoute:
        """
        Create a reversed operational view of a bidirectional route.

        The returned object preserves route physics but has its own transient
        identity. It is not added to the network.
        """
        return TransportRoute(
            name=route.name,
            origin_room=route.destination_room,
            destination_room=route.origin_room,
            transport_mode=route.transport_mode,
            distance_m=route.distance_m,
            nominal_speed_m_per_s=route.nominal_speed_m_per_s,
            status=route.status,
            is_bidirectional=True,
        )
