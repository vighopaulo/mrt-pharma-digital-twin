from uuid import UUID

import pytest

from mrt.core.entities.equipment import Equipment


def test_equipment_stores_required_fields() -> None:
    equipment = Equipment(
        name="PET Scanner 1",
        equipment_type="PET Scanner",
    )

    assert equipment.name == "PET Scanner 1"
    assert equipment.equipment_type == "PET Scanner"
    assert equipment.is_active is True


def test_equipment_receives_unique_identifier() -> None:
    first = Equipment(name="PET 1", equipment_type="PET Scanner")
    second = Equipment(name="PET 2", equipment_type="PET Scanner")

    assert isinstance(first.id, UUID)
    assert isinstance(second.id, UUID)
    assert first.id != second.id


def test_equipment_metadata_is_trimmed() -> None:
    equipment = Equipment(
        name="  Cyclotron 1  ",
        equipment_type="  Cyclotron  ",
        manufacturer="  GE  ",
        model="  PETtrace  ",
    )

    assert equipment.name == "Cyclotron 1"
    assert equipment.equipment_type == "Cyclotron"
    assert equipment.manufacturer == "GE"
    assert equipment.model == "PETtrace"


@pytest.mark.parametrize("field_value", ["", " ", "\t", "\n"])
def test_blank_name_is_rejected(field_value: str) -> None:
    with pytest.raises(ValueError):
        Equipment(name=field_value, equipment_type="PET Scanner")


@pytest.mark.parametrize("field_value", ["", " ", "\t", "\n"])
def test_blank_equipment_type_is_rejected(field_value: str) -> None:
    with pytest.raises(ValueError):
        Equipment(name="PET 1", equipment_type=field_value)


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("manufacturer", ""),
        ("manufacturer", " "),
        ("model", ""),
        ("model", " "),
    ],
)
def test_blank_optional_metadata_is_rejected(
    field_name: str,
    field_value: str,
) -> None:
    kwargs = {
        "name": "PET 1",
        "equipment_type": "PET Scanner",
        field_name: field_value,
    }

    with pytest.raises(ValueError):
        Equipment(**kwargs)


def test_display_name_without_vendor_metadata() -> None:
    equipment = Equipment(name="Dose Calibrator 1", equipment_type="Calibrator")

    assert equipment.display_name == "Dose Calibrator 1"


def test_display_name_with_manufacturer_and_model() -> None:
    equipment = Equipment(
        name="Cyclotron 1",
        equipment_type="Cyclotron",
        manufacturer="GE",
        model="PETtrace",
    )

    assert equipment.display_name == "Cyclotron 1 (GE PETtrace)"


def test_equipment_can_be_deactivated_and_reactivated() -> None:
    equipment = Equipment(name="Hot Cell 1", equipment_type="Hot Cell")

    equipment.deactivate()
    assert equipment.is_active is False

    equipment.activate()
    assert equipment.is_active is True


def test_non_boolean_active_state_is_rejected() -> None:
    with pytest.raises(TypeError):
        Equipment(
            name="Scanner 1",
            equipment_type="PET Scanner",
            is_active=1,  # type: ignore[arg-type]
        )
