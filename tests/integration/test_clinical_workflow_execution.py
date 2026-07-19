from mrt.core.entities.clinical_case import (
    ClinicalCase,
    ClinicalCaseOrigin,
    ClinicalCaseStatus,
)
from mrt.core.entities.clinical_workflow import (
    ClinicalWorkflow,
    ClinicalWorkflowStatus,
)
from mrt.core.entities.patient import Patient
from mrt.core.entities.treatment_plan import TreatmentPlan
from mrt.core.entities.workflow_step import WorkflowStep


def test_clinical_case_and_workflow_progress_together() -> None:
    patient = Patient(
        patient_reference="PAT-1001",
        name="Test Patient",
    )
    plan = TreatmentPlan(
        patient=patient,
        treatment_name="PET Imaging",
    )
    case = ClinicalCase(
        patient=patient,
        treatment_plan=plan,
        origin=ClinicalCaseOrigin.INBOUND,
    )
    workflow = ClinicalWorkflow(
        clinical_case=case,
        name="PET Imaging Workflow",
        steps=[
            WorkflowStep("Registration", 1, 10),
            WorkflowStep("Injection", 2, 15),
            WorkflowStep("Uptake", 3, 45),
            WorkflowStep("PET Acquisition", 4, 30),
        ],
    )

    case.admit()
    workflow.mark_ready()
    workflow.start()
    case.start_treatment()

    while workflow.status != ClinicalWorkflowStatus.COMPLETED:
        workflow.complete_current_step()

    case.complete()

    assert workflow.status == ClinicalWorkflowStatus.COMPLETED
    assert case.status == ClinicalCaseStatus.COMPLETED
    assert workflow.planned_duration_minutes == 100.0
