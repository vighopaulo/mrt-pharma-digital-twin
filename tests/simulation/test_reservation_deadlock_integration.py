from datetime import datetime, timedelta

from mrt.simulation.deadlock_detector import detect_deadlock_risks
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


def test_timeout_clears_blocked_request_and_deadlock_risk() -> None:
    start = datetime(2026, 7, 19, 8, 0)

    scanner_pool = ResourcePool(
        "Scanner Pool",
        [ResourceUnit("PET-1")],
    )
    scanner_pool.acquire()

    scheduler = MultiResourceScheduler(
        pools={"scanner": scanner_pool}
    )
    manager = ReservationManager(scheduler)

    request = MultiResourceRequest(
        entity="patient-1",
        requested_at=start,
        requirements=(ResourceRequirement("scanner"),),
    )
    reservation = manager.create(
        request,
        start,
        timeout_seconds=120,
    )

    assert len(detect_deadlock_risks(scheduler)) == 1

    manager.expire_due(start + timedelta(minutes=3))

    assert reservation.status == ReservationStatus.EXPIRED
    assert detect_deadlock_risks(scheduler) == ()
