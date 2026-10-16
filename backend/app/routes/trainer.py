import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import SessionLocal
from app.models import (
    Session as SessionModel,
    Event,
    IntegritySignal,
    StudentMastery,
    Concept,
    Submission,
    VivaQuestion,
    VivaResponse,
    ReviewNote,
)
from app.schemas import ReviewNoteCreate, ReviewNoteOut
from app.integrity.analyzer import analyze_session
from app.replay.service import reconstruct_editor_state

router = APIRouter(prefix="/api/trainer", tags=["Trainer & Reviewer Experience"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/overview")
def get_trainer_overview(db: Session = Depends(get_db)):
    """
    Overview for trainer dashboard:
    - Struggling concepts (average mastery across batch < 0.60)
    - Student count & list with mastery profiles
    - Recent coding sessions with signal indicators
    """
    concepts = db.query(Concept).all()
    concept_map = {c.id: c.name for c in concepts}

    # Calculate average mastery per concept
    mastery_stats = (
        db.query(
            StudentMastery.concept_id,
            func.avg(StudentMastery.mastery).label("avg_mastery"),
            func.count(StudentMastery.id).label("student_count")
        )
        .group_by(StudentMastery.concept_id)
        .all()
    )

    struggling_concepts = []
    for cid, avg_m, count in mastery_stats:
        avg_float = round(float(avg_m or 0.0), 3)
        struggling_concepts.append({
            "concept_id": cid,
            "concept_name": concept_map.get(cid, cid),
            "average_mastery": avg_float,
            "struggling": avg_float < 0.60,
            "students_tracked": count,
        })
    struggling_concepts.sort(key=lambda x: x["average_mastery"])

    # List unique students
    student_records = (
        db.query(
            StudentMastery.student_id,
            func.avg(StudentMastery.mastery).label("overall_mastery"),
            func.count(StudentMastery.id).label("concepts_tracked")
        )
        .group_by(StudentMastery.student_id)
        .all()
    )

    students = [
        {
            "student_id": s[0],
            "overall_mastery": round(float(s[1] or 0.0), 3),
            "concepts_tracked": s[2],
        }
        for s in student_records
    ]

    # Recent sessions
    recent_sessions_db = db.query(SessionModel).order_by(SessionModel.id.desc()).limit(20).all()
    recent_sessions = []
    for s in recent_sessions_db:
        signal_count = len(s.signals)
        latest_note = (
            db.query(ReviewNote)
            .filter(ReviewNote.session_id == s.id)
            .order_by(ReviewNote.id.desc())
            .first()
        )
        recent_sessions.append({
            "session_id": s.id,
            "student_id": s.student_id,
            "started_at": s.started_at,
            "ended_at": s.ended_at,
            "event_count": len(s.events),
            "signal_count": signal_count,
            "review_status": latest_note.status if latest_note else ("Evidence Available" if signal_count > 0 else "Observation"),
        })

    return {
        "struggling_concepts": struggling_concepts,
        "students": students,
        "recent_sessions": recent_sessions,
        "total_sessions": db.query(SessionModel).count(),
        "total_submissions": db.query(Submission).count(),
    }

@router.get("/session/{session_id}")
def get_session_review_data(session_id: int, db: Session = Depends(get_db)):
    """
    Detailed session data for reviewer:
    - Events with reconstructed code states
    - Integrity signals with direct event anchors
    - Submissions & code
    - Viva questions and student answers
    - Review notes
    """
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    events = (
        db.query(Event)
        .filter(Event.session_id == session_id)
        .order_by(Event.timestamp.asc(), Event.id.asc())
        .all()
    )

    signals = analyze_session(events)
    timeline = reconstruct_editor_state(events)

    submissions = (
        db.query(Submission)
        .filter(Submission.session_id == session_id)
        .order_by(Submission.id.desc())
        .all()
    )

    submissions_data = []
    for sub in submissions:
        viva_list = []
        for vq in sub.viva_questions:
            responses = [
                {
                    "response_text": r.response_text,
                    "score": r.score,
                    "feedback": r.feedback,
                    "evaluated_at": r.evaluated_at,
                }
                for r in vq.responses
            ]
            viva_list.append({
                "id": vq.id,
                "question_text": vq.question_text,
                "question_type": vq.question_type,
                "context": vq.context,
                "responses": responses,
            })

        submissions_data.append({
            "id": sub.id,
            "question_id": sub.question_id,
            "question_title": sub.question.title if sub.question else f"Question {sub.question_id}",
            "code": sub.code,
            "status": sub.status,
            "passed_tests": sub.passed_tests,
            "total_tests": sub.total_tests,
            "created_at": sub.created_at,
            "viva": viva_list,
        })

    notes = (
        db.query(ReviewNote)
        .filter(ReviewNote.session_id == session_id)
        .order_by(ReviewNote.id.desc())
        .all()
    )

    return {
        "session": {
            "id": session.id,
            "student_id": session.student_id,
            "started_at": session.started_at,
            "ended_at": session.ended_at,
        },
        "signals": signals,
        "timeline": timeline,
        "submissions": submissions_data,
        "notes": [
            {
                "id": n.id,
                "trainer_id": n.trainer_id,
                "status": n.status,
                "notes": n.notes,
                "created_at": n.created_at,
            }
            for n in notes
        ],
    }

@router.post("/review_notes", response_model=ReviewNoteOut, status_code=status.HTTP_201_CREATED)
def create_review_note(session_id: int, note_data: ReviewNoteCreate, db: Session = Depends(get_db)):
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    note = ReviewNote(
        session_id=session_id,
        trainer_id=note_data.trainer_id,
        status=note_data.status,
        notes=note_data.notes,
        created_at=now_iso,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note
