from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable

from mrt.simulation.multi_resource_scheduler import (
    MultiResourceRequest,
    MultiResourceScheduler,
)
from mrt.simulation.wait_for_graph import WaitForCycle, WaitForGraph


@dataclass(frozen=True, slots=True)
class DeadlockRisk:
    request: MultiResourceRequest
    unavailable_pools: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CyclicDeadlock:
    cycle: WaitForCycle


def detect_deadlock_risks(
    scheduler: MultiResourceScheduler,
) -> tuple[DeadlockRisk, ...]:
    if not isinstance(scheduler, MultiResourceScheduler):
        raise TypeError("scheduler must be a MultiResourceScheduler.")

    risks: list[DeadlockRisk] = []

    for request in scheduler.pending:
        unavailable: list[str] = []

        for requirement in request.requirements:
            pool = scheduler.pools.get(requirement.pool_name)
            if (
                pool is None
                or pool.available_count < requirement.quantity
            ):
                unavailable.append(requirement.pool_name)

        if unavailable:
            risks.append(
                DeadlockRisk(
                    request=request,
                    unavailable_pools=tuple(unavailable),
                )
            )

    return tuple(risks)


def detect_cyclic_deadlocks(
    waits: tuple[tuple[Hashable, Hashable], ...],
) -> tuple[CyclicDeadlock, ...]:
    graph = WaitForGraph()

    for waiter, holder in waits:
        graph.add_wait(waiter, holder)

    return tuple(
        CyclicDeadlock(cycle)
        for cycle in graph.detect_cycles()
    )
