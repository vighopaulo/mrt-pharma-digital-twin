from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from mrt.core.entities.room import Room
from mrt.radiation.entities.radiopharmaceutical_dose import (
    RadiopharmaceuticalDose,
)


class TransportMode(StrEnum):
    """Supported internal transport modes."""

    MANUAL = "manual"
    PNEUMATIC = "pneumatic"
    MRT = "mrt"


class TransportRequestStatus(StrEnum):
    """Lifecycle states for one dose-transport request."""

    CREATED = "created"
    DISPATCHED = "dispatched"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class TransportRequest:
    """
    Represents one internal request to move a patient-specific dose.

    The request links a dose to an origin room, destination room, selected
    transport mode, timestamps, and lifecycle state. Routing, travel-time
    estimation, carrier assignment, chain-of-custody events, and exposure
    calculations are introduced in later builds.
    """

    dose: RadiopharmaceuticalDose
    origin_room: Room
    destination_room: Room
    transport_mode: TransportMode
    requested_at: datetime
    priority: int = 3
    status: TransportRequestStatus = TransportRequestStatus.CREATED
    dispatched_at: datetime | None = None
    delivered_at: datetime | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.dose, RadiopharmaceuticalDose):
            raise TypeError(
                "dose must be a RadiopharmaceuticalDose instance."
            )

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

        if not isinstance(self.requested_at, datetime):
            raise TypeError("requested_at must be a datetime.")

        if isinstance(self.priority, bool) or not isinstance(
            self.priority,
            int,
        ):
            raise TypeError("priority must be an integer.")

        if not 1 <= self.priority <= 5:
            raise ValueError("priority must be between 1 and 5.")

        if not isinstance(self.status, TransportRequestStatus):
            raise TypeError(
                "status must be a TransportRequestStatus."
            )

        if self.dispatched_at is not None:
            if not isinstance(self.dispatched_at, datetime):
                raise TypeError(
                    "dispatched_at must be a datetime or None."
                )
            if self.dispatched_at < self.requested_at:
                raise ValueError(
                    "dispatched_at cannot precede requested_at."
                )

        if self.delivered_at is not None:
            if not isinstance(self.delivered_at, datetime):
                raise TypeError(
                    "delivered_at must be a datetime or None."
                )
            if self.dispatched_at is None:
                raise ValueError(
                    "delivered_at requires dispatched_at."
                )
            if self.delivered_at < self.dispatched_at:
                raise ValueError(
                    "delivered_at cannot precede dispatched_at."
                )

    @property
    def dose_id(self) -> UUID:
        return self.dose.id

    @property
    def patient_id(self) -> UUID:
        return self.dose.patient_id

    @property
    def elapsed_minutes(self) -> float | None:
        """Return completed transport duration in minutes."""
        if self.dispatched_at is None or self.delivered_at is None:
            return None

        return (
            self.delivered_at - self.dispatched_at
        ).total_seconds() / 60.0

    @property
    def display_name(self) -> str:
        return (
            f"{self.dose.dose_reference}: "
            f"{self.origin_room.name} → {self.destination_room.name} "
            f"[{self.transport_mode.value}/{self.status.value}]"
        )

    def dispatch(self, dispatched_at: datetime) -> None:
        """Dispatch a newly created transport request."""
        if self.status != TransportRequestStatus.CREATED:
            raise ValueError(
                "only a created transport request can be dispatched."
            )

        if not isinstance(dispatched_at, datetime):
            raise TypeError("dispatched_at must be a datetime.")

        if dispatched_at < self.requested_at:
            raise ValueError(
                "dispatched_at cannot precede requested_at."
            )

        self.dispatched_at = dispatched_at
        self.status = TransportRequestStatus.DISPATCHED

    def start_transport(self) -> None:
        """Mark a dispatched request as in transit."""
        if self.status != TransportRequestStatus.DISPATCHED:
            raise ValueError(
                "only a dispatched transport request can enter transit."
            )

        self.dose.start_transport()
        self.status = TransportRequestStatus.IN_TRANSIT

    def deliver(self, delivered_at: datetime) -> None:
        """Deliver an in-transit dose to its destination."""
        if self.status != TransportRequestStatus.IN_TRANSIT:
            raise ValueError(
                "only an in-transit transport request can be delivered."
            )

        if not isinstance(delivered_at, datetime):
            raise TypeError("delivered_at must be a datetime.")

        if self.dispatched_at is None:
            raise ValueError(
                "transport request must have a dispatch timestamp."
            )

        if delivered_at < self.dispatched_at:
            raise ValueError(
                "delivered_at cannot precede dispatched_at."
            )

        self.dose.receive()
        self.delivered_at = delivered_at
        self.status = TransportRequestStatus.DELIVERED

    def cancel(self) -> None:
        """Cancel a request that has not been delivered."""
        if self.status == TransportRequestStatus.DELIVERED:
            raise ValueError(
                "a delivered transport request cannot be cancelled."
            )

        self.dose.cancel()
        self.status = TransportRequestStatus.CANCELLED
