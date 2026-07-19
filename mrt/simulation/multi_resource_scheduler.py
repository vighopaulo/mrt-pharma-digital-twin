from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from mrt.simulation.resource_pool import ResourcePool, ResourceUnit


@dataclass(frozen=True, slots=True)
class ResourceRequirement:
    """One named resource pool and the quantity required from it."""

    pool_name: str
    quantity: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.pool_name, str):
            raise TypeError("pool_name must be a string.")
        if not self.pool_name.strip():
            raise ValueError("pool_name cannot be empty.")
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise TypeError("quantity must be an integer.")
        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero.")


@dataclass(frozen=True, slots=True)
class MultiResourceRequest:
    """An entity requesting several constrained resources atomically."""

    entity: Any
    requested_at: datetime
    requirements: tuple[ResourceRequirement, ...]
    priority: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.requested_at, datetime):
            raise TypeError("requested_at must be a datetime.")
        if not isinstance(self.requirements, tuple):
            raise TypeError("requirements must be a tuple.")
        if not self.requirements:
            raise ValueError("requirements cannot be empty.")
        if not all(
            isinstance(item, ResourceRequirement)
            for item in self.requirements
        ):
            raise TypeError(
                "all requirements must be ResourceRequirement instances."
            )
        if len({item.pool_name for item in self.requirements}) != len(
            self.requirements
        ):
            raise ValueError("requirements cannot repeat a pool name.")
        if isinstance(self.priority, bool) or not isinstance(
            self.priority,
            int,
        ):
            raise TypeError("priority must be an integer.")


@dataclass(frozen=True, slots=True)
class MultiResourceAllocation:
    request: MultiResourceRequest
    allocated_at: datetime
    resources: dict[str, tuple[ResourceUnit, ...]]

    def __post_init__(self) -> None:
        if not isinstance(self.allocated_at, datetime):
            raise TypeError("allocated_at must be a datetime.")


@dataclass(slots=True)
class MultiResourceScheduler:
    """Performs all-or-nothing allocation across multiple resource pools."""

    pools: dict[str, ResourcePool]
    pending: list[MultiResourceRequest] = field(default_factory=list)
    allocations: list[MultiResourceAllocation] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.pools, dict):
            raise TypeError("pools must be a dictionary.")
        if not self.pools:
            raise ValueError("at least one resource pool is required.")
        if not all(
            isinstance(name, str) and name.strip()
            for name in self.pools
        ):
            raise ValueError("pool names must be non-empty strings.")
        if not all(
            isinstance(pool, ResourcePool)
            for pool in self.pools.values()
        ):
            raise TypeError("all pool values must be ResourcePool instances.")

    def can_allocate(self, request: MultiResourceRequest) -> bool:
        if not isinstance(request, MultiResourceRequest):
            raise TypeError("request must be a MultiResourceRequest.")
        for requirement in request.requirements:
            pool = self.pools.get(requirement.pool_name)
            if pool is None or pool.available_count < requirement.quantity:
                return False
        return True

    def submit(self, request: MultiResourceRequest) -> None:
        if not isinstance(request, MultiResourceRequest):
            raise TypeError("request must be a MultiResourceRequest.")
        self.pending.append(request)
        self.pending.sort(
            key=lambda item: (
                item.priority,
                item.requested_at,
            )
        )

    def allocate(
        self,
        request: MultiResourceRequest,
        allocated_at: datetime,
    ) -> MultiResourceAllocation | None:
        if not isinstance(allocated_at, datetime):
            raise TypeError("allocated_at must be a datetime.")
        if allocated_at < request.requested_at:
            raise ValueError(
                "allocated_at cannot be earlier than requested_at."
            )
        if not self.can_allocate(request):
            return None

        acquired: dict[str, tuple[ResourceUnit, ...]] = {}

        try:
            for requirement in request.requirements:
                pool = self.pools[requirement.pool_name]
                units = tuple(
                    pool.acquire()
                    for _ in range(requirement.quantity)
                )
                acquired[requirement.pool_name] = units
        except Exception:
            for pool_name, units in acquired.items():
                for unit in units:
                    self.pools[pool_name].release(unit)
            raise

        allocation = MultiResourceAllocation(
            request=request,
            allocated_at=allocated_at,
            resources=acquired,
        )
        self.allocations.append(allocation)

        if request in self.pending:
            self.pending.remove(request)

        return allocation

    def allocate_next(
        self,
        allocated_at: datetime,
    ) -> MultiResourceAllocation | None:
        for request in tuple(self.pending):
            if self.can_allocate(request):
                return self.allocate(request, allocated_at)
        return None

    def release(self, allocation: MultiResourceAllocation) -> None:
        if not isinstance(allocation, MultiResourceAllocation):
            raise TypeError(
                "allocation must be a MultiResourceAllocation."
            )
        for pool_name, units in allocation.resources.items():
            pool = self.pools[pool_name]
            for unit in units:
                pool.release(unit)
