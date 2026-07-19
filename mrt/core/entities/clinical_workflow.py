from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4

from mrt.core.entities.clinical_case import ClinicalCase
from mrt.core.entities.workflow_step import WorkflowStep, WorkflowStepStatus


class ClinicalWorkflowStatus(StrEnum):
    """Lifecycle states for a clinical workflow."""

    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class ClinicalWorkflow:
    """
    Represents the ordered operational workflow for one clinical case.

    The workflow owns an ordered set of WorkflowStep objects and coordinates
    their progression. Queueing, simulation timestamps, resource contention,
    stochastic durations, and optimization hooks are introduced later.
    """

    clinical_case: ClinicalCase
    name: str
    steps: list[WorkflowStep] = field(default_factory=list)
    status: ClinicalWorkflowStatus = ClinicalWorkflowStatus.DRAFT
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.clinical_case, ClinicalCase):
            raise TypeError(
                "clinical_case must be a ClinicalCase instance."
            )

        if not isinstance(self.name, str):
            raise TypeError("name must be a string.")

        normalized_name = self.name.strip()
        if not normalized_name:
            raise ValueError("name cannot be empty or whitespace.")
        self.name = normalized_name

        if not isinstance(self.status, ClinicalWorkflowStatus):
            raise TypeError(
                "status must be a ClinicalWorkflowStatus."
            )

        initial_steps = list(self.steps)
        self.steps = []
        for step in initial_steps:
            self.add_step(step)

    @property
    def clinical_case_id(self) -> UUID:
        return self.clinical_case.id

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def planned_duration_minutes(self) -> float:
        return sum(step.planned_duration_minutes for step in self.steps)

    @property
    def current_step(self) -> WorkflowStep | None:
        for step in self.steps:
            if step.status in {
                WorkflowStepStatus.READY,
                WorkflowStepStatus.IN_PROGRESS,
            }:
                return step
        return None

    @property
    def display_name(self) -> str:
        return (
            f"{self.name} — {self.clinical_case.display_name} "
            f"[{self.status.value}]"
        )

    def add_step(self, step: WorkflowStep) -> None:
        if not isinstance(step, WorkflowStep):
            raise TypeError("step must be a WorkflowStep instance.")

        if any(existing.id == step.id for existing in self.steps):
            raise ValueError("workflow step is already present.")

        if any(existing.sequence == step.sequence for existing in self.steps):
            raise ValueError(
                f"workflow already contains sequence {step.sequence}."
            )

        self.steps.append(step)
        self.steps.sort(key=lambda item: item.sequence)

    def get_step(self, sequence: int) -> WorkflowStep:
        for step in self.steps:
            if step.sequence == sequence:
                return step
        raise KeyError(f"no workflow step exists at sequence {sequence}.")

    def remove_step(self, sequence: int) -> WorkflowStep:
        if self.status != ClinicalWorkflowStatus.DRAFT:
            raise ValueError(
                "steps can only be removed while workflow is in draft."
            )

        step = self.get_step(sequence)
        self.steps.remove(step)
        return step

    def mark_ready(self) -> None:
        if self.status != ClinicalWorkflowStatus.DRAFT:
            raise ValueError("only a draft workflow can be marked ready.")

        if not self.steps:
            raise ValueError(
                "workflow must contain at least one step before it is ready."
            )

        self.status = ClinicalWorkflowStatus.READY
        self.steps[0].mark_ready()

    def start(self) -> None:
        if self.status != ClinicalWorkflowStatus.READY:
            raise ValueError("only a ready workflow can be started.")

        first_step = self.steps[0]
        first_step.start()
        self.status = ClinicalWorkflowStatus.IN_PROGRESS

    def complete_current_step(self) -> WorkflowStep:
        if self.status != ClinicalWorkflowStatus.IN_PROGRESS:
            raise ValueError(
                "workflow must be in progress to complete a step."
            )

        step = self.current_step
        if step is None:
            raise ValueError("workflow has no current step.")

        if step.status == WorkflowStepStatus.READY:
            step.start()

        step.complete()

        completed_index = self.steps.index(step)
        next_index = completed_index + 1

        if next_index < len(self.steps):
            self.steps[next_index].mark_ready()
        else:
            self.status = ClinicalWorkflowStatus.COMPLETED

        return step

    def cancel(self) -> None:
        if self.status == ClinicalWorkflowStatus.COMPLETED:
            raise ValueError("a completed workflow cannot be cancelled.")

        for step in self.steps:
            if step.status not in {
                WorkflowStepStatus.COMPLETED,
                WorkflowStepStatus.CANCELLED,
            }:
                step.cancel()

        self.status = ClinicalWorkflowStatus.CANCELLED
