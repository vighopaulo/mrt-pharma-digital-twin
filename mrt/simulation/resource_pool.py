from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class ResourceUnit:
    """One assignable unit within a constrained resource pool."""

    name: str
    payload: Any = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("name must be a string.")
        if not self.name.strip():
            raise ValueError("name cannot be empty.")


@dataclass(slots=True)
class ResourcePool:
    """Tracks available and allocated resource units."""

    name: str
    units: list[ResourceUnit]
    _available: list[ResourceUnit] = field(init=False, repr=False)
    _allocated: dict[UUID, ResourceUnit] = field(
        default_factory=dict,
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("name must be a string.")
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("name cannot be empty.")
        if not isinstance(self.units, list):
            raise TypeError("units must be a list.")
        if not self.units:
            raise ValueError("resource pool requires at least one unit.")
        if not all(isinstance(unit, ResourceUnit) for unit in self.units):
            raise TypeError("all units must be ResourceUnit instances.")
        if len({unit.id for unit in self.units}) != len(self.units):
            raise ValueError("resource units must have unique identities.")
        self._available = list(self.units)

    @property
    def total_capacity(self) -> int:
        return len(self.units)

    @property
    def available_count(self) -> int:
        return len(self._available)

    @property
    def allocated_count(self) -> int:
        return len(self._allocated)

    @property
    def has_available(self) -> bool:
        return bool(self._available)

    def acquire(self) -> ResourceUnit:
        if not self._available:
            raise RuntimeError(f"resource pool '{self.name}' is exhausted.")
        unit = self._available.pop(0)
        self._allocated[unit.id] = unit
        return unit

    def release(self, unit: ResourceUnit) -> None:
        if not isinstance(unit, ResourceUnit):
            raise TypeError("unit must be a ResourceUnit.")
        if unit.id not in self._allocated:
            raise KeyError("resource unit is not allocated from this pool.")
        released = self._allocated.pop(unit.id)
        self._available.append(released)
