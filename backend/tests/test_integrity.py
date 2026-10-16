import pytest
from app.integrity.analyzer import analyze_session
from app.core.config import settings

class MockEvent:
    def __init__(self, id, timestamp, event_type, data=""):
        self.id = id
        self.timestamp = timestamp
        self.event_type = event_type
        self.data = data

def test_large_paste_rule():
    # Below threshold (e.g. 20 chars) -> no signal
    small_paste = [MockEvent(1, 1000, "paste", "x = 10")]
    signals = analyze_session(small_paste)
    assert len(signals) == 0

    # Above threshold (e.g. 60 chars) -> triggers Large Paste with medium severity
    large_paste_text = "def solution(nums):\n    total = 0\n    for n in nums:\n        total += n\n    return total"
    assert len(large_paste_text) >= settings.LARGE_PASTE_CHAR_THRESHOLD
    med_paste = [MockEvent(2, 2000, "paste", large_paste_text)]
    signals = analyze_session(med_paste)
    assert len(signals) == 1
    assert signals[0]["rule"] == "Large Paste"
    assert signals[0]["severity"] in ("medium", "high")
    assert "paste" in signals[0]["reason"].lower()

def test_rapid_insertion_rule():
    # Ordinary typing: 10 chars every 500ms -> should not trigger rapid insertion
    ordinary_typing = [
        MockEvent(i, i * 500, "insert", "c") for i in range(1, 10)
    ]
    signals = analyze_session(ordinary_typing)
    rapid_signals = [s for s in signals if s["rule"] == "Rapid Insertion"]
    assert len(rapid_signals) == 0

    # Rapid burst: 250 characters typed in 1000ms across multiple events
    burst_events = [
        MockEvent(1, 100, "insert", "a" * 80),
        MockEvent(2, 400, "insert", "b" * 80),
        MockEvent(3, 800, "insert", "c" * 80),
    ]
    signals = analyze_session(burst_events)
    rapid_signals = [s for s in signals if s["rule"] == "Rapid Insertion"]
    assert len(rapid_signals) >= 1
    assert rapid_signals[0]["evidence"]["total_chars"] == 240

def test_low_edit_cycle_rule():
    # Two consecutive runs with 0 edits in between -> triggers Low Edit Cycle observation
    events = [
        MockEvent(1, 1000, "insert", "x = 1"),
        MockEvent(2, 2000, "run", ""),
        MockEvent(3, 2500, "run", ""),
    ]
    signals = analyze_session(events)
    low_edit_signals = [s for s in signals if s["rule"] == "Low Edit Cycle"]
    assert len(low_edit_signals) == 1
    assert "consecutive" in low_edit_signals[0]["reason"].lower()

def test_insufficient_events_no_false_positive():
    # Only 1 run, 1 insert -> insufficient evidence
    events = [
        MockEvent(1, 1000, "insert", "x = 1"),
        MockEvent(2, 2000, "run", "")
    ]
    signals = analyze_session(events)
    assert len(signals) == 0

def test_signals_link_to_event_ids_and_timestamps():
    events = [
        MockEvent(42, 5500, "paste", "def solution(nums):\n" + "x = 1\n" * 20),
    ]
    signals = analyze_session(events)
    assert len(signals) >= 1
    assert signals[0]["event_id"] == 42
    assert signals[0]["timestamp"] == 5500
    assert signals[0]["review_guidance"] is not None
