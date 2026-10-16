from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database.database import Base, engine, SessionLocal
from app.schemas import EventCreate
from app.events.recorder import record_event
from app.replay import get_session_events
from app.integrity import analyze_session
from app.models import Session as SessionModel
from app.models import Event
from app.models import IntegritySignal

Base.metadata.create_all(bind=engine)

app = FastAPI(title="EvidentAI API", version="1.0.0")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message":"EvidentAI Backend Running","database":"Connected"}

@app.post("/record_event")
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    return record_event(db,event.session_id,event.timestamp,event.event_type,event.data)

@app.get("/replay/{session_id}")
def replay_session(session_id:int, db: Session = Depends(get_db)):
    return get_session_events(db, session_id)

@app.get("/analyze/{session_id}")
def analyze(session_id:int, db: Session = Depends(get_db)):
    events = get_session_events(db, session_id)
    return analyze_session(events)

