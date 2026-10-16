import json
from typing import List, Dict, Any, Optional
from app.core.config import settings

def _format_time(ms: Optional[int]) -> str:
    if ms is None or ms < 0:
        return "00:00"
    total_sec = ms // 1000
    minutes = total_sec // 60
    seconds = total_sec % 60
    return f"{minutes:02d}:{seconds:02d}"

def _extract_event_info(ev: Any) -> Dict[str, Any]:
    """Helper to extract attributes whether ev is ORM object, dict, or schema."""
    if isinstance(ev, dict):
        ev_id = ev.get("id")
        timestamp = ev.get("timestamp", 0)
        event_type = ev.get("event_type", "other")
        data = ev.get("data", "")
    else:
        ev_id = getattr(ev, "id", None)
        timestamp = getattr(ev, "timestamp", 0)
        event_type = getattr(ev, "event_type", "other")
        data = getattr(ev, "data", "")

    if data is None:
        data = ""
    elif not isinstance(data, str):
        try:
            data = json.dumps(data)
        except Exception:
            data = str(data)

    return {
        "id": ev_id,
        "timestamp": int(timestamp) if timestamp is not None else 0,
        "event_type": str(event_type).lower(),
        "data": data,
    }

def analyze_session(events: List[Any]) -> List[Dict[str, Any]]:
    """
    Analyze session events to detect evidence-based integrity signals.
    Returns an ordered list of signals for human review.
    Signals are neutral observations, not proof of misconduct.
    """
    if not events:
        return []

    # Sort events deterministically by timestamp, then event id
    normalized = [_extract_event_info(e) for e in events]
    normalized.sort(key=lambda e: (e["timestamp"], e["id"] or 0))

    signals: List[Dict[str, Any]] = []

    # -------------------------------------------------------------
    # Rule 1: Large Paste
    # -------------------------------------------------------------
    for ev in normalized:
        if ev["event_type"] == "paste":
            data = ev["data"]
            char_count = len(data)
            if char_count >= settings.LARGE_PASTE_CHAR_THRESHOLD:
                is_high = char_count >= settings.LARGE_PASTE_HIGH_SEVERITY_CHARS
                lines = len(data.splitlines()) or 1
                signals.append({
                    "rule": "Large Paste",
                    "rule_name": "Large Paste",
                    "severity": "high" if is_high else "medium",
                    "event_id": ev["id"],
                    "timestamp": ev["timestamp"],
                    "reason": f"A paste of {char_count} characters ({lines} lines) was observed at {_format_time(ev['timestamp'])}.",
                    "evidence": {
                        "event_id": ev["id"],
                        "char_count": char_count,
                        "line_count": lines,
                        "sample": data[:80] + ("..." if char_count > 80 else "")
                    },
                    "review_guidance": "Inspect whether pasted content is template code, allowed library usage, or external pre-written code."
                })

    # -------------------------------------------------------------
    # Rule 2: Rapid Insertion (Sliding window burst detection)
    # -------------------------------------------------------------
    window_ms = settings.RAPID_INSERT_WINDOW_MS
    insert_threshold = settings.RAPID_INSERT_CHAR_THRESHOLD
    n = len(normalized)
    flagged_ranges = set()

    # Check for single event rapid insertion (backwards-compatibility & fast bursts)
    for ev in normalized:
        if ev["event_type"] in ("insert", "paste"):
            data = ev["data"]
            if len(data) >= insert_threshold and ev["event_type"] == "insert":
                signals.append({
                    "rule": "Rapid Insertion",
                    "rule_name": "Rapid Insertion",
                    "severity": "medium",
                    "event_id": ev["id"],
                    "timestamp": ev["timestamp"],
                    "reason": f"Single insertion event added {len(data)} characters at {_format_time(ev['timestamp'])}.",
                    "evidence": {
                        "event_id": ev["id"],
                        "char_count": len(data),
                        "sample": data[:80] + ("..." if len(data) > 80 else "")
                    },
                    "review_guidance": "Verify if the browser received an automated insertion, snippet expansion, or batch typing."
                })
                flagged_ranges.add(ev["id"])

    # Multi-event sliding window aggregation
    left = 0
    while left < n:
        if normalized[left]["event_type"] not in ("insert", "paste"):
            left += 1
            continue

        right = left
        burst_chars = 0
        window_events = []

        while right < n and (normalized[right]["timestamp"] - normalized[left]["timestamp"]) <= window_ms:
            if normalized[right]["event_type"] in ("insert", "paste"):
                burst_chars += len(normalized[right]["data"])
                window_events.append(normalized[right])
            right += 1

        elapsed = normalized[min(right - 1, n - 1)]["timestamp"] - normalized[left]["timestamp"]

        # Only trigger multi-event window if multiple events contributed and threshold exceeded
        if len(window_events) > 1 and burst_chars >= insert_threshold:
            first_ev = window_events[0]
            last_ev = window_events[-1]
            if first_ev["id"] not in flagged_ranges:
                signals.append({
                    "rule": "Rapid Insertion",
                    "rule_name": "Rapid Insertion",
                    "severity": "medium",
                    "event_id": first_ev["id"],
                    "timestamp": first_ev["timestamp"],
                    "reason": f"Observed rapid insertion of {burst_chars} characters within {elapsed} ms across {len(window_events)} events ({_format_time(first_ev['timestamp'])} to {_format_time(last_ev['timestamp'])}).",
                    "evidence": {
                        "event_ids": [e["id"] for e in window_events if e["id"]],
                        "total_chars": burst_chars,
                        "elapsed_ms": elapsed,
                        "event_count": len(window_events)
                    },
                    "review_guidance": "Check whether multi-line autocompletion, script injection, or rapid typing took place."
                })
                flagged_ranges.add(first_ev["id"])
                left = right
                continue

        left += 1

    # -------------------------------------------------------------
    # Rule 3: Low Observed Edit Cycle
    # -------------------------------------------------------------
    runs = [e for e in normalized if e["event_type"] == "run"]
    edits = [e for e in normalized if e["event_type"] in ("insert", "delete", "paste")]
    deletes = sum(1 for e in normalized if e["event_type"] == "delete")
    pasted_chars = sum(len(e["data"]) for e in normalized if e["event_type"] == "paste")

    if len(runs) >= 2:
        # Check edits between consecutive runs
        zero_edit_runs = 0
        for i in range(len(runs) - 1):
            run1 = runs[i]
            run2 = runs[i + 1]
            interim_edits = [
                e for e in normalized
                if run1["timestamp"] <= e["timestamp"] <= run2["timestamp"]
                and e["event_type"] in ("insert", "delete", "paste")
            ]
            if len(interim_edits) == 0:
                zero_edit_runs += 1

        if zero_edit_runs > 0:
            signals.append({
                "rule": "Low Edit Cycle",
                "rule_name": "Low Edit Cycle",
                "severity": "low",
                "event_id": runs[-1]["id"],
                "timestamp": runs[-1]["timestamp"],
                "reason": f"Observed consecutive executions with no recorded edits between runs at {_format_time(runs[-1]['timestamp'])}.",
                "evidence": {
                    "total_runs": len(runs),
                    "zero_edit_transitions": zero_edit_runs
                },
                "review_guidance": "Examine if the student re-ran existing code to verify intermittent behavior or environment output."
            })
        elif len(edits) < len(runs) and (pasted_chars >= settings.LOW_EDIT_MIN_PASTED_CHARS or deletes <= settings.LOW_EDIT_MAX_DELETES):
            signals.append({
                "rule": "Low Edit Cycle",
                "rule_name": "Low Edit Cycle",
                "severity": "low",
                "event_id": runs[0]["id"] if runs else None,
                "timestamp": runs[0]["timestamp"] if runs else None,
                "reason": f"Observed {len(runs)} executions with few recorded edits ({len(edits)} edits, {deletes} deletes, {pasted_chars} pasted chars).",
                "evidence": {
                    "runs": len(runs),
                    "edits": len(edits),
                    "deletes": deletes,
                    "pasted_chars": pasted_chars
                },
                "review_guidance": "Review the timeline in context. Student may have planned the solution before typing or imported a complete solution."
            })

    # Sort signals chronologically
    signals.sort(key=lambda s: (s["timestamp"] or 0, s["event_id"] or 0))
    return signals
