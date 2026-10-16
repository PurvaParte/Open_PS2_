from sqlalchemy.orm import Session
from app.models import Event, Session as SessionModel

class SessionNotFoundError(Exception):
    pass

def record_event(db: Session, session_id: int, timestamp: int, event_type: str, data: str):
    if db.get(SessionModel, session_id) is None:
        raise SessionNotFoundError(f"Session {session_id} does not exist")
    event = Event(session_id=session_id, timestamp=timestamp, event_type=event_type, data=data)
    db.add(event)
    try:
        db.commit()
        db.refresh(event)
    except Exception:
        db.rollback()
        raise
    return event
