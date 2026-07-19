from uuid import UUID

import pytest

from mrt.core.entities.staff import Staff


def test_staff_stores_required_fields() -> None:
    staff = Staff(
        name="Ada Okafor",
        role="Nuclear Medicine Technologist",
    )

    assert staff.name == "Ada Okafor"
    assert staff.role == "Nuclear Medicine Technologist"
    assert staff.is_active is True


def test_staff_receives_unique_identifier() -> None:
    first = Staff(name="Ada Okafor", role="Technologist")
    second = Staff(name="Musa Bello", role="Pharmacist")

    assert isinstance(first.id, UUID)
    assert isinstance(second.id, UUID)
    assert first.id != second.id


def test_staff_metadata_is_trimmed() -> None:
    staff = Staff(
        name="  Ada Okafor  ",
        role="  Nuclear Medicine Technologist  ",
        department="  Nuclear Medicine  ",
        email="  ada@example.com  ",
    )

    assert staff.name == "Ada Okafor"
    assert staff.role == "Nuclear Medicine Technologist"
    assert staff.department == "Nuclear Medicine"
    assert staff.email == "ada@example.com"


@pytest.mark.parametrize("invalid_name", ["", " ", "\t", "\n"])
def test_blank_name_is_rejected(invalid_name: str) -> None:
    with pytest.raises(ValueError):
        Staff(name=invalid_name, role="Technologist")


@pytest.mark.parametrize("invalid_role", ["", " ", "\t", "\n"])
def test_blank_role_is_rejected(invalid_role: str) -> None:
    with pytest.raises(ValueError):
        Staff(name="Ada Okafor", role=invalid_role)


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("department", ""),
        ("department", " "),
        ("email", ""),
        ("email", " "),
    ],
)
def test_blank_optional_metadata_is_rejected(
    field_name: str,
    field_value: str,
) -> None:
    kwargs = {
        "name": "Ada Okafor",
        "role": "Technologist",
        field_name: field_value,
    }

    with pytest.raises(ValueError):
        Staff(**kwargs)


def test_invalid_email_is_rejected() -> None:
    with pytest.raises(ValueError):
        Staff(
            name="Ada Okafor",
            role="Technologist",
            email="invalid-email",
        )


def test_display_name_without_department() -> None:
    staff = Staff(name="Ada Okafor", role="Technologist")

    assert staff.display_name == "Ada Okafor — Technologist"


def test_display_name_with_department() -> None:
    staff = Staff(
        name="Ada Okafor",
        role="Technologist",
        department="Nuclear Medicine",
    )

    assert (
        staff.display_name
        == "Ada Okafor — Technologist, Nuclear Medicine"
    )


def test_staff_can_be_deactivated_and_reactivated() -> None:
    staff = Staff(name="Ada Okafor", role="Technologist")

    staff.deactivate()
    assert staff.is_active is False

    staff.activate()
    assert staff.is_active is True


def test_non_boolean_active_state_is_rejected() -> None:
    with pytest.raises(TypeError):
        Staff(
            name="Ada Okafor",
            role="Technologist",
            is_active=1,  # type: ignore[arg-type]
        )
