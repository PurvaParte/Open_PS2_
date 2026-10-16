import json
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import Event, Session as SessionModel

ALLOWED_EVENT_TYPES = {
    "insert",
    "delete",
    "paste",
    "run",
    "focus",
    "blur",
    "focus_change",
    "tab_visibility",
    "submit",
    "other",
}

class SessionNotFoundError(Exception):
    """Raised when the target session does not exist."""
    pass

class InvalidEventError(Exception):
    """Raised when event attributes fail validation."""
    pass

def record_event(db: Session, session_id: int, timestamp: int, event_type: str, data: str):
    """
    Validate, normalize, and persist an editor or session event.
    Returns the persisted Event model instance including its assigned ID.
    """
    if not isinstance(session_id, int) or session_id <= 0:
        raise InvalidEventError(f"Invalid session_id: {session_id}")

    session = db.get(SessionModel, session_id)
    if session is None:
        raise SessionNotFoundError(f"Session {session_id} does not exist")

    if not isinstance(timestamp, int) or timestamp < 0:
        raise InvalidEventError(f"Invalid timestamp: {timestamp}. Must be non-negative integer ms.")

    norm_type = str(event_type).strip().lower()
    if norm_type not in ALLOWED_EVENT_TYPES:
        norm_type = "other"

    # Normalize data payload
    if data is None:
        norm_data = ""
    elif isinstance(data, (dict, list)):
        norm_data = json.dumps(data, ensure_ascii=False)
    else:
        norm_data = str(data)

    # Avoid duplicate events if identical event arrived within same session at exact same millisecond
    existing = db.query(Event).filter(
        Event.session_id == session_id,
        Event.timestamp == timestamp,
        Event.event_type == norm_type,
        Event.data == norm_data,
    ).first()
    if existing:
        return existing

    event = Event(
        session_id=session_id,
        timestamp=timestamp,
        event_type=norm_type,
        data=norm_data,
    )
    db.add(event)
    try:
        db.commit()
        db.refresh(event)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RuntimeError(f"Database error while persisting event: {str(exc)}") from exc

    return event
