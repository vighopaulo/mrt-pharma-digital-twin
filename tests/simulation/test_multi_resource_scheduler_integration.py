from datetime import datetime, timedelta

from mrt.simulation.multi_resource_scheduler import (
    MultiResourceRequest,
    MultiResourceScheduler,
    ResourceRequirement,
)
from mrt.simulation.resource_pool import ResourcePool, ResourceUnit


def test_waiting_request_allocates_after_blocking_resource_release() -> None:
    start = datetime(2026, 7, 19, 8, 0)

    scanner_pool = ResourcePool(
        "Scanner Pool",
        [ResourceUnit("PET-1")],
    )
    technologist_pool = ResourcePool(
        "Technologist Pool",
        [ResourceUnit("Tech-1")],
    )

    blocking_scanner = scanner_pool.acquire()

    scheduler = MultiResourceScheduler(
        pools={
            "scanner": scanner_pool,
            "technologist": technologist_pool,
        }
    )

    request = MultiResourceRequest(
        entity="patient-1",
        requested_at=start,
        requirements=(
            ResourceRequirement("scanner"),
            ResourceRequirement("technologist"),
        ),
    )
    scheduler.submit(request)

    assert scheduler.allocate_next(start) is None
    assert technologist_pool.available_count == 1

    scanner_pool.release(blocking_scanner)

    allocation = scheduler.allocate_next(
        start + timedelta(minutes=10)
    )

    assert allocation is not None
    assert allocation.request.entity == "patient-1"
    assert scanner_pool.allocated_count == 1
    assert technologist_pool.allocated_count == 1
