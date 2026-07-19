from datetime import datetime, timedelta

import pytest

from mrt.simulation.multi_resource_scheduler import (
    MultiResourceRequest,
    MultiResourceScheduler,
    ResourceRequirement,
)
from mrt.simulation.reservation_manager import (
    ReservationManager,
    ReservationStatus,
)
from mrt.simulation.resource_pool import ResourcePool, ResourceUnit


START = datetime(2026, 7, 19, 8, 0)


def make_manager() -> ReservationManager:
    scheduler = MultiResourceScheduler(
        pools={
            "scanner": ResourcePool(
                "Scanner Pool",
                [ResourceUnit("PET-1")],
            )
        }
    )
    return ReservationManager(scheduler)


def make_request() -> MultiResourceRequest:
    return MultiResourceRequest(
        entity="patient-1",
        requested_at=START,
        requirements=(ResourceRequirement("scanner"),),
    )


def test_reservation_allocates_before_timeout() -> None:
    manager = make_manager()
    reservation = manager.create(
        make_request(),
        START,
        timeout_seconds=600,
    )

    allocation = manager.try_allocate(
        reservation,
        START + timedelta(minutes=5),
    )

    assert allocation is not None
    assert reservation.status == ReservationStatus.ALLOCATED


def test_reservation_expires_after_timeout() -> None:
    manager = make_manager()
    manager.scheduler.pools["scanner"].acquire()
    reservation = manager.create(
        make_request(),
        START,
        timeout_seconds=300,
    )

    allocation = manager.try_allocate(
        reservation,
        START + timedelta(minutes=6),
    )

    assert allocation is None
    assert reservation.status == ReservationStatus.EXPIRED


def test_expire_due_removes_pending_request() -> None:
    manager = make_manager()
    manager.scheduler.pools["scanner"].acquire()
    reservation = manager.create(
        make_request(),
        START,
        timeout_seconds=60,
    )

    expired = manager.expire_due(
        START + timedelta(minutes=2)
    )

    assert expired == (reservation,)
    assert reservation.request not in manager.scheduler.pending


def test_release_returns_resources() -> None:
    manager = make_manager()
    reservation = manager.create(
        make_request(),
        START,
        timeout_seconds=600,
    )
    manager.try_allocate(reservation, START)

    manager.release(reservation)

    assert reservation.status == ReservationStatus.RELEASED
    assert manager.scheduler.pools["scanner"].available_count == 1


def test_releasing_unallocated_reservation_fails() -> None:
    manager = make_manager()
    reservation = manager.create(
        make_request(),
        START,
        timeout_seconds=600,
    )

    with pytest.raises(ValueError):
        manager.release(reservation)
