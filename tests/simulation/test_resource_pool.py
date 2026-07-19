import pytest

from mrt.simulation.resource_pool import ResourcePool, ResourceUnit


def make_pool() -> ResourcePool:
    return ResourcePool(
        name="PET Scanners",
        units=[
            ResourceUnit("PET-1"),
            ResourceUnit("PET-2"),
        ],
    )


def test_acquire_and_release_resource() -> None:
    pool = make_pool()

    unit = pool.acquire()

    assert pool.available_count == 1
    assert pool.allocated_count == 1

    pool.release(unit)

    assert pool.available_count == 2
    assert pool.allocated_count == 0


def test_exhausted_pool_rejects_acquisition() -> None:
    pool = make_pool()
    pool.acquire()
    pool.acquire()

    with pytest.raises(RuntimeError):
        pool.acquire()


def test_unallocated_resource_cannot_be_released() -> None:
    pool = make_pool()

    with pytest.raises(KeyError):
        pool.release(ResourceUnit("External Scanner"))
