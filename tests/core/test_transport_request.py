from datetime import datetime
from uuid import UUID

import pytest

from mrt.core.entities.patient import Patient
from mrt.core.entities.radiopharmaceutical_prescription import (
    RadiopharmaceuticalPrescription,
)
from mrt.core.entities.room import Room
from mrt.core.entities.transport_request import (
    TransportMode,
    TransportRequest,
    TransportRequestStatus,
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


def make_dose() -> RadiopharmaceuticalDose:
    patient = Patient(
        patient_reference="PAT-0001",
        name="Example Patient",
    )
    plan = TreatmentPlan(
        patient=patient,
        treatment_name="PET Imaging",
    )
    prescription = RadiopharmaceuticalPrescription(
        treatment_plan=plan,
        radiopharmaceutical_name="F-18 FDG",
        activity_mbq=370,
        calibration_at=datetime(2026, 7, 19, 9, 0),
    )
    batch = RadiopharmaceuticalBatch(
        batch_number="FDG-20260719-001",
        product_name="F-18 FDG",
        radionuclide=Radionuclide(
            symbol="F-18",
            name="Fluorine-18",
            half_life_minutes=109.77,
        ),
        initial_activity_mbq=10000,
        produced_at=datetime(2026, 7, 19, 7, 30),
        calibration_at=datetime(2026, 7, 19, 8, 0),
    )
    dose = RadiopharmaceuticalDose(
        dose_reference="DOSE-0001",
        prescription=prescription,
        batch=batch,
        dispensed_activity_mbq=370,
        dispensed_at=datetime(2026, 7, 19, 9, 0),
    )
    dose.release()
    return dose


def make_request() -> TransportRequest:
    return TransportRequest(
        dose=make_dose(),
        origin_room=Room(name="Hot Lab"),
        destination_room=Room(name="Injection Room"),
        transport_mode=TransportMode.MRT,
        requested_at=datetime(2026, 7, 19, 9, 5),
        priority=2,
    )


def test_transport_request_stores_required_fields() -> None:
    request = make_request()

    assert request.transport_mode == TransportMode.MRT
    assert request.priority == 2
    assert request.status == TransportRequestStatus.CREATED


def test_transport_request_receives_unique_identifier() -> None:
    first = make_request()
    second = make_request()

    assert isinstance(first.id, UUID)
    assert isinstance(second.id, UUID)
    assert first.id != second.id


def test_request_links_dose_and_patient() -> None:
    request = make_request()

    assert request.dose_id == request.dose.id
    assert request.patient_id == request.dose.patient_id


def test_origin_and_destination_must_differ() -> None:
    room = Room(name="Hot Lab")

    with pytest.raises(ValueError):
        TransportRequest(
            dose=make_dose(),
            origin_room=room,
            destination_room=room,
            transport_mode=TransportMode.MRT,
            requested_at=datetime(2026, 7, 19, 9, 5),
        )


@pytest.mark.parametrize("invalid_priority", [0, 6, -1])
def test_priority_outside_range_is_rejected(
    invalid_priority: int,
) -> None:
    with pytest.raises(ValueError):
        TransportRequest(
            dose=make_dose(),
            origin_room=Room(name="Hot Lab"),
            destination_room=Room(name="Injection Room"),
            transport_mode=TransportMode.MRT,
            requested_at=datetime(2026, 7, 19, 9, 5),
            priority=invalid_priority,
        )


def test_valid_transport_lifecycle() -> None:
    request = make_request()

    request.dispatch(datetime(2026, 7, 19, 9, 6))
    request.start_transport()
    request.deliver(datetime(2026, 7, 19, 9, 8))

    assert request.status == TransportRequestStatus.DELIVERED
    assert request.dose.status == DoseStatus.RECEIVED
    assert request.elapsed_minutes == 2.0


def test_dispatch_cannot_precede_request() -> None:
    request = make_request()

    with pytest.raises(ValueError):
        request.dispatch(datetime(2026, 7, 19, 9, 4))


def test_start_transport_requires_dispatched_status() -> None:
    request = make_request()

    with pytest.raises(ValueError):
        request.start_transport()


def test_delivered_request_cannot_be_cancelled() -> None:
    request = make_request()
    request.dispatch(datetime(2026, 7, 19, 9, 6))
    request.start_transport()
    request.deliver(datetime(2026, 7, 19, 9, 8))

    with pytest.raises(ValueError):
        request.cancel()


def test_display_name() -> None:
    request = make_request()

    assert (
        request.display_name
        == "DOSE-0001: Hot Lab → Injection Room [mrt/created]"
    )
