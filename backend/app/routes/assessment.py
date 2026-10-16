import json
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models import Question, Submission, VivaQuestion, VivaResponse, Session as SessionModel
from app.schemas import (
    QuestionSummaryOut,
    QuestionDetailOut,
    CodeRunRequest,
    CodeRunResponse,
    SubmissionCreate,
    SubmissionOut,
    VivaAnswerRequest,
    VivaAnswerResponse,
    VivaQuestionOut,
)
from app.services.sandbox import execute_code_sandboxed
from app.adaptive.engine import update_bkt_mastery
from app.assessment.viva import generate_viva_questions_from_code, evaluate_viva_response

router = APIRouter(prefix="/api", tags=["Assessment & Sandbox Execution"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/questions", response_model=List[QuestionSummaryOut])
def list_questions(concept_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Question)
    if concept_id:
        query = query.filter(Question.concept_id == concept_id)
    return query.all()

@router.get("/questions/{question_id}", response_model=QuestionDetailOut)
def get_question_detail(question_id: int, db: Session = Depends(get_db)):
    q = db.get(Question, question_id)
    if not q:
        raise HTTPException(status_code=404, detail=f"Question {question_id} not found")

    visible_tests = []
    if q.visible_tests:
        try:
            visible_tests = json.loads(q.visible_tests)
        except Exception:
            visible_tests = []

    return QuestionDetailOut(
        id=q.id,
        concept_id=q.concept_id,
        concept_name=q.concept.name if q.concept else q.concept_id,
        title=q.title,
        description=q.description,
        difficulty=q.difficulty,
        allowed_languages=q.allowed_languages,
        starter_code=q.starter_code,
        visible_tests=visible_tests,
    )

@router.post("/code/run", response_model=CodeRunResponse)
def run_code(req: CodeRunRequest, db: Session = Depends(get_db)):
    """
    Run user code in isolated sandbox against visible/custom sample tests.
    Does not execute hidden tests and does not record a permanent submission.
    """
    test_cases = []
    if req.custom_tests:
        test_cases = [t.model_dump() for t in req.custom_tests]
    elif req.question_id:
        q = db.get(Question, req.question_id)
        if q and q.visible_tests:
            try:
                test_cases = json.loads(q.visible_tests)
            except Exception:
                test_cases = []

    if not test_cases:
        # Default probe test
        test_cases = [{"input": None, "expected": None}]

    res = execute_code_sandboxed(req.code, test_cases)
    return CodeRunResponse(
        status=res.get("status", "failed"),
        stdout=res.get("stdout", ""),
        stderr=res.get("stderr", ""),
        passed_tests=res.get("passed_tests", 0),
        total_tests=res.get("total_tests", len(test_cases)),
        test_results=res.get("test_results", []),
        execution_time_ms=res.get("execution_time_ms", 0.0),
    )

@router.post("/submissions", response_model=SubmissionOut, status_code=status.HTTP_201_CREATED)
def submit_solution(req: SubmissionCreate, db: Session = Depends(get_db)):
    """
    Final assessment submission:
    1. Validates session and question.
    2. Runs code against ALL tests (visible + hidden server-side tests).
    3. Persists submission record.
    4. Dynamically updates student concept mastery using BKT.
    5. Deterministically generates code viva comprehension questions based on AST.
    """
    session = db.get(SessionModel, req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {req.session_id} not found")

    q = db.get(Question, req.question_id)
    if not q:
        raise HTTPException(status_code=404, detail=f"Question {req.question_id} not found")

    # Load all test cases (visible + hidden)
    all_tests = []
    if q.visible_tests:
        try:
            all_tests.extend(json.loads(q.visible_tests))
        except Exception:
            pass
    if q.hidden_tests:
        try:
            all_tests.extend(json.loads(q.hidden_tests))
        except Exception:
            pass

    # Execute in sandbox
    exec_result = execute_code_sandboxed(req.code, all_tests)
    is_passed = (exec_result.get("status") == "passed") and (exec_result.get("passed_tests") == len(all_tests))
    sub_status = "passed" if is_passed else "failed"

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    submission = Submission(
        session_id=req.session_id,
        student_id=req.student_id,
        question_id=req.question_id,
        code=req.code,
        status=sub_status,
        passed_tests=exec_result.get("passed_tests", 0),
        total_tests=len(all_tests),
        execution_output=exec_result.get("stderr") or exec_result.get("stdout") or "",
        created_at=now_iso,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    # Update Bayesian Knowledge Tracing mastery
    update_bkt_mastery(db, req.student_id, q.concept_id, is_passed, now_iso)

    # Generate Viva comprehension questions based on student's actual code structure
    viva_q_data = generate_viva_questions_from_code(req.code)
    created_viva = []
    for vqd in viva_q_data:
        vq = VivaQuestion(
            submission_id=submission.id,
            question_text=vqd["question_text"],
            question_type=vqd["question_type"],
            context=vqd["context"],
        )
        db.add(vq)
        created_viva.append(vq)
    db.commit()

    for cv in created_viva:
        db.refresh(cv)

    return SubmissionOut(
        id=submission.id,
        session_id=submission.session_id,
        student_id=submission.student_id,
        question_id=submission.question_id,
        code=submission.code,
        status=submission.status,
        passed_tests=submission.passed_tests,
        total_tests=submission.total_tests,
        execution_output=submission.execution_output,
        created_at=submission.created_at,
        viva_questions=[
            VivaQuestionOut(
                id=v.id,
                submission_id=v.submission_id,
                question_text=v.question_text,
                question_type=v.question_type,
                context=v.context
            ) for v in created_viva
        ]
    )

@router.get("/submissions/{submission_id}", response_model=SubmissionOut)
def get_submission(submission_id: int, db: Session = Depends(get_db)):
    sub = db.get(Submission, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")
    return sub

@router.post("/viva/answer", response_model=VivaAnswerResponse)
def answer_viva(req: VivaAnswerRequest, db: Session = Depends(get_db)):
    vq = db.get(VivaQuestion, req.viva_question_id)
    if not vq:
        raise HTTPException(status_code=404, detail=f"Viva question {req.viva_question_id} not found")

    eval_result = evaluate_viva_response(vq.question_text, vq.question_type, req.response_text)
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    resp = VivaResponse(
        viva_question_id=req.viva_question_id,
        response_text=req.response_text,
        score=eval_result["score"],
        feedback=eval_result["feedback"],
        evaluated_at=now_iso,
    )
    db.add(resp)
    db.commit()
    db.refresh(resp)

    return VivaAnswerResponse(
        viva_question_id=vq.id,
        score=resp.score,
        feedback=resp.feedback,
        evaluated_at=resp.evaluated_at,
    )
