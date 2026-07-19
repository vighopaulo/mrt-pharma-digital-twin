import pytest

from mrt.simulation.wait_for_graph import WaitForGraph


def test_detects_simple_two_node_cycle() -> None:
    graph = WaitForGraph()
    graph.add_wait("request-a", "request-b")
    graph.add_wait("request-b", "request-a")

    cycles = graph.detect_cycles()

    assert len(cycles) == 1
    assert set(cycles[0].nodes[:-1]) == {
        "request-a",
        "request-b",
    }


def test_detects_three_node_cycle() -> None:
    graph = WaitForGraph()
    graph.add_wait("a", "b")
    graph.add_wait("b", "c")
    graph.add_wait("c", "a")

    assert graph.has_cycle() is True


def test_acyclic_graph_has_no_cycles() -> None:
    graph = WaitForGraph()
    graph.add_wait("a", "b")
    graph.add_wait("b", "c")

    assert graph.detect_cycles() == ()


def test_removing_wait_breaks_cycle() -> None:
    graph = WaitForGraph()
    graph.add_wait("a", "b")
    graph.add_wait("b", "a")

    graph.remove_wait("b", "a")

    assert graph.has_cycle() is False


def test_self_wait_is_rejected() -> None:
    graph = WaitForGraph()

    with pytest.raises(ValueError):
        graph.add_wait("a", "a")


def test_node_and_edge_counts() -> None:
    graph = WaitForGraph()
    graph.add_wait("a", "b")
    graph.add_wait("a", "c")

    assert graph.node_count == 3
    assert graph.edge_count == 2
