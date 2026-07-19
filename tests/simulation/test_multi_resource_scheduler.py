from datetime import datetime, timedelta

import pytest

from mrt.simulation.multi_resource_scheduler import (
    MultiResourceRequest,
    MultiResourceScheduler,
    ResourceRequirement,
)
from mrt.simulation.resource_pool import ResourcePool, ResourceUnit


START = datetime(2026, 7, 19, 8, 0)


def make_scheduler() -> MultiResourceScheduler:
    return MultiResourceScheduler(
        pools={
            "scanner": ResourcePool(
                "Scanner Pool",
                [ResourceUnit("PET-1")],
            ),
            "technologist": ResourcePool(
                "Technologist Pool",
                [ResourceUnit("Tech-1")],
            ),
        }
    )


def make_request(entity: str = "patient-1") -> MultiResourceRequest:
    return MultiResourceRequest(
        entity=entity,
        requested_at=START,
        requirements=(
            ResourceRequirement("scanner"),
            ResourceRequirement("technologist"),
        ),
    )


def test_can_allocate_when_all_resources_available() -> None:
    assert make_scheduler().can_allocate(make_request()) is True


def test_allocation_is_atomic_across_pools() -> None:
    scheduler = make_scheduler()
    request = make_request()

    allocation = scheduler.allocate(request, START)

    assert allocation is not None
    assert scheduler.pools["scanner"].allocated_count == 1
    assert scheduler.pools["technologist"].allocated_count == 1


def test_allocation_returns_none_when_one_pool_is_unavailable() -> None:
    scheduler = make_scheduler()
    scheduler.pools["technologist"].acquire()

    allocation = scheduler.allocate(make_request(), START)

    assert allocation is None
    assert scheduler.pools["scanner"].available_count == 1


def test_pending_requests_respect_priority() -> None:
    scheduler = make_scheduler()
    routine = MultiResourceRequest(
        entity="routine",
        requested_at=START,
        requirements=(ResourceRequirement("scanner"),),
        priority=5,
    )
    urgent = MultiResourceRequest(
        entity="urgent",
        requested_at=START + timedelta(minutes=1),
        requirements=(ResourceRequirement("scanner"),),
        priority=1,
    )

    scheduler.submit(routine)
    scheduler.submit(urgent)

    allocation = scheduler.allocate_next(
        START + timedelta(minutes=2)
    )

    assert allocation is not None
    assert allocation.request.entity == "urgent"


def test_release_returns_all_resources() -> None:
    scheduler = make_scheduler()
    allocation = scheduler.allocate(make_request(), START)
    assert allocation is not None

    scheduler.release(allocation)

    assert scheduler.pools["scanner"].available_count == 1
    assert scheduler.pools["technologist"].available_count == 1


def test_duplicate_pool_requirements_are_rejected() -> None:
    with pytest.raises(ValueError):
        MultiResourceRequest(
            entity="patient-1",
            requested_at=START,
            requirements=(
                ResourceRequirement("scanner"),
                ResourceRequirement("scanner"),
            ),
        )
