import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.models import Session as SessionModel, Event
from app.events.recorder import record_event, SessionNotFoundError, InvalidEventError

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_record_valid_event(db_session):
    s = SessionModel(student_id="test_student", started_at="2026-10-17T00:00:00Z")
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)

    event = record_event(db_session, s.id, 1200, "insert", "def solution():")
    assert event.id is not None
    assert event.session_id == s.id
    assert event.timestamp == 1200
    assert event.event_type == "insert"
    assert event.data == "def solution():"

def test_record_event_nonexistent_session(db_session):
    with pytest.raises(SessionNotFoundError):
        record_event(db_session, 9999, 100, "insert", "abc")

def test_record_event_invalid_timestamp(db_session):
    s = SessionModel(student_id="test_student", started_at="2026-10-17T00:00:00Z")
    db_session.add(s)
    db_session.commit()

    with pytest.raises(InvalidEventError):
        record_event(db_session, s.id, -50, "insert", "abc")

def test_record_event_normalizes_unknown_type(db_session):
    s = SessionModel(student_id="test_student", started_at="2026-10-17T00:00:00Z")
    db_session.add(s)
    db_session.commit()

    ev = record_event(db_session, s.id, 500, "CUSTOM_UNKNOWN_TYPE", "data")
    assert ev.event_type == "other"

def test_record_event_idempotency(db_session):
    s = SessionModel(student_id="test_student", started_at="2026-10-17T00:00:00Z")
    db_session.add(s)
    db_session.commit()

    ev1 = record_event(db_session, s.id, 1000, "insert", "code")
    ev2 = record_event(db_session, s.id, 1000, "insert", "code")
    assert ev1.id == ev2.id
