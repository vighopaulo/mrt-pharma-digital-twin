from uuid import UUID

import pytest

from mrt.core.entities.equipment import Equipment
from mrt.core.entities.room import Room
from mrt.core.entities.staff import Staff
from mrt.core.entities.workflow_step import (
    WorkflowStep,
    WorkflowStepStatus,
)


def test_workflow_step_stores_required_fields() -> None:
    step = WorkflowStep(
        name="Patient Registration",
        sequence=1,
        planned_duration_minutes=10,
    )

    assert step.name == "Patient Registration"
    assert step.sequence == 1
    assert step.planned_duration_minutes == 10.0
    assert step.status == WorkflowStepStatus.PENDING


def test_workflow_step_receives_unique_identifier() -> None:
    first = WorkflowStep("Registration", 1, 10)
    second = WorkflowStep("Injection", 2, 15)

    assert isinstance(first.id, UUID)
    assert isinstance(second.id, UUID)
    assert first.id != second.id


def test_workflow_step_metadata_is_trimmed() -> None:
    step = WorkflowStep(
        name="  PET Acquisition  ",
        sequence=3,
        planned_duration_minutes=30,
    )

    assert step.name == "PET Acquisition"


@pytest.mark.parametrize("invalid_name", ["", " ", "\t", "\n"])
def test_blank_name_is_rejected(invalid_name: str) -> None:
    with pytest.raises(ValueError):
        WorkflowStep(invalid_name, 1, 10)


@pytest.mark.parametrize("invalid_sequence", [0, -1])
def test_non_positive_sequence_is_rejected(
    invalid_sequence: int,
) -> None:
    with pytest.raises(ValueError):
        WorkflowStep("Registration", invalid_sequence, 10)


@pytest.mark.parametrize("invalid_sequence", [1.5, "1", True, None])
def test_non_integer_sequence_is_rejected(
    invalid_sequence: object,
) -> None:
    with pytest.raises(TypeError):
        WorkflowStep(
            "Registration",
            invalid_sequence,  # type: ignore[arg-type]
            10,
        )


@pytest.mark.parametrize("invalid_duration", [0, -1, -0.5])
def test_non_positive_duration_is_rejected(
    invalid_duration: float,
) -> None:
    with pytest.raises(ValueError):
        WorkflowStep("Registration", 1, invalid_duration)


def test_optional_resources_can_be_assigned() -> None:
    room = Room(name="PET Suite")
    scanner = Equipment(
        name="PET Scanner 1",
        equipment_type="PET Scanner",
    )
    room.add_equipment(scanner)
    staff = Staff(name="Ada Okafor", role="Technologist")

    step = WorkflowStep(
        name="PET Acquisition",
        sequence=3,
        planned_duration_minutes=30,
        room=room,
        equipment=scanner,
        staff=staff,
    )

    assert step.room is room
    assert step.equipment is scanner
    assert step.staff is staff


def test_equipment_assigned_to_different_room_is_rejected() -> None:
    first_room = Room(name="PET Suite A")
    second_room = Room(name="PET Suite B")
    scanner = Equipment(
        name="PET Scanner 1",
        equipment_type="PET Scanner",
    )
    first_room.add_equipment(scanner)

    with pytest.raises(ValueError):
        WorkflowStep(
            name="PET Acquisition",
            sequence=3,
            planned_duration_minutes=30,
            room=second_room,
            equipment=scanner,
        )


def test_valid_workflow_step_lifecycle() -> None:
    step = WorkflowStep("Injection", 2, 15)

    step.mark_ready()
    step.start()
    step.complete()

    assert step.status == WorkflowStepStatus.COMPLETED


def test_start_requires_ready_status() -> None:
    step = WorkflowStep("Injection", 2, 15)

    with pytest.raises(ValueError):
        step.start()


def test_completed_step_cannot_be_cancelled() -> None:
    step = WorkflowStep("Injection", 2, 15)
    step.mark_ready()
    step.start()
    step.complete()

    with pytest.raises(ValueError):
        step.cancel()


def test_display_name() -> None:
    step = WorkflowStep("PET Acquisition", 3, 30)

    assert step.display_name == "3. PET Acquisition (30 min) [pending]"
