"""Tests for the Build 43 event queue monitor."""

from dataclasses import dataclass

from ui.event_queue import event_rows


@dataclass
class FakeEvent:
    time: float
    priority: int
    event_type: str
    entity_id: str


class FakeEngine:
    event_queue = [
        FakeEvent(2.5, 1, "ARRIVAL", "patient-001"),
        FakeEvent(4.0, 2, "TRANSPORT", "dose-003"),
    ]


def test_event_rows_normalizes_pending_events() -> None:
    rows = event_rows(FakeEngine())

    assert len(rows) == 2
    assert rows[0]["Position"] == 1
    assert rows[0]["Time"] == 2.5
    assert rows[0]["Priority"] == 1
    assert rows[0]["Event Type"] == "ARRIVAL"
    assert rows[0]["Entity"] == "patient-001"


def test_event_rows_respects_limit() -> None:
    rows = event_rows(FakeEngine(), limit=1)

    assert len(rows) == 1


def test_event_rows_handles_missing_engine() -> None:
    assert event_rows(None) == []


def test_event_rows_supports_dictionary_events() -> None:
    class DictionaryEngine:
        event_queue = [
            {
                "scheduled_time": 7.0,
                "priority": 3,
                "kind": "SERVICE_COMPLETE",
                "resource_id": "scanner-01",
            }
        ]

    row = event_rows(DictionaryEngine())[0]

    assert row["Time"] == 7.0
    assert row["Priority"] == 3
    assert row["Event Type"] == "SERVICE_COMPLETE"
    assert row["Entity"] == "scanner-01"
