import pytest

from mrt.core.entities.room import Room
from mrt.core.entities.transport_network import (
    RouteOptimizationCriterion,
    TransportNetwork,
)
from mrt.core.entities.transport_request import TransportMode
from mrt.core.entities.transport_route import TransportRoute


def make_rooms() -> tuple[Room, Room, Room]:
    return (
        Room(name="Hot Lab"),
        Room(name="Injection Room"),
        Room(name="PET Suite"),
    )


def make_route(
    name: str,
    origin: Room,
    destination: Room,
    *,
    distance: float,
    speed: float,
    mode: TransportMode = TransportMode.MRT,
    bidirectional: bool = False,
) -> TransportRoute:
    return TransportRoute(
        name=name,
        origin_room=origin,
        destination_room=destination,
        transport_mode=mode,
        distance_m=distance,
        nominal_speed_m_per_s=speed,
        is_bidirectional=bidirectional,
    )


def test_network_owns_routes_and_counts_rooms() -> None:
    hot_lab, injection, pet = make_rooms()
    network = TransportNetwork(
        name="Nuclear Medicine Network",
        routes=[
            make_route(
                "Route A",
                hot_lab,
                injection,
                distance=100,
                speed=10,
            ),
            make_route(
                "Route B",
                injection,
                pet,
                distance=50,
                speed=5,
            ),
        ],
    )

    assert network.route_count == 2
    assert network.room_count == 3


def test_duplicate_route_is_rejected() -> None:
    hot_lab, injection, _ = make_rooms()
    route = make_route(
        "Route A",
        hot_lab,
        injection,
        distance=100,
        speed=10,
    )
    network = TransportNetwork("Network", routes=[route])

    with pytest.raises(ValueError):
        network.add_route(route)


def test_direct_path_is_found() -> None:
    hot_lab, injection, _ = make_rooms()
    route = make_route(
        "Direct",
        hot_lab,
        injection,
        distance=120,
        speed=10,
    )
    network = TransportNetwork("Network", routes=[route])

    path = network.find_path(hot_lab, injection)

    assert path.route_count == 1
    assert path.total_distance_m == 120.0
    assert path.total_travel_time_seconds == 12.0
    assert path.room_sequence == (hot_lab, injection)


def test_multisegment_path_is_found() -> None:
    hot_lab, injection, pet = make_rooms()
    network = TransportNetwork(
        "Network",
        routes=[
            make_route(
                "A",
                hot_lab,
                injection,
                distance=100,
                speed=10,
            ),
            make_route(
                "B",
                injection,
                pet,
                distance=50,
                speed=5,
            ),
        ],
    )

    path = network.find_path(hot_lab, pet)

    assert path.route_count == 2
    assert path.total_distance_m == 150.0
    assert path.total_travel_time_seconds == 20.0
    assert path.room_sequence == (hot_lab, injection, pet)


def test_travel_time_and_distance_can_select_different_paths() -> None:
    start = Room(name="Start")
    middle = Room(name="Middle")
    end = Room(name="End")

    network = TransportNetwork(
        "Network",
        routes=[
            make_route(
                "Short Slow A",
                start,
                middle,
                distance=40,
                speed=1,
            ),
            make_route(
                "Short Slow B",
                middle,
                end,
                distance=40,
                speed=1,
            ),
            make_route(
                "Long Fast",
                start,
                end,
                distance=120,
                speed=12,
            ),
        ],
    )

    shortest = network.find_path(
        start,
        end,
        criterion=RouteOptimizationCriterion.DISTANCE,
    )
    fastest = network.find_path(
        start,
        end,
        criterion=RouteOptimizationCriterion.TRAVEL_TIME,
    )

    assert shortest.route_count == 2
    assert shortest.total_distance_m == 80.0
    assert fastest.route_count == 1
    assert fastest.total_travel_time_seconds == 10.0


def test_mode_filter_excludes_incompatible_routes() -> None:
    hot_lab, injection, _ = make_rooms()
    manual_route = make_route(
        "Manual",
        hot_lab,
        injection,
        distance=50,
        speed=1,
        mode=TransportMode.MANUAL,
    )
    network = TransportNetwork("Network", routes=[manual_route])

    with pytest.raises(KeyError):
        network.find_path(
            hot_lab,
            injection,
            mode=TransportMode.MRT,
        )


def test_inactive_route_is_not_used() -> None:
    hot_lab, injection, _ = make_rooms()
    route = make_route(
        "Route A",
        hot_lab,
        injection,
        distance=50,
        speed=5,
    )
    route.deactivate()
    network = TransportNetwork("Network", routes=[route])

    with pytest.raises(KeyError):
        network.find_path(hot_lab, injection)


def test_bidirectional_route_supports_reverse_path() -> None:
    hot_lab, injection, _ = make_rooms()
    route = make_route(
        "Bidirectional",
        hot_lab,
        injection,
        distance=50,
        speed=5,
        bidirectional=True,
    )
    network = TransportNetwork("Network", routes=[route])

    reverse_path = network.find_path(injection, hot_lab)

    assert reverse_path.route_count == 1
    assert reverse_path.room_sequence == (injection, hot_lab)


def test_same_room_returns_empty_path() -> None:
    room = Room(name="Hot Lab")
    network = TransportNetwork("Network")

    path = network.find_path(room, room)

    assert path.route_count == 0
    assert path.total_distance_m == 0.0
    assert path.total_travel_time_seconds == 0.0
