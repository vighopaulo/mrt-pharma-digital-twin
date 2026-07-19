from datetime import datetime, timedelta
from math import isclose
from uuid import UUID

import pytest

from mrt.core.entities.patient import Patient
from mrt.core.entities.radiopharmaceutical_prescription import (
    RadiopharmaceuticalPrescription,
)
from mrt.core.entities.treatment_plan import TreatmentPlan
from mrt.radiation.entities.radiopharmaceutical_batch import (
    RadiopharmaceuticalBatch,
)
from mrt.radiation.entities.radiopharmaceutical_dose import (
    DoseStatus,
    RadiopharmaceuticalDose,
)
from mrt.radiation.entities.radionuclide import Radionuclide


def make_prescription() -> RadiopharmaceuticalPrescription:
    patient = Patient(
        patient_reference="PAT-0001",
        name="Example Patient",
    )
    plan = TreatmentPlan(
        patient=patient,
        treatment_name="PET Imaging",
    )
    return RadiopharmaceuticalPrescription(
        treatment_plan=plan,
        radiopharmaceutical_name="F-18 FDG",
        activity_mbq=370,
        calibration_at=datetime(2026, 7, 19, 9, 0),
    )


def make_batch() -> RadiopharmaceuticalBatch:
    radionuclide = Radionuclide(
        symbol="F-18",
        name="Fluorine-18",
        half_life_minutes=109.77,
    )
    return RadiopharmaceuticalBatch(
        batch_number="FDG-20260719-001",
        product_name="F-18 FDG",
        radionuclide=radionuclide,
        initial_activity_mbq=10000,
        produced_at=datetime(2026, 7, 19, 7, 30),
        calibration_at=datetime(2026, 7, 19, 8, 0),
    )


def make_dose() -> RadiopharmaceuticalDose:
    return RadiopharmaceuticalDose(
        dose_reference="DOSE-0001",
        prescription=make_prescription(),
        batch=make_batch(),
        dispensed_activity_mbq=370,
        dispensed_at=datetime(2026, 7, 19, 9, 0),
    )


def test_dose_stores_required_fields() -> None:
    dose = make_dose()

    assert dose.dose_reference == "DOSE-0001"
    assert dose.dispensed_activity_mbq == 370.0
    assert dose.status == DoseStatus.DISPENSED


def test_dose_receives_unique_identifier() -> None:
    first = make_dose()
    second = make_dose()

    assert isinstance(first.id, UUID)
    assert isinstance(second.id, UUID)
    assert first.id != second.id


def test_dose_links_prescription_patient_and_batch() -> None:
    dose = make_dose()

    assert dose.prescription_id == dose.prescription.id
    assert dose.patient_id == dose.prescription.patient_id
    assert dose.batch_id == dose.batch.id


def test_dose_reference_is_trimmed() -> None:
    dose = RadiopharmaceuticalDose(
        dose_reference="  DOSE-0001  ",
        prescription=make_prescription(),
        batch=make_batch(),
        dispensed_activity_mbq=370,
        dispensed_at=datetime(2026, 7, 19, 9, 0),
    )

    assert dose.dose_reference == "DOSE-0001"


def test_dispensed_activity_cannot_exceed_available_batch_activity() -> None:
    with pytest.raises(ValueError):
        RadiopharmaceuticalDose(
            dose_reference="DOSE-0001",
            prescription=make_prescription(),
            batch=make_batch(),
            dispensed_activity_mbq=20000,
            dispensed_at=datetime(2026, 7, 19, 9, 0),
        )


def test_dispensing_before_batch_calibration_is_rejected() -> None:
    with pytest.raises(ValueError):
        RadiopharmaceuticalDose(
            dose_reference="DOSE-0001",
            prescription=make_prescription(),
            batch=make_batch(),
            dispensed_activity_mbq=370,
            dispensed_at=datetime(2026, 7, 19, 7, 59),
        )


def test_activity_at_dispensing_equals_dispensed_activity() -> None:
    dose = make_dose()

    assert dose.activity_at(dose.dispensed_at) == 370.0


def test_activity_after_one_half_life_is_half() -> None:
    dose = make_dose()
    later = dose.dispensed_at + timedelta(
        minutes=dose.batch.radionuclide.half_life_minutes
    )

    assert isclose(
        dose.activity_at(later),
        185.0,
        rel_tol=1e-12,
    )


def test_valid_dose_lifecycle() -> None:
    dose = make_dose()

    dose.release()
    dose.start_transport()
    dose.receive()
    dose.administer()

    assert dose.status == DoseStatus.ADMINISTERED


def test_transport_requires_released_status() -> None:
    dose = make_dose()

    with pytest.raises(ValueError):
        dose.start_transport()


def test_administered_dose_cannot_be_cancelled() -> None:
    dose = make_dose()
    dose.release()
    dose.start_transport()
    dose.receive()
    dose.administer()

    with pytest.raises(ValueError):
        dose.cancel()


def test_display_name() -> None:
    dose = make_dose()

    assert (
        dose.display_name
        == "Dose DOSE-0001 — F-18 FDG 370 MBq [dispensed]"
    )
