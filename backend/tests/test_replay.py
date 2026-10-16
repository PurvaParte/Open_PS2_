import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.models import Session as SessionModel, Event
from app.replay.service import get_session_events, reconstruct_editor_state

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

def test_get_session_events_ordered(db_session):
    s = SessionModel(student_id="replay_student")
    db_session.add(s)
    db_session.commit()

    # Add events out of chronological order
    db_session.add(Event(session_id=s.id, timestamp=5000, event_type="run", data=""))
    db_session.add(Event(session_id=s.id, timestamp=1000, event_type="insert", data="a"))
    db_session.add(Event(session_id=s.id, timestamp=3000, event_type="insert", data="b"))
    db_session.commit()

    events = get_session_events(db_session, s.id)
    assert len(events) == 3
    assert [e.timestamp for e in events] == [1000, 3000, 5000]

def test_get_session_events_nonexistent_session(db_session):
    assert get_session_events(db_session, 9999) is None

def test_reconstruct_editor_state():
    mock_events = [
        {"id": 1, "session_id": 1, "timestamp": 100, "event_type": "insert", "data": "def solve():"},
        {"id": 2, "session_id": 1, "timestamp": 200, "event_type": "insert", "data": "\n    return 42"},
        {"id": 3, "session_id": 1, "timestamp": 300, "event_type": "delete", "data": "2"},
        {"id": 4, "session_id": 1, "timestamp": 400, "event_type": "insert", "data": "0"},
        {"id": 5, "session_id": 1, "timestamp": 500, "event_type": "run", "data": ""},
    ]
    timeline = reconstruct_editor_state(mock_events)
    assert len(timeline) == 5
    # Check intermediate states
    assert timeline[0]["reconstructed_code"] == "def solve():"
    assert timeline[1]["reconstructed_code"] == "def solve():\n    return 42"
    assert timeline[2]["reconstructed_code"] == "def solve():\n    return 4"
    assert timeline[3]["reconstructed_code"] == "def solve():\n    return 40"
    assert timeline[4]["reconstructed_code"] == "def solve():\n    return 40"
