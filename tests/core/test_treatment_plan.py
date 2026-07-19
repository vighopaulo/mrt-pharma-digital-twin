from datetime import datetime
from uuid import UUID

import pytest

from mrt.core.entities.patient import Patient
from mrt.core.entities.treatment_plan import (
    TreatmentPlan,
    TreatmentPlanStatus,
)


def make_patient() -> Patient:
    return Patient(
        patient_reference="PAT-0001",
        name="Example Patient",
    )


def test_treatment_plan_stores_required_fields() -> None:
    patient = make_patient()
    plan = TreatmentPlan(
        patient=patient,
        treatment_name="Lu-177 PSMA Therapy",
    )

    assert plan.patient is patient
    assert plan.patient_id == patient.id
    assert plan.treatment_name == "Lu-177 PSMA Therapy"
    assert plan.status == TreatmentPlanStatus.DRAFT


def test_treatment_plan_receives_unique_identifier() -> None:
    first = TreatmentPlan(
        patient=make_patient(),
        treatment_name="Plan One",
    )
    second = TreatmentPlan(
        patient=make_patient(),
        treatment_name="Plan Two",
    )

    assert isinstance(first.id, UUID)
    assert isinstance(second.id, UUID)
    assert first.id != second.id


def test_treatment_metadata_is_trimmed() -> None:
    plan = TreatmentPlan(
        patient=make_patient(),
        treatment_name="  PET Imaging  ",
        notes="  Fast for six hours.  ",
    )

    assert plan.treatment_name == "PET Imaging"
    assert plan.notes == "Fast for six hours."


def test_patient_must_be_patient_instance() -> None:
    with pytest.raises(TypeError):
        TreatmentPlan(
            patient="PAT-0001",  # type: ignore[arg-type]
            treatment_name="PET Imaging",
        )


@pytest.mark.parametrize("invalid_name", ["", " ", "\t", "\n"])
def test_blank_treatment_name_is_rejected(invalid_name: str) -> None:
    with pytest.raises(ValueError):
        TreatmentPlan(
            patient=make_patient(),
            treatment_name=invalid_name,
        )


@pytest.mark.parametrize("invalid_notes", ["", " ", "\t", "\n"])
def test_blank_optional_notes_are_rejected(invalid_notes: str) -> None:
    with pytest.raises(ValueError):
        TreatmentPlan(
            patient=make_patient(),
            treatment_name="PET Imaging",
            notes=invalid_notes,
        )


def test_scheduled_status_requires_datetime() -> None:
    with pytest.raises(ValueError):
        TreatmentPlan(
            patient=make_patient(),
            treatment_name="PET Imaging",
            status=TreatmentPlanStatus.SCHEDULED,
        )


def test_schedule_sets_datetime_and_status() -> None:
    plan = TreatmentPlan(
        patient=make_patient(),
        treatment_name="PET Imaging",
    )
    scheduled_at = datetime(2026, 7, 25, 9, 30)

    plan.schedule(scheduled_at)

    assert plan.scheduled_at == scheduled_at
    assert plan.status == TreatmentPlanStatus.SCHEDULED


def test_valid_lifecycle_progression() -> None:
    plan = TreatmentPlan(
        patient=make_patient(),
        treatment_name="Lu-177 PSMA Therapy",
    )

    plan.schedule(datetime(2026, 7, 25, 9, 30))
    plan.start()
    plan.complete()

    assert plan.status == TreatmentPlanStatus.COMPLETED


def test_start_requires_scheduled_status() -> None:
    plan = TreatmentPlan(
        patient=make_patient(),
        treatment_name="PET Imaging",
    )

    with pytest.raises(ValueError):
        plan.start()


def test_complete_requires_in_progress_status() -> None:
    plan = TreatmentPlan(
        patient=make_patient(),
        treatment_name="PET Imaging",
    )

    with pytest.raises(ValueError):
        plan.complete()


def test_completed_plan_cannot_be_cancelled() -> None:
    plan = TreatmentPlan(
        patient=make_patient(),
        treatment_name="PET Imaging",
    )
    plan.schedule(datetime(2026, 7, 25, 9, 30))
    plan.start()
    plan.complete()

    with pytest.raises(ValueError):
        plan.cancel()


def test_display_name_contains_patient_treatment_and_status() -> None:
    plan = TreatmentPlan(
        patient=make_patient(),
        treatment_name="PET Imaging",
    )

    assert (
        plan.display_name
        == "PET Imaging — Example Patient [PAT-0001] [draft]"
    )
