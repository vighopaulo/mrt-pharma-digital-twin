from math import isclose
from uuid import UUID

import pytest

from mrt.core.entities.room import Room
from mrt.core.entities.transport_request import TransportMode
from mrt.core.entities.transport_route import (
    RouteStatus,
    TransportRoute,
)


def make_route(
    *,
    bidirectional: bool = False,
) -> TransportRoute:
    return TransportRoute(
        name="Hot Lab to Injection Room",
        origin_room=Room(name="Hot Lab"),
        destination_room=Room(name="Injection Room"),
        transport_mode=TransportMode.MRT,
        distance_m=120,
        nominal_speed_m_per_s=10,
        is_bidirectional=bidirectional,
    )


def test_route_stores_required_fields() -> None:
    route = make_route()

    assert route.name == "Hot Lab to Injection Room"
    assert route.distance_m == 120.0
    assert route.nominal_speed_m_per_s == 10.0
    assert route.status == RouteStatus.ACTIVE


def test_route_receives_unique_identifier() -> None:
    first = make_route()
    second = make_route()

    assert isinstance(first.id, UUID)
    assert isinstance(second.id, UUID)
    assert first.id != second.id


def test_route_name_is_trimmed() -> None:
    route = TransportRoute(
        name="  MRT Corridor A  ",
        origin_room=Room(name="Hot Lab"),
        destination_room=Room(name="PET Suite"),
        transport_mode=TransportMode.MRT,
        distance_m=80,
        nominal_speed_m_per_s=8,
    )

    assert route.name == "MRT Corridor A"


def test_origin_and_destination_must_differ() -> None:
    room = Room(name="Hot Lab")

    with pytest.raises(ValueError):
        TransportRoute(
            name="Invalid Route",
            origin_room=room,
            destination_room=room,
            transport_mode=TransportMode.MRT,
            distance_m=10,
            nominal_speed_m_per_s=1,
        )


@pytest.mark.parametrize("invalid_value", [0, -1, -0.5])
def test_non_positive_distance_is_rejected(
    invalid_value: float,
) -> None:
    with pytest.raises(ValueError):
        TransportRoute(
            name="Invalid Route",
            origin_room=Room(name="Hot Lab"),
            destination_room=Room(name="Injection Room"),
            transport_mode=TransportMode.MRT,
            distance_m=invalid_value,
            nominal_speed_m_per_s=1,
        )


def test_nominal_travel_time_calculation() -> None:
    route = make_route()

    assert route.nominal_travel_time_seconds == 12.0
    assert isclose(
        route.nominal_travel_time_minutes,
        0.2,
        rel_tol=1e-12,
    )


def test_directed_route_connects_only_forward_direction() -> None:
    route = make_route()

    assert route.connects(
        route.origin_room,
        route.destination_room,
    ) is True
    assert route.connects(
        route.destination_room,
        route.origin_room,
    ) is False


def test_bidirectional_route_connects_both_directions() -> None:
    route = make_route(bidirectional=True)

    assert route.connects(
        route.origin_room,
        route.destination_room,
    ) is True
    assert route.connects(
        route.destination_room,
        route.origin_room,
    ) is True


def test_route_accepts_only_matching_mode_when_active() -> None:
    route = make_route()

    assert route.can_accept_transport(TransportMode.MRT) is True
    assert route.can_accept_transport(TransportMode.MANUAL) is False


def test_inactive_route_rejects_transport() -> None:
    route = make_route()
    route.deactivate()

    assert route.status == RouteStatus.INACTIVE
    assert route.can_accept_transport(TransportMode.MRT) is False


def test_maintenance_route_can_be_reactivated() -> None:
    route = make_route()

    route.place_in_maintenance()
    assert route.status == RouteStatus.MAINTENANCE

    route.activate()
    assert route.status == RouteStatus.ACTIVE


def test_display_name() -> None:
    route = make_route()

    assert (
        route.display_name
        == "Hot Lab to Injection Room: "
        "Hot Lab → Injection Room [mrt/active]"
    )
