from datetime import datetime

from mrt.simulation.deadlock_detector import detect_deadlock_risks
from mrt.simulation.multi_resource_scheduler import (
    MultiResourceRequest,
    MultiResourceScheduler,
    ResourceRequirement,
)
from mrt.simulation.resource_pool import ResourcePool, ResourceUnit


START = datetime(2026, 7, 19, 8, 0)


def test_detects_blocked_pending_request() -> None:
    scanner_pool = ResourcePool(
        "Scanner Pool",
        [ResourceUnit("PET-1")],
    )
    scanner_pool.acquire()

    scheduler = MultiResourceScheduler(
        pools={"scanner": scanner_pool}
    )
    request = MultiResourceRequest(
        entity="patient-1",
        requested_at=START,
        requirements=(ResourceRequirement("scanner"),),
    )
    scheduler.submit(request)

    risks = detect_deadlock_risks(scheduler)

    assert len(risks) == 1
    assert risks[0].unavailable_pools == ("scanner",)


def test_returns_no_risk_when_resources_available() -> None:
    scheduler = MultiResourceScheduler(
        pools={
            "scanner": ResourcePool(
                "Scanner Pool",
                [ResourceUnit("PET-1")],
            )
        }
    )
    request = MultiResourceRequest(
        entity="patient-1",
        requested_at=START,
        requirements=(ResourceRequirement("scanner"),),
    )
    scheduler.submit(request)

    assert detect_deadlock_risks(scheduler) == ()
