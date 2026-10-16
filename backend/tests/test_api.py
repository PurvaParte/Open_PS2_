import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import Base, engine, SessionLocal
from app.database.seed import seed_initial_data

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_initial_data(db)
    db.close()
    with TestClient(app) as c:
        yield c

def test_home_and_health(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["database"] == "Connected"

    r_h = client.get("/health")
    assert r_h.status_code == 200
    assert r_h.json()["status"] == "healthy"

def test_session_lifecycle_and_events(client):
    # Create session
    r_s = client.post("/sessions", json={"student_id": "api_test_student"})
    assert r_s.status_code == 201
    s_id = r_s.json()["id"]

    # Record events
    r_e1 = client.post("/record_event", json={
        "session_id": s_id,
        "timestamp": 100,
        "event_type": "insert",
        "data": "def solution(nums):"
    })
    assert r_e1.status_code == 201
    ev1 = r_e1.json()
    assert ev1["id"] is not None

    r_e2 = client.post("/record_event", json={
        "session_id": s_id,
        "timestamp": 500,
        "event_type": "paste",
        "data": "x = 10\n" * 15  # large paste
    })
    assert r_e2.status_code == 201

    r_e3 = client.post("/record_event", json={
        "session_id": s_id,
        "timestamp": 2000,
        "event_type": "run",
        "data": ""
    })
    assert r_e3.status_code == 201

    # Replay
    r_rep = client.get(f"/replay/{s_id}")
    assert r_rep.status_code == 200
    events = r_rep.json()
    assert len(events) == 3

    # Replay timeline reconstruction
    r_tl = client.get(f"/replay/{s_id}/timeline")
    assert r_tl.status_code == 200
    assert len(r_tl.json()) == 3

    # Analyze
    r_an = client.get(f"/analyze/{s_id}")
    assert r_an.status_code == 200
    signals = r_an.json()
    assert any(s["rule"] == "Large Paste" for s in signals)

    # Save signals
    r_save = client.post(f"/analyze/{s_id}/save")
    assert r_save.status_code == 200

    # Retrieve signals
    r_sig = client.get(f"/signals/{s_id}")
    assert r_sig.status_code == 200
    assert len(r_sig.json()) >= 1

    # End session
    r_end = client.post(f"/sessions/{s_id}/end")
    assert r_end.status_code == 200
    assert r_end.json()["ended_at"] is not None

def test_code_execution_and_submission(client):
    # List questions
    r_q = client.get("/api/questions")
    assert r_q.status_code == 200
    questions = r_q.json()
    assert len(questions) > 0
    q1 = questions[0]

    # Create session
    r_s = client.post("/sessions", json={"student_id": "submit_student"})
    s_id = r_s.json()["id"]

    # Run code in sandbox (visible tests)
    code = "def solution(nums):\n    return sum(n for n in nums if n > 0)\n"
    r_run = client.post("/api/code/run", json={"code": code, "question_id": q1["id"]})
    assert r_run.status_code == 200
    assert r_run.json()["status"] == "passed"

    # Submit code (visible + hidden tests)
    r_sub = client.post("/api/submissions", json={
        "session_id": s_id,
        "student_id": "submit_student",
        "question_id": q1["id"],
        "code": code
    })
    assert r_sub.status_code == 201
    sub_data = r_sub.json()
    assert sub_data["status"] == "passed"
    assert len(sub_data["viva_questions"]) >= 1

    # Answer viva
    viva_q = sub_data["viva_questions"][0]
    r_ans = client.post("/api/viva/answer", json={
        "viva_question_id": viva_q["id"],
        "response_text": "I used a linear generator expression to sum positive numbers with O(N) complexity."
    })
    assert r_ans.status_code == 200
    assert r_ans.json()["score"] > 0
