from datetime import datetime
from uuid import UUID

import pytest

from mrt.core.entities.clinical_case import (
    ClinicalCase,
    ClinicalCaseOrigin,
    ClinicalCaseStatus,
)
from mrt.core.entities.patient import Patient
from mrt.core.entities.treatment_plan import TreatmentPlan


def make_patient(reference: str = "PAT-0001") -> Patient:
    return Patient(
        patient_reference=reference,
        name="Example Patient",
    )


def make_plan(patient: Patient) -> TreatmentPlan:
    return TreatmentPlan(
        patient=patient,
        treatment_name="Lu-177 PSMA Therapy",
    )


def test_clinical_case_links_patient_and_treatment_plan() -> None:
    patient = make_patient()
    plan = make_plan(patient)
    case = ClinicalCase(
        patient=patient,
        treatment_plan=plan,
        origin=ClinicalCaseOrigin.INBOUND,
    )

    assert case.patient is patient
    assert case.treatment_plan is plan
    assert case.patient_id == patient.id
    assert case.treatment_plan_id == plan.id
    assert case.status == ClinicalCaseStatus.CREATED


def test_clinical_case_receives_unique_identifier() -> None:
    patient = make_patient()
    plan = make_plan(patient)

    first = ClinicalCase(
        patient=patient,
        treatment_plan=plan,
        origin=ClinicalCaseOrigin.INBOUND,
    )
    second = ClinicalCase(
        patient=patient,
        treatment_plan=plan,
        origin=ClinicalCaseOrigin.INTERNAL,
    )

    assert isinstance(first.id, UUID)
    assert isinstance(second.id, UUID)
    assert first.id != second.id


def test_treatment_plan_must_belong_to_same_patient() -> None:
    patient = make_patient("PAT-0001")
    other_patient = make_patient("PAT-0002")
    plan = make_plan(other_patient)

    with pytest.raises(ValueError):
        ClinicalCase(
            patient=patient,
            treatment_plan=plan,
            origin=ClinicalCaseOrigin.INBOUND,
        )


def test_origin_must_use_defined_enum() -> None:
    patient = make_patient()
    plan = make_plan(patient)

    with pytest.raises(TypeError):
        ClinicalCase(
            patient=patient,
            treatment_plan=plan,
            origin="inbound",  # type: ignore[arg-type]
        )


def test_external_reference_is_trimmed() -> None:
    patient = make_patient()
    plan = make_plan(patient)

    case = ClinicalCase(
        patient=patient,
        treatment_plan=plan,
        origin=ClinicalCaseOrigin.INBOUND,
        external_reference="  REF-1001  ",
    )

    assert case.external_reference == "REF-1001"


@pytest.mark.parametrize("invalid_reference", ["", " ", "\t", "\n"])
def test_blank_external_reference_is_rejected(
    invalid_reference: str,
) -> None:
    patient = make_patient()
    plan = make_plan(patient)

    with pytest.raises(ValueError):
        ClinicalCase(
            patient=patient,
            treatment_plan=plan,
            origin=ClinicalCaseOrigin.INBOUND,
            external_reference=invalid_reference,
        )


def test_created_at_must_be_datetime() -> None:
    patient = make_patient()
    plan = make_plan(patient)

    with pytest.raises(TypeError):
        ClinicalCase(
            patient=patient,
            treatment_plan=plan,
            origin=ClinicalCaseOrigin.INBOUND,
            created_at="2026-07-18",  # type: ignore[arg-type]
        )


def test_valid_case_lifecycle() -> None:
    patient = make_patient()
    plan = make_plan(patient)
    case = ClinicalCase(
        patient=patient,
        treatment_plan=plan,
        origin=ClinicalCaseOrigin.INBOUND,
        created_at=datetime(2026, 7, 18, 10, 0),
    )

    case.admit()
    case.start_treatment()
    case.complete()

    assert case.status == ClinicalCaseStatus.COMPLETED


def test_start_treatment_requires_admitted_status() -> None:
    patient = make_patient()
    plan = make_plan(patient)
    case = ClinicalCase(
        patient=patient,
        treatment_plan=plan,
        origin=ClinicalCaseOrigin.INTERNAL,
    )

    with pytest.raises(ValueError):
        case.start_treatment()


def test_completed_case_cannot_be_cancelled() -> None:
    patient = make_patient()
    plan = make_plan(patient)
    case = ClinicalCase(
        patient=patient,
        treatment_plan=plan,
        origin=ClinicalCaseOrigin.OUTBOUND,
    )

    case.admit()
    case.start_treatment()
    case.complete()

    with pytest.raises(ValueError):
        case.cancel()


def test_display_name_contains_origin_and_status() -> None:
    patient = make_patient()
    plan = make_plan(patient)
    case = ClinicalCase(
        patient=patient,
        treatment_plan=plan,
        origin=ClinicalCaseOrigin.INBOUND,
    )

    assert (
        case.display_name
        == "Example Patient [PAT-0001] — "
        "Lu-177 PSMA Therapy [inbound/created]"
    )
