from datetime import datetime
from uuid import UUID

import pytest

from mrt.core.entities.patient import Patient
from mrt.core.entities.radiopharmaceutical_prescription import (
    PrescriptionStatus,
    RadiopharmaceuticalPrescription,
)
from mrt.core.entities.treatment_plan import TreatmentPlan


def make_plan() -> TreatmentPlan:
    patient = Patient(
        patient_reference="PAT-0001",
        name="Example Patient",
    )
    return TreatmentPlan(
        patient=patient,
        treatment_name="Lu-177 PSMA Therapy",
    )


def make_prescription() -> RadiopharmaceuticalPrescription:
    return RadiopharmaceuticalPrescription(
        treatment_plan=make_plan(),
        radiopharmaceutical_name="Lu-177 PSMA-617",
        activity_mbq=7400,
        calibration_at=datetime(2026, 7, 25, 9, 0),
    )


def test_prescription_stores_required_fields() -> None:
    prescription = make_prescription()

    assert prescription.radiopharmaceutical_name == "Lu-177 PSMA-617"
    assert prescription.activity_mbq == 7400.0
    assert prescription.activity_gbq == 7.4
    assert prescription.status == PrescriptionStatus.DRAFT


def test_prescription_receives_unique_identifier() -> None:
    first = make_prescription()
    second = make_prescription()

    assert isinstance(first.id, UUID)
    assert isinstance(second.id, UUID)
    assert first.id != second.id


def test_prescription_links_to_plan_and_patient() -> None:
    plan = make_plan()
    prescription = RadiopharmaceuticalPrescription(
        treatment_plan=plan,
        radiopharmaceutical_name="F-18 FDG",
        activity_mbq=370,
        calibration_at=datetime(2026, 7, 25, 8, 0),
    )

    assert prescription.treatment_plan_id == plan.id
    assert prescription.patient_id == plan.patient_id


def test_text_metadata_is_trimmed() -> None:
    prescription = RadiopharmaceuticalPrescription(
        treatment_plan=make_plan(),
        radiopharmaceutical_name="  F-18 FDG  ",
        activity_mbq=370,
        calibration_at=datetime(2026, 7, 25, 8, 0),
        administration_route="  intravenous  ",
        notes="  Fast for six hours.  ",
    )

    assert prescription.radiopharmaceutical_name == "F-18 FDG"
    assert prescription.administration_route == "intravenous"
    assert prescription.notes == "Fast for six hours."


@pytest.mark.parametrize("invalid_activity", [0, -1, -0.5])
def test_non_positive_activity_is_rejected(
    invalid_activity: float,
) -> None:
    with pytest.raises(ValueError):
        RadiopharmaceuticalPrescription(
            treatment_plan=make_plan(),
            radiopharmaceutical_name="F-18 FDG",
            activity_mbq=invalid_activity,
            calibration_at=datetime(2026, 7, 25, 8, 0),
        )


@pytest.mark.parametrize("invalid_activity", ["370", None, True])
def test_non_numeric_activity_is_rejected(
    invalid_activity: object,
) -> None:
    with pytest.raises(TypeError):
        RadiopharmaceuticalPrescription(
            treatment_plan=make_plan(),
            radiopharmaceutical_name="F-18 FDG",
            activity_mbq=invalid_activity,  # type: ignore[arg-type]
            calibration_at=datetime(2026, 7, 25, 8, 0),
        )


def test_valid_prescription_lifecycle() -> None:
    prescription = make_prescription()

    prescription.approve()
    prescription.mark_prepared()
    prescription.mark_administered()

    assert prescription.status == PrescriptionStatus.ADMINISTERED


def test_prepared_requires_approved_status() -> None:
    prescription = make_prescription()

    with pytest.raises(ValueError):
        prescription.mark_prepared()


def test_administered_prescription_cannot_be_cancelled() -> None:
    prescription = make_prescription()
    prescription.approve()
    prescription.mark_prepared()
    prescription.mark_administered()

    with pytest.raises(ValueError):
        prescription.cancel()


def test_display_name() -> None:
    prescription = make_prescription()

    assert (
        prescription.display_name
        == "Lu-177 PSMA-617 7400 MBq — "
        "Example Patient [PAT-0001] [draft]"
    )
