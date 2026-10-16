from sqlalchemy.orm import Session
from app.models import Event, Session as SessionModel

def get_session_events(db: Session, session_id: int):
    if db.get(SessionModel, session_id) is None:
        return None
    return db.query(Event).filter(Event.session_id == session_id).order_by(Event.timestamp.asc(), Event.id.asc()).all()
