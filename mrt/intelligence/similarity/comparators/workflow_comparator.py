"""Comparator for the workflow signature section."""

from .base_comparator import BaseSectionComparator


class WorkflowComparator(BaseSectionComparator):
    section_name = "workflow"
