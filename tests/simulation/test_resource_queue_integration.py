from datetime import datetime, timedelta

from mrt.simulation.resource_pool import ResourcePool, ResourceUnit
from mrt.simulation.resource_queue import ResourceQueue


def test_waiting_patient_receives_released_scanner() -> None:
    start = datetime(2026, 7, 19, 8, 0)
    pool = ResourcePool(
        "PET Scanner",
        [ResourceUnit("PET-1")],
    )
    queue = ResourceQueue("PET Patient Queue")

    scanner = pool.acquire()
    waiting = queue.enqueue("patient-2", start)

    pool.release(scanner)
    reassigned = pool.acquire()
    next_patient = queue.dequeue(start + timedelta(minutes=12))

    assert reassigned.name == "PET-1"
    assert next_patient == waiting
    assert next_patient.entity == "patient-2"
    assert queue.is_empty is True
