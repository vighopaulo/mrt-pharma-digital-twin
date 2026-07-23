"""Reusable deterministic comparison logic."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from numbers import Real
from typing import Any

from ..similarity_score import SectionSimilarityScore


class BaseSectionComparator:
    """Compare normalized observations for one signature section."""

    section_name: str = ""

    def compare(
        self,
        reference: Mapping[str, Any],
        candidate: Mapping[str, Any],
    ) -> SectionSimilarityScore:
        all_fields = sorted(set(reference) | set(candidate))
        common_fields = sorted(set(reference) & set(candidate))
        missing_fields = tuple(
            field for field in all_fields if field not in common_fields
        )

        if not common_fields:
            return SectionSimilarityScore(
                section=self.section_name,
                score=0.0,
                compared_fields=0,
                matched_fields=0,
                missing_fields=missing_fields,
                explanations=("No common fields were available for comparison.",),
            )

        field_scores: list[float] = []
        explanations: list[str] = []
        matched = 0

        for field in common_fields:
            score = self._value_similarity(reference[field], candidate[field])
            field_scores.append(score)
            if score >= 0.999999:
                matched += 1
            explanations.append(
                f"{field}: {score * 100.0:.1f}% similar."
            )

        return SectionSimilarityScore(
            section=self.section_name,
            score=sum(field_scores) / len(field_scores),
            compared_fields=len(common_fields),
            matched_fields=matched,
            missing_fields=missing_fields,
            explanations=tuple(explanations),
        )

    def _value_similarity(self, left: Any, right: Any) -> float:
        if left is None or right is None:
            return 1.0 if left is right else 0.0

        if isinstance(left, bool) or isinstance(right, bool):
            return 1.0 if left == right else 0.0

        if isinstance(left, Real) and isinstance(right, Real):
            return self._numeric_similarity(float(left), float(right))

        if isinstance(left, str) and isinstance(right, str):
            return 1.0 if left.strip().casefold() == right.strip().casefold() else 0.0

        if isinstance(left, Mapping) and isinstance(right, Mapping):
            nested = BaseSectionComparator()
            nested.section_name = self.section_name
            return nested.compare(left, right).score

        if self._is_sequence(left) and self._is_sequence(right):
            return self._sequence_similarity(left, right)

        return 1.0 if left == right else 0.0

    @staticmethod
    def _numeric_similarity(left: float, right: float) -> float:
        if left == right:
            return 1.0

        scale = max(abs(left), abs(right), 1.0)
        return max(0.0, 1.0 - abs(left - right) / scale)

    @staticmethod
    def _is_sequence(value: Any) -> bool:
        return isinstance(value, Sequence) and not isinstance(
            value, (str, bytes, bytearray)
        )

    @staticmethod
    def _sequence_similarity(left: Sequence[Any], right: Sequence[Any]) -> float:
        try:
            left_set = set(left)
            right_set = set(right)
        except TypeError:
            return 1.0 if list(left) == list(right) else 0.0

        union = left_set | right_set
        if not union:
            return 1.0
        return len(left_set & right_set) / len(union)
