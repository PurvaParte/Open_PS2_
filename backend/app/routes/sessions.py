import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models import Session as SessionModel, Event, IntegritySignal
from app.schemas import (
    EventCreate,
    EventOut,
    SessionCreate,
    SessionOut,
    IntegritySignalOut,
)
from app.events.recorder import record_event, SessionNotFoundError, InvalidEventError
from app.replay.service import get_session_events, reconstruct_editor_state
from app.integrity.analyzer import analyze_session

router = APIRouter(tags=["Sessions & Integrity"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Session endpoints
@router.post("/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_session(data: SessionCreate, db: Session = Depends(get_db)):
    started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    session = SessionModel(student_id=data.student_id, started_at=started_at)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/sessions", response_model=List[SessionOut])
def list_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(SessionModel).order_by(SessionModel.id.desc()).offset(skip).limit(limit).all()

@router.get("/sessions/{session_id}", response_model=SessionOut)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.get(SessionModel, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return session

@router.post("/sessions/{session_id}/end", response_model=SessionOut)
def end_session(session_id: int, db: Session = Depends(get_db)):
    session = db.get(SessionModel, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    session.ended_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    db.commit()
    db.refresh(session)
    return session

# Event recording
@router.post("/record_event", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def post_event(event: EventCreate, db: Session = Depends(get_db)):
    try:
        return record_event(db, event.session_id, event.timestamp, event.event_type, event.data)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidEventError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error recording event: {str(e)}")

# Replay
@router.get("/replay/{session_id}")
def replay_session(session_id: int, db: Session = Depends(get_db)):
    events = get_session_events(db, session_id)
    if events is None:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return events

@router.get("/replay/{session_id}/timeline")
def replay_timeline(session_id: int, db: Session = Depends(get_db)):
    events = get_session_events(db, session_id)
    if events is None:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return reconstruct_editor_state(events)

# Integrity Analysis
@router.get("/analyze/{session_id}")
def analyze(session_id: int, db: Session = Depends(get_db)):
    events = get_session_events(db, session_id)
    if events is None:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return analyze_session(events)

@router.post("/analyze/{session_id}/save")
def analyze_and_save(session_id: int, db: Session = Depends(get_db)):
    events = get_session_events(db, session_id)
    if events is None:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    signals_data = analyze_session(events)

    # Replace previous signals for deterministic idempotency
    db.query(IntegritySignal).filter(IntegritySignal.session_id == session_id).delete()
    persisted = []
    for sig in signals_data:
        record = IntegritySignal(
            session_id=session_id,
            rule_name=sig.get("rule_name") or sig.get("rule", "Unknown"),
            severity=sig.get("severity", "medium"),
            event_id=sig.get("event_id"),
            timestamp=sig.get("timestamp"),
            reason=sig.get("reason", ""),
            review_guidance=sig.get("review_guidance", ""),
        )
        db.add(record)
        persisted.append(record)
    db.commit()
    for p in persisted:
        db.refresh(p)
    return persisted

@router.get("/signals/{session_id}", response_model=List[IntegritySignalOut])
def get_signals(session_id: int, db: Session = Depends(get_db)):
    session = db.get(SessionModel, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return (
        db.query(IntegritySignal)
        .filter(IntegritySignal.session_id == session_id)
        .order_by(IntegritySignal.timestamp.asc(), IntegritySignal.id.asc())
        .all()
    )
