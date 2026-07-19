from datetime import datetime

from mrt.core.entities.patient import Patient
from mrt.core.entities.radiopharmaceutical_prescription import (
    RadiopharmaceuticalPrescription,
)
from mrt.core.entities.room import Room
from mrt.core.entities.transport_network import TransportNetwork
from mrt.core.entities.transport_request import (
    TransportMode,
    TransportRequest,
)
from mrt.core.entities.transport_route import TransportRoute
from mrt.core.entities.treatment_plan import TreatmentPlan
from mrt.radiation.entities.radiopharmaceutical_batch import (
    RadiopharmaceuticalBatch,
)
from mrt.radiation.entities.radiopharmaceutical_dose import (
    RadiopharmaceuticalDose,
)
from mrt.radiation.entities.radionuclide import Radionuclide


def test_transport_request_can_be_routed_through_network() -> None:
    hot_lab = Room(name="Hot Lab")
    junction = Room(name="MRT Junction")
    injection = Room(name="Injection Room")

    network = TransportNetwork(
        name="MRT Internal Network",
        routes=[
            TransportRoute(
                name="Segment A",
                origin_room=hot_lab,
                destination_room=junction,
                transport_mode=TransportMode.MRT,
                distance_m=60,
                nominal_speed_m_per_s=10,
            ),
            TransportRoute(
                name="Segment B",
                origin_room=junction,
                destination_room=injection,
                transport_mode=TransportMode.MRT,
                distance_m=40,
                nominal_speed_m_per_s=10,
            ),
        ],
    )

    patient = Patient(
        patient_reference="PAT-0001",
        name="Test Patient",
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
        batch_number="FDG-001",
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
        dose_reference="DOSE-001",
        prescription=prescription,
        batch=batch,
        dispensed_activity_mbq=370,
        dispensed_at=datetime(2026, 7, 19, 9, 0),
    )
    dose.release()

    request = TransportRequest(
        dose=dose,
        origin_room=hot_lab,
        destination_room=injection,
        transport_mode=TransportMode.MRT,
        requested_at=datetime(2026, 7, 19, 9, 5),
    )

    path = network.find_path(
        request.origin_room,
        request.destination_room,
        mode=request.transport_mode,
    )

    assert path.route_count == 2
    assert path.total_distance_m == 100.0
    assert path.total_travel_time_seconds == 10.0
