from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4

from mrt.core.entities.room import Room
from mrt.core.entities.transport_request import TransportMode


class RouteStatus(StrEnum):
    """Operational availability states for a transport route."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


@dataclass(slots=True)
class TransportRoute:
    """
    Represents one directed internal transport connection between two rooms.

    The route records distance, supported transport mode, nominal speed,
    and operational availability. Network graphs, intersections, vertical
    transitions, congestion, and dynamic routing are introduced later.
    """

    name: str
    origin_room: Room
    destination_room: Room
    transport_mode: TransportMode
    distance_m: float
    nominal_speed_m_per_s: float
    status: RouteStatus = RouteStatus.ACTIVE
    is_bidirectional: bool = False
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.name = self._normalize_required(self.name, "name")

        if not isinstance(self.origin_room, Room):
            raise TypeError("origin_room must be a Room instance.")

        if not isinstance(self.destination_room, Room):
            raise TypeError("destination_room must be a Room instance.")

        if self.origin_room.id == self.destination_room.id:
            raise ValueError(
                "origin_room and destination_room must be different."
            )

        if not isinstance(self.transport_mode, TransportMode):
            raise TypeError("transport_mode must be a TransportMode.")

        self.distance_m = self._validate_positive_number(
            self.distance_m,
            "distance_m",
        )
        self.nominal_speed_m_per_s = self._validate_positive_number(
            self.nominal_speed_m_per_s,
            "nominal_speed_m_per_s",
        )

        if not isinstance(self.status, RouteStatus):
            raise TypeError("status must be a RouteStatus.")

        if not isinstance(self.is_bidirectional, bool):
            raise TypeError("is_bidirectional must be a boolean.")

    @staticmethod
    def _normalize_required(value: str, field_name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string.")

        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field_name} cannot be empty or whitespace.")

        return normalized

    @staticmethod
    def _validate_positive_number(value: float, field_name: str) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{field_name} must be a number.")

        normalized = float(value)
        if normalized <= 0:
            raise ValueError(f"{field_name} must be greater than zero.")

        return normalized

    @property
    def nominal_travel_time_seconds(self) -> float:
        """Return uncongested travel time using nominal route speed."""
        return self.distance_m / self.nominal_speed_m_per_s

    @property
    def nominal_travel_time_minutes(self) -> float:
        """Return uncongested travel time in minutes."""
        return self.nominal_travel_time_seconds / 60.0

    @property
    def display_name(self) -> str:
        direction = "↔" if self.is_bidirectional else "→"
        return (
            f"{self.name}: {self.origin_room.name} {direction} "
            f"{self.destination_room.name} "
            f"[{self.transport_mode.value}/{self.status.value}]"
        )

    def connects(self, origin_room: Room, destination_room: Room) -> bool:
        """Return whether this route can serve the requested direction."""
        if not isinstance(origin_room, Room):
            raise TypeError("origin_room must be a Room instance.")
        if not isinstance(destination_room, Room):
            raise TypeError("destination_room must be a Room instance.")

        direct_match = (
            self.origin_room.id == origin_room.id
            and self.destination_room.id == destination_room.id
        )
        reverse_match = (
            self.is_bidirectional
            and self.origin_room.id == destination_room.id
            and self.destination_room.id == origin_room.id
        )
        return direct_match or reverse_match

    def activate(self) -> None:
        """Return the route to active service."""
        self.status = RouteStatus.ACTIVE

    def deactivate(self) -> None:
        """Mark the route unavailable for operations."""
        self.status = RouteStatus.INACTIVE

    def place_in_maintenance(self) -> None:
        """Mark the route unavailable due to maintenance."""
        self.status = RouteStatus.MAINTENANCE

    def can_accept_transport(self, mode: TransportMode) -> bool:
        """Return whether the route is active and supports the given mode."""
        if not isinstance(mode, TransportMode):
            raise TypeError("mode must be a TransportMode.")

        return (
            self.status == RouteStatus.ACTIVE
            and self.transport_mode == mode
        )
