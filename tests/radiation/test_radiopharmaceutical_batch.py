from datetime import datetime, timedelta
from math import isclose
from uuid import UUID

import pytest

from mrt.radiation.entities.radiopharmaceutical_batch import (
    BatchStatus,
    RadiopharmaceuticalBatch,
)
from mrt.radiation.entities.radionuclide import Radionuclide


def make_radionuclide() -> Radionuclide:
    return Radionuclide(
        symbol="F-18",
        name="Fluorine-18",
        half_life_minutes=109.77,
    )


def make_batch() -> RadiopharmaceuticalBatch:
    produced_at = datetime(2026, 7, 19, 7, 30)
    calibration_at = datetime(2026, 7, 19, 8, 0)

    return RadiopharmaceuticalBatch(
        batch_number="FDG-20260719-001",
        product_name="F-18 FDG",
        radionuclide=make_radionuclide(),
        initial_activity_mbq=120000,
        calibration_at=calibration_at,
        produced_at=produced_at,
        expiration_at=datetime(2026, 7, 19, 18, 0),
    )


def test_batch_stores_required_fields() -> None:
    batch = make_batch()

    assert batch.batch_number == "FDG-20260719-001"
    assert batch.product_name == "F-18 FDG"
    assert batch.initial_activity_mbq == 120000.0
    assert batch.status == BatchStatus.CREATED


def test_batch_receives_unique_identifier() -> None:
    first = make_batch()
    second = make_batch()

    assert isinstance(first.id, UUID)
    assert isinstance(second.id, UUID)
    assert first.id != second.id


def test_text_fields_are_trimmed() -> None:
    batch = RadiopharmaceuticalBatch(
        batch_number="  BATCH-001  ",
        product_name="  F-18 FDG  ",
        radionuclide=make_radionuclide(),
        initial_activity_mbq=1000,
        produced_at=datetime(2026, 7, 19, 7, 30),
        calibration_at=datetime(2026, 7, 19, 8, 0),
    )

    assert batch.batch_number == "BATCH-001"
    assert batch.product_name == "F-18 FDG"


def test_production_cannot_occur_after_calibration() -> None:
    with pytest.raises(ValueError):
        RadiopharmaceuticalBatch(
            batch_number="BATCH-001",
            product_name="F-18 FDG",
            radionuclide=make_radionuclide(),
            initial_activity_mbq=1000,
            produced_at=datetime(2026, 7, 19, 9, 0),
            calibration_at=datetime(2026, 7, 19, 8, 0),
        )


@pytest.mark.parametrize("invalid_activity", [0, -1, -0.5])
def test_non_positive_initial_activity_is_rejected(
    invalid_activity: float,
) -> None:
    with pytest.raises(ValueError):
        RadiopharmaceuticalBatch(
            batch_number="BATCH-001",
            product_name="F-18 FDG",
            radionuclide=make_radionuclide(),
            initial_activity_mbq=invalid_activity,
            produced_at=datetime(2026, 7, 19, 7, 30),
            calibration_at=datetime(2026, 7, 19, 8, 0),
        )


def test_activity_at_calibration_equals_initial_activity() -> None:
    batch = make_batch()

    assert batch.activity_at(batch.calibration_at) == 120000.0


def test_activity_after_one_half_life_is_half() -> None:
    batch = make_batch()
    at_time = batch.calibration_at + timedelta(
        minutes=batch.radionuclide.half_life_minutes
    )

    assert isclose(
        batch.activity_at(at_time),
        60000.0,
        rel_tol=1e-12,
    )
    assert isclose(
        batch.remaining_fraction_at(at_time),
        0.5,
        rel_tol=1e-12,
    )


def test_activity_before_calibration_is_rejected() -> None:
    batch = make_batch()

    with pytest.raises(ValueError):
        batch.activity_at(batch.calibration_at - timedelta(minutes=1))


def test_expiration_check() -> None:
    batch = make_batch()

    assert batch.is_expired_at(
        datetime(2026, 7, 19, 17, 59)
    ) is False
    assert batch.is_expired_at(
        datetime(2026, 7, 19, 18, 0)
    ) is True


def test_valid_batch_lifecycle() -> None:
    batch = make_batch()

    batch.release()
    batch.mark_depleted()

    assert batch.status == BatchStatus.DEPLETED


def test_depleted_batch_cannot_be_cancelled() -> None:
    batch = make_batch()
    batch.release()
    batch.mark_depleted()

    with pytest.raises(ValueError):
        batch.cancel()


def test_display_name() -> None:
    batch = make_batch()

    assert (
        batch.display_name
        == "F-18 FDG — Batch FDG-20260719-001 [created]"
    )
