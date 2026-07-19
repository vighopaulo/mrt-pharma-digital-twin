from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from heapq import heappop, heappush
from itertools import count
from typing import Any
from uuid import UUID, uuid4


class QueueDiscipline(StrEnum):
    FIFO = "fifo"
    PRIORITY = "priority"


@dataclass(frozen=True, slots=True)
class QueueEntry:
    """One entity waiting for a constrained simulation resource."""

    entity: Any
    entered_at: datetime
    priority: int = 0
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.entered_at, datetime):
            raise TypeError("entered_at must be a datetime.")
        if isinstance(self.priority, bool) or not isinstance(self.priority, int):
            raise TypeError("priority must be an integer.")


@dataclass(slots=True)
class ResourceQueue:
    """
    Queue for entities waiting for a constrained resource.

    FIFO serves by arrival order. PRIORITY serves the numerically lowest
    priority first, while preserving FIFO order among equal priorities.
    """

    name: str
    capacity: int | None = None
    discipline: QueueDiscipline = QueueDiscipline.FIFO
    _heap: list[tuple[int, int, QueueEntry]] = field(
        default_factory=list,
        init=False,
        repr=False,
    )
    _sequence: Any = field(default_factory=count, init=False, repr=False)
    _entry_ids: set[UUID] = field(default_factory=set, init=False, repr=False)
    maximum_length_observed: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("name must be a string.")
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("name cannot be empty.")

        if self.capacity is not None:
            if isinstance(self.capacity, bool) or not isinstance(self.capacity, int):
                raise TypeError("capacity must be an integer or None.")
            if self.capacity <= 0:
                raise ValueError("capacity must be greater than zero.")

        if not isinstance(self.discipline, QueueDiscipline):
            raise TypeError("discipline must be a QueueDiscipline.")

    @property
    def length(self) -> int:
        return len(self._heap)

    @property
    def is_empty(self) -> bool:
        return not self._heap

    @property
    def is_full(self) -> bool:
        return self.capacity is not None and self.length >= self.capacity

    def enqueue(
        self,
        entity: Any,
        entered_at: datetime,
        priority: int = 0,
    ) -> QueueEntry:
        if self.is_full:
            raise OverflowError(f"resource queue '{self.name}' is full.")

        entry = QueueEntry(
            entity=entity,
            entered_at=entered_at,
            priority=priority,
        )
        sequence = next(self._sequence)
        sort_priority = (
            priority
            if self.discipline == QueueDiscipline.PRIORITY
            else 0
        )
        heappush(self._heap, (sort_priority, sequence, entry))
        self._entry_ids.add(entry.id)
        self.maximum_length_observed = max(
            self.maximum_length_observed,
            self.length,
        )
        return entry

    def peek(self) -> QueueEntry:
        if self.is_empty:
            raise IndexError(f"resource queue '{self.name}' is empty.")
        return self._heap[0][2]

    def dequeue(self, service_started_at: datetime) -> QueueEntry:
        if not isinstance(service_started_at, datetime):
            raise TypeError("service_started_at must be a datetime.")
        if self.is_empty:
            raise IndexError(f"resource queue '{self.name}' is empty.")

        _, _, entry = heappop(self._heap)
        self._entry_ids.remove(entry.id)

        if service_started_at < entry.entered_at:
            heappush(
                self._heap,
                (
                    entry.priority
                    if self.discipline == QueueDiscipline.PRIORITY
                    else 0,
                    -1,
                    entry,
                ),
            )
            self._entry_ids.add(entry.id)
            raise ValueError(
                "service_started_at cannot be earlier than entered_at."
            )

        return entry

    def waiting_seconds(
        self,
        entry: QueueEntry,
        as_of: datetime,
    ) -> float:
        if not isinstance(entry, QueueEntry):
            raise TypeError("entry must be a QueueEntry.")
        if not isinstance(as_of, datetime):
            raise TypeError("as_of must be a datetime.")
        if entry.id not in self._entry_ids:
            raise KeyError("entry is not currently waiting in this queue.")
        if as_of < entry.entered_at:
            raise ValueError("as_of cannot be earlier than entered_at.")
        return (as_of - entry.entered_at).total_seconds()

    def clear(self) -> tuple[QueueEntry, ...]:
        entries: list[QueueEntry] = []
        while self._heap:
            entries.append(heappop(self._heap)[2])
        self._entry_ids.clear()
        return tuple(entries)
