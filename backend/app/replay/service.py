import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Event, Session as SessionModel

def get_session_events(db: Session, session_id: int):
    """
    Return all ordered, persisted events for the requested session.
    Preserves exact contract: returns None if session not found, or List[Event].
    """
    if db.get(SessionModel, session_id) is None:
        return None
    return (
        db.query(Event)
        .filter(Event.session_id == session_id)
        .order_by(Event.timestamp.asc(), Event.id.asc())
        .all()
    )

def reconstruct_editor_state(events: List[Any]) -> List[Dict[str, Any]]:
    """
    Reconstruct the editor buffer state deterministically across an ordered timeline of events.
    Handles insert, delete, paste, and snapshot events.
    Returns enriched timeline entries with `reconstructed_code`, `char_count`, `line_count`.
    """
    reconstructed_timeline = []
    current_buffer = ""

    for idx, ev in enumerate(events):
        event_type = getattr(ev, "event_type", None) or (ev.get("event_type", "") if isinstance(ev, dict) else "")
        raw_data = getattr(ev, "data", "") or (ev.get("data", "") if isinstance(ev, dict) else "")
        ev_id = getattr(ev, "id", None) or (ev.get("id") if isinstance(ev, dict) else idx + 1)
        ev_ts = getattr(ev, "timestamp", 0) or (ev.get("timestamp", 0) if isinstance(ev, dict) else 0)

        # Parse structured payload if present
        payload_text = raw_data
        parsed_json = None
        if raw_data and (raw_data.startswith("{") or raw_data.startswith("[")):
            try:
                parsed_json = json.loads(raw_data)
                if isinstance(parsed_json, dict):
                    # Check for explicit code snapshot in payload
                    if "code" in parsed_json:
                        payload_text = parsed_json["code"]
                    elif "text" in parsed_json:
                        payload_text = parsed_json["text"]
            except Exception:
                pass

        if event_type == "insert":
            if parsed_json and "text" in parsed_json:
                current_buffer += str(parsed_json["text"])
            else:
                current_buffer += payload_text
        elif event_type == "paste":
            if parsed_json and "text" in parsed_json:
                current_buffer += str(parsed_json["text"])
            else:
                current_buffer += payload_text
        elif event_type == "delete":
            count = 1
            if parsed_json and "count" in parsed_json:
                try:
                    count = int(parsed_json["count"])
                except Exception:
                    count = 1
            elif parsed_json and "length" in parsed_json:
                try:
                    count = int(parsed_json["length"])
                except Exception:
                    count = 1
            elif len(payload_text) > 0:
                count = len(payload_text)
            current_buffer = current_buffer[:-count] if count <= len(current_buffer) else ""
        elif event_type in ("run", "submit"):
            if parsed_json and "code" in parsed_json and parsed_json["code"]:
                current_buffer = parsed_json["code"]
            elif payload_text and not payload_text.startswith("{"):
                current_buffer = payload_text

        lines = current_buffer.splitlines() or [""]
        reconstructed_timeline.append({
            "id": ev_id,
            "session_id": getattr(ev, "session_id", None) or (ev.get("session_id") if isinstance(ev, dict) else None),
            "timestamp": ev_ts,
            "event_type": event_type,
            "data": raw_data,
            "reconstructed_code": current_buffer,
            "char_count": len(current_buffer),
            "line_count": len(lines),
        })

    return reconstructed_timeline
