from app.core.config import settings

def analyze_session(events):
    """Return explainable integrity signals; these are indicators, not proof of misconduct."""
    events = sorted(events, key=lambda e: (e.timestamp, e.id or 0))
    signals = []
    for event in events:
        data = event.data or ""
        if event.event_type == "paste" and len(data) >= settings.LARGE_PASTE_CHAR_THRESHOLD:
            high = len(data) >= settings.LARGE_PASTE_HIGH_SEVERITY_CHARS
            signals.append({"rule": "Large Paste", "severity": "high" if high else "medium", "event_id": event.id, "timestamp": event.timestamp, "reason": f"Paste event contained {len(data)} characters."})

    previous = None
    for event in events:
        data = event.data or ""
        if previous is not None:
            elapsed = event.timestamp - previous.timestamp
            if 0 <= elapsed <= settings.RAPID_INSERT_WINDOW_MS and event.event_type in ("insert", "paste") and len(data) >= settings.RAPID_INSERT_CHAR_THRESHOLD:
                signals.append({"rule": "Rapid Insertion", "severity": "medium", "event_id": event.id, "timestamp": event.timestamp, "reason": f"{len(data)} characters appeared within {elapsed} ms of the preceding event."})
        previous = event

    runs = sum(e.event_type == "run" for e in events)
    edits = sum(e.event_type in ("insert", "delete", "paste") for e in events)
    pasted_chars = sum(len(e.data or "") for e in events if e.event_type == "paste")
    deletes = sum(e.event_type == "delete" for e in events)
    if runs >= 2 and edits < runs and (pasted_chars >= settings.LOW_EDIT_MIN_PASTED_CHARS or deletes <= settings.LOW_EDIT_MAX_DELETES):
        signals.append({"rule": "Low Edit Cycle", "severity": "low", "event_id": None, "timestamp": None, "reason": f"Observed {runs} run events and {edits} edit events; review the timeline in context."})
    return signals
