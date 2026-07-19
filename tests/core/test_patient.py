from datetime import date
from uuid import UUID

import pytest

from mrt.core.entities.patient import Patient


def test_patient_stores_required_fields() -> None:
    patient = Patient(
        patient_reference="PAT-0001",
        name="Example Patient",
    )

    assert patient.patient_reference == "PAT-0001"
    assert patient.name == "Example Patient"
    assert patient.is_active is True


def test_patient_receives_unique_identifier() -> None:
    first = Patient(patient_reference="PAT-0001", name="Patient One")
    second = Patient(patient_reference="PAT-0002", name="Patient Two")

    assert isinstance(first.id, UUID)
    assert isinstance(second.id, UUID)
    assert first.id != second.id


def test_patient_metadata_is_trimmed() -> None:
    patient = Patient(
        patient_reference="  PAT-0001  ",
        name="  Example Patient  ",
        sex="  Female  ",
    )

    assert patient.patient_reference == "PAT-0001"
    assert patient.name == "Example Patient"
    assert patient.sex == "Female"


@pytest.mark.parametrize("invalid_reference", ["", " ", "\t", "\n"])
def test_blank_patient_reference_is_rejected(
    invalid_reference: str,
) -> None:
    with pytest.raises(ValueError):
        Patient(
            patient_reference=invalid_reference,
            name="Example Patient",
        )


@pytest.mark.parametrize("invalid_name", ["", " ", "\t", "\n"])
def test_blank_patient_name_is_rejected(invalid_name: str) -> None:
    with pytest.raises(ValueError):
        Patient(
            patient_reference="PAT-0001",
            name=invalid_name,
        )


@pytest.mark.parametrize("invalid_sex", ["", " ", "\t", "\n"])
def test_blank_optional_sex_is_rejected(invalid_sex: str) -> None:
    with pytest.raises(ValueError):
        Patient(
            patient_reference="PAT-0001",
            name="Example Patient",
            sex=invalid_sex,
        )


def test_future_date_of_birth_is_rejected() -> None:
    with pytest.raises(ValueError):
        Patient(
            patient_reference="PAT-0001",
            name="Example Patient",
            date_of_birth=date(2999, 1, 1),
        )


def test_display_name() -> None:
    patient = Patient(
        patient_reference="PAT-0001",
        name="Example Patient",
    )

    assert patient.display_name == "Example Patient [PAT-0001]"


@pytest.mark.parametrize(
    ("reference_date", "expected_age"),
    [
        (date(2026, 6, 14), 39),
        (date(2026, 6, 15), 40),
        (date(2026, 12, 31), 40),
    ],
)
def test_age_on(
    reference_date: date,
    expected_age: int,
) -> None:
    patient = Patient(
        patient_reference="PAT-0001",
        name="Example Patient",
        date_of_birth=date(1986, 6, 15),
    )

    assert patient.age_on(reference_date) == expected_age


def test_age_on_returns_none_without_date_of_birth() -> None:
    patient = Patient(
        patient_reference="PAT-0001",
        name="Example Patient",
    )

    assert patient.age_on(date(2026, 1, 1)) is None


def test_age_on_rejects_date_before_birth() -> None:
    patient = Patient(
        patient_reference="PAT-0001",
        name="Example Patient",
        date_of_birth=date(2000, 1, 1),
    )

    with pytest.raises(ValueError):
        patient.age_on(date(1999, 12, 31))


def test_patient_can_be_deactivated_and_reactivated() -> None:
    patient = Patient(
        patient_reference="PAT-0001",
        name="Example Patient",
    )

    patient.deactivate()
    assert patient.is_active is False

    patient.activate()
    assert patient.is_active is True


def test_non_boolean_active_state_is_rejected() -> None:
    with pytest.raises(TypeError):
        Patient(
            patient_reference="PAT-0001",
            name="Example Patient",
            is_active=1,  # type: ignore[arg-type]
        )
