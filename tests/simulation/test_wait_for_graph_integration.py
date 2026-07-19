from datetime import datetime

from mrt.simulation.deadlock_detector import detect_cyclic_deadlocks
from mrt.simulation.multi_resource_scheduler import (
    MultiResourceRequest,
    ResourceRequirement,
)


def test_opposing_multi_resource_requests_form_detectable_cycle() -> None:
    start = datetime(2026, 7, 19, 8, 0)

    first = MultiResourceRequest(
        entity="workflow-a",
        requested_at=start,
        requirements=(
            ResourceRequirement("scanner"),
            ResourceRequirement("technologist"),
        ),
    )
    second = MultiResourceRequest(
        entity="workflow-b",
        requested_at=start,
        requirements=(
            ResourceRequirement("technologist"),
            ResourceRequirement("scanner"),
        ),
    )

    waits = (
        (first.entity, second.entity),
        (second.entity, first.entity),
    )

    deadlocks = detect_cyclic_deadlocks(waits)

    assert len(deadlocks) == 1
    assert set(deadlocks[0].cycle.nodes[:-1]) == {
        "workflow-a",
        "workflow-b",
    }
