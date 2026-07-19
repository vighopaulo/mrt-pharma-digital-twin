from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from mrt.simulation.resource_pool import ResourcePool, ResourceUnit
from mrt.simulation.resource_queue import QueueEntry, ResourceQueue


@dataclass(frozen=True, slots=True)
class ResourceAssignment:
    queue_entry: QueueEntry
    resource_unit: ResourceUnit
    assigned_at: datetime
    waiting_seconds: float

    def __post_init__(self) -> None:
        if not isinstance(self.assigned_at, datetime):
            raise TypeError("assigned_at must be a datetime.")
        if self.waiting_seconds < 0:
            raise ValueError("waiting_seconds cannot be negative.")


@dataclass(slots=True)
class ResourceDispatcher:
    name: str
    queue: ResourceQueue
    pool: ResourcePool
    assignments: list[ResourceAssignment] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("name must be a string.")
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("name cannot be empty.")
        if not isinstance(self.queue, ResourceQueue):
            raise TypeError("queue must be a ResourceQueue.")
        if not isinstance(self.pool, ResourcePool):
            raise TypeError("pool must be a ResourcePool.")

    @property
    def active_assignment_count(self) -> int:
        return self.pool.allocated_count

    def dispatch_one(self, assigned_at: datetime) -> ResourceAssignment | None:
        if not isinstance(assigned_at, datetime):
            raise TypeError("assigned_at must be a datetime.")
        if self.queue.is_empty or not self.pool.has_available:
            return None

        entry = self.queue.peek()
        waiting_seconds = self.queue.waiting_seconds(entry, assigned_at)
        entry = self.queue.dequeue(assigned_at)
        unit = self.pool.acquire()

        assignment = ResourceAssignment(
            queue_entry=entry,
            resource_unit=unit,
            assigned_at=assigned_at,
            waiting_seconds=waiting_seconds,
        )
        self.assignments.append(assignment)
        return assignment

    def dispatch_available(
        self,
        assigned_at: datetime,
    ) -> tuple[ResourceAssignment, ...]:
        dispatched: list[ResourceAssignment] = []
        while not self.queue.is_empty and self.pool.has_available:
            assignment = self.dispatch_one(assigned_at)
            if assignment is not None:
                dispatched.append(assignment)
        return tuple(dispatched)

    def release_and_dispatch(
        self,
        resource_unit: ResourceUnit,
        released_at: datetime,
    ) -> ResourceAssignment | None:
        if not isinstance(resource_unit, ResourceUnit):
            raise TypeError("resource_unit must be a ResourceUnit.")
        if not isinstance(released_at, datetime):
            raise TypeError("released_at must be a datetime.")
        self.pool.release(resource_unit)
        return self.dispatch_one(released_at)

    def assignment_for_entity(self, entity: Any) -> ResourceAssignment:
        for assignment in reversed(self.assignments):
            if assignment.queue_entry.entity == entity:
                return assignment
        raise KeyError("no assignment exists for the requested entity.")
