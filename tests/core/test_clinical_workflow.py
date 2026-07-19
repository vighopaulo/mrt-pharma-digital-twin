import pytest

from mrt.core.entities.clinical_case import (
    ClinicalCase,
    ClinicalCaseOrigin,
)
from mrt.core.entities.clinical_workflow import (
    ClinicalWorkflow,
    ClinicalWorkflowStatus,
)
from mrt.core.entities.patient import Patient
from mrt.core.entities.treatment_plan import TreatmentPlan
from mrt.core.entities.workflow_step import (
    WorkflowStep,
    WorkflowStepStatus,
)


def make_case() -> ClinicalCase:
    patient = Patient(
        patient_reference="PAT-0001",
        name="Example Patient",
    )
    plan = TreatmentPlan(
        patient=patient,
        treatment_name="PET Imaging",
    )
    return ClinicalCase(
        patient=patient,
        treatment_plan=plan,
        origin=ClinicalCaseOrigin.INTERNAL,
    )


def make_steps() -> list[WorkflowStep]:
    return [
        WorkflowStep("Registration", 1, 10),
        WorkflowStep("Injection", 2, 15),
        WorkflowStep("PET Acquisition", 3, 30),
    ]


def test_workflow_stores_case_and_orders_steps() -> None:
    steps = make_steps()
    workflow = ClinicalWorkflow(
        clinical_case=make_case(),
        name="PET Diagnostic Workflow",
        steps=[steps[2], steps[0], steps[1]],
    )

    assert workflow.step_count == 3
    assert [step.sequence for step in workflow.steps] == [1, 2, 3]
    assert workflow.status == ClinicalWorkflowStatus.DRAFT


def test_workflow_rejects_duplicate_sequence() -> None:
    workflow = ClinicalWorkflow(
        clinical_case=make_case(),
        name="PET Workflow",
        steps=[WorkflowStep("Registration", 1, 10)],
    )

    with pytest.raises(ValueError):
        workflow.add_step(WorkflowStep("Another Step", 1, 5))


def test_planned_duration_is_sum_of_steps() -> None:
    workflow = ClinicalWorkflow(
        clinical_case=make_case(),
        name="PET Workflow",
        steps=make_steps(),
    )

    assert workflow.planned_duration_minutes == 55.0


def test_empty_workflow_cannot_be_marked_ready() -> None:
    workflow = ClinicalWorkflow(
        clinical_case=make_case(),
        name="PET Workflow",
    )

    with pytest.raises(ValueError):
        workflow.mark_ready()


def test_mark_ready_activates_first_step() -> None:
    workflow = ClinicalWorkflow(
        clinical_case=make_case(),
        name="PET Workflow",
        steps=make_steps(),
    )

    workflow.mark_ready()

    assert workflow.status == ClinicalWorkflowStatus.READY
    assert workflow.steps[0].status == WorkflowStepStatus.READY


def test_workflow_executes_steps_in_sequence() -> None:
    workflow = ClinicalWorkflow(
        clinical_case=make_case(),
        name="PET Workflow",
        steps=make_steps(),
    )

    workflow.mark_ready()
    workflow.start()

    assert workflow.status == ClinicalWorkflowStatus.IN_PROGRESS
    assert workflow.current_step is workflow.steps[0]

    workflow.complete_current_step()
    assert workflow.steps[0].status == WorkflowStepStatus.COMPLETED
    assert workflow.steps[1].status == WorkflowStepStatus.READY

    workflow.complete_current_step()
    assert workflow.steps[1].status == WorkflowStepStatus.COMPLETED
    assert workflow.steps[2].status == WorkflowStepStatus.READY

    workflow.complete_current_step()
    assert workflow.steps[2].status == WorkflowStepStatus.COMPLETED
    assert workflow.status == ClinicalWorkflowStatus.COMPLETED


def test_steps_cannot_be_removed_after_draft() -> None:
    workflow = ClinicalWorkflow(
        clinical_case=make_case(),
        name="PET Workflow",
        steps=make_steps(),
    )
    workflow.mark_ready()

    with pytest.raises(ValueError):
        workflow.remove_step(1)


def test_completed_workflow_cannot_be_cancelled() -> None:
    workflow = ClinicalWorkflow(
        clinical_case=make_case(),
        name="PET Workflow",
        steps=[WorkflowStep("Registration", 1, 10)],
    )
    workflow.mark_ready()
    workflow.start()
    workflow.complete_current_step()

    with pytest.raises(ValueError):
        workflow.cancel()
