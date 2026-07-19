from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4

from mrt.simulation.multi_resource_scheduler import (
    MultiResourceAllocation,
    MultiResourceRequest,
    MultiResourceScheduler,
)


class ReservationStatus(StrEnum):
    PENDING = "pending"
    ALLOCATED = "allocated"
    EXPIRED = "expired"
    RELEASED = "released"


@dataclass(slots=True)
class ResourceReservation:
    request: MultiResourceRequest
    created_at: datetime
    timeout_seconds: float
    id: UUID = field(default_factory=uuid4)
    status: ReservationStatus = ReservationStatus.PENDING
    allocation: MultiResourceAllocation | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime.")
        if isinstance(self.timeout_seconds, bool) or not isinstance(
            self.timeout_seconds,
            (int, float),
        ):
            raise TypeError("timeout_seconds must be numeric.")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero.")

    @property
    def expires_at(self) -> datetime:
        return self.created_at + timedelta(seconds=float(self.timeout_seconds))

    def is_expired(self, moment: datetime) -> bool:
        if not isinstance(moment, datetime):
            raise TypeError("moment must be a datetime.")
        return moment >= self.expires_at


@dataclass(slots=True)
class ReservationManager:
    scheduler: MultiResourceScheduler
    reservations: list[ResourceReservation] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.scheduler, MultiResourceScheduler):
            raise TypeError(
                "scheduler must be a MultiResourceScheduler."
            )

    def create(
        self,
        request: MultiResourceRequest,
        created_at: datetime,
        timeout_seconds: float,
    ) -> ResourceReservation:
        reservation = ResourceReservation(
            request=request,
            created_at=created_at,
            timeout_seconds=timeout_seconds,
        )
        self.reservations.append(reservation)
        self.scheduler.submit(request)
        return reservation

    def try_allocate(
        self,
        reservation: ResourceReservation,
        moment: datetime,
    ) -> MultiResourceAllocation | None:
        if reservation.status != ReservationStatus.PENDING:
            return reservation.allocation

        if reservation.is_expired(moment):
            reservation.status = ReservationStatus.EXPIRED
            if reservation.request in self.scheduler.pending:
                self.scheduler.pending.remove(reservation.request)
            return None

        allocation = self.scheduler.allocate(
            reservation.request,
            moment,
        )
        if allocation is not None:
            reservation.allocation = allocation
            reservation.status = ReservationStatus.ALLOCATED
        return allocation

    def expire_due(self, moment: datetime) -> tuple[ResourceReservation, ...]:
        expired: list[ResourceReservation] = []
        for reservation in self.reservations:
            if (
                reservation.status == ReservationStatus.PENDING
                and reservation.is_expired(moment)
            ):
                reservation.status = ReservationStatus.EXPIRED
                if reservation.request in self.scheduler.pending:
                    self.scheduler.pending.remove(reservation.request)
                expired.append(reservation)
        return tuple(expired)

    def release(self, reservation: ResourceReservation) -> None:
        if reservation.status != ReservationStatus.ALLOCATED:
            raise ValueError("reservation is not currently allocated.")
        assert reservation.allocation is not None
        self.scheduler.release(reservation.allocation)
        reservation.status = ReservationStatus.RELEASED
