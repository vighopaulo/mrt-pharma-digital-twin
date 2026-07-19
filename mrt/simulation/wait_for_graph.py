from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable


@dataclass(frozen=True, slots=True)
class WaitForCycle:
    """A detected cycle in a wait-for graph."""

    nodes: tuple[Hashable, ...]

    def __post_init__(self) -> None:
        if len(self.nodes) < 2:
            raise ValueError("a wait-for cycle requires at least two nodes.")
        if self.nodes[0] != self.nodes[-1]:
            raise ValueError("a wait-for cycle must start and end at the same node.")


class WaitForGraph:
    """Directed graph used to detect cyclic resource waits."""

    def __init__(self) -> None:
        self._edges: dict[Hashable, set[Hashable]] = {}

    @property
    def node_count(self) -> int:
        nodes = set(self._edges)
        for targets in self._edges.values():
            nodes.update(targets)
        return len(nodes)

    @property
    def edge_count(self) -> int:
        return sum(len(targets) for targets in self._edges.values())

    def add_wait(self, waiter: Hashable, holder: Hashable) -> None:
        if waiter == holder:
            raise ValueError("a node cannot wait for itself.")
        self._edges.setdefault(waiter, set()).add(holder)
        self._edges.setdefault(holder, set())

    def remove_wait(self, waiter: Hashable, holder: Hashable) -> None:
        targets = self._edges.get(waiter)
        if targets is None:
            return
        targets.discard(holder)

    def remove_node(self, node: Hashable) -> None:
        self._edges.pop(node, None)
        for targets in self._edges.values():
            targets.discard(node)

    def successors(self, node: Hashable) -> tuple[Hashable, ...]:
        return tuple(self._edges.get(node, ()))

    def detect_cycles(self) -> tuple[WaitForCycle, ...]:
        visited: set[Hashable] = set()
        active: set[Hashable] = set()
        stack: list[Hashable] = []
        cycles: list[WaitForCycle] = []
        canonical_seen: set[tuple[str, ...]] = set()

        def canonicalize(cycle: list[Hashable]) -> tuple[str, ...]:
            body = cycle[:-1]
            rendered = [repr(item) for item in body]
            rotations = [
                tuple(rendered[index:] + rendered[:index])
                for index in range(len(rendered))
            ]
            reversed_rendered = list(reversed(rendered))
            rotations.extend(
                tuple(reversed_rendered[index:] + reversed_rendered[:index])
                for index in range(len(reversed_rendered))
            )
            return min(rotations)

        def visit(node: Hashable) -> None:
            visited.add(node)
            active.add(node)
            stack.append(node)

            for successor in self._edges.get(node, ()):
                if successor not in visited:
                    visit(successor)
                elif successor in active:
                    start = stack.index(successor)
                    cycle_nodes = stack[start:] + [successor]
                    canonical = canonicalize(cycle_nodes)
                    if canonical not in canonical_seen:
                        canonical_seen.add(canonical)
                        cycles.append(WaitForCycle(tuple(cycle_nodes)))

            stack.pop()
            active.remove(node)

        for node in tuple(self._edges):
            if node not in visited:
                visit(node)

        return tuple(cycles)

    def has_cycle(self) -> bool:
        return bool(self.detect_cycles())
