import math
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Concept, Prerequisite, StudentMastery, Question, Submission

# Standard BKT Model Parameters
BKT_PRIOR_L0 = 0.20
BKT_TRANSIT_T = 0.15
BKT_GUESS_G = 0.10
BKT_SLIP_S = 0.10
MASTERY_THRESHOLD = 0.65

def get_concept_graph(db: Session) -> Dict[str, Any]:
    """Retrieve all concepts and prerequisite relationships as a directed graph."""
    concepts = db.query(Concept).all()
    prereqs = db.query(Prerequisite).all()

    prereq_map: Dict[str, List[str]] = {c.id: [] for c in concepts}
    for p in prereqs:
        if p.concept_id in prereq_map:
            prereq_map[p.concept_id].append(p.prerequisite_id)

    nodes = []
    for c in concepts:
        nodes.append({
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "category": c.category,
            "learning_content": c.learning_content or "",
            "prerequisites": prereq_map.get(c.id, []),
        })

    edges = [{"from": p.prerequisite_id, "to": p.concept_id} for p in prereqs]
    return {"concepts": nodes, "edges": edges}

def get_or_create_mastery(db: Session, student_id: str, concept_id: str) -> StudentMastery:
    """Retrieve existing mastery record or initialize with BKT prior."""
    mastery_record = (
        db.query(StudentMastery)
        .filter(StudentMastery.student_id == student_id, StudentMastery.concept_id == concept_id)
        .first()
    )
    if not mastery_record:
        mastery_record = StudentMastery(
            student_id=student_id,
            concept_id=concept_id,
            mastery=BKT_PRIOR_L0,
            confidence=0.3,
            attempts_count=0,
            success_count=0,
        )
        db.add(mastery_record)
        db.commit()
        db.refresh(mastery_record)
    return mastery_record

def update_bkt_mastery(
    db: Session,
    student_id: str,
    concept_id: str,
    is_correct: bool,
    timestamp_str: Optional[str] = None
) -> StudentMastery:
    """
    Update student concept mastery using standard Bayesian Knowledge Tracing formulas.
    """
    rec = get_or_create_mastery(db, student_id, concept_id)
    p_l = rec.mastery

    if is_correct:
        # P(L | correct) = [P(L) * (1 - S)] / [P(L) * (1 - S) + (1 - P(L)) * G]
        numerator = p_l * (1.0 - BKT_SLIP_S)
        denominator = numerator + (1.0 - p_l) * BKT_GUESS_G
        p_l_given_obs = numerator / max(denominator, 1e-6)
        rec.success_count += 1
    else:
        # P(L | incorrect) = [P(L) * S] / [P(L) * S + (1 - P(L)) * (1 - G)]
        numerator = p_l * BKT_SLIP_S
        denominator = numerator + (1.0 - p_l) * (1.0 - BKT_GUESS_G)
        p_l_given_obs = numerator / max(denominator, 1e-6)

    # State transition: P(L_next) = P(L | obs) + (1 - P(L | obs)) * T
    p_l_next = p_l_given_obs + (1.0 - p_l_given_obs) * BKT_TRANSIT_T
    rec.mastery = round(min(max(p_l_next, 0.05), 0.99), 3)

    rec.attempts_count += 1
    # Confidence increases asymptotically with number of trials
    rec.confidence = round(1.0 - (0.7 * math.exp(-0.4 * rec.attempts_count)), 3)
    if timestamp_str:
        rec.last_updated = timestamp_str

    db.commit()
    db.refresh(rec)
    return rec

def get_adaptive_recommendation(db: Session, student_id: str) -> Optional[Dict[str, Any]]:
    """
    Select the optimal next question and concept for the student:
    1. Check prerequisite fulfillment based on mastery.
    2. Prioritize weak / developing concepts among unlocked ones.
    3. Choose unattempted or failed question targeting the concept.
    """
    graph = get_concept_graph(db)
    concepts = graph["concepts"]
    if not concepts:
        return None

    # Load all masteries for student
    masteries = {
        m.concept_id: m.mastery
        for m in db.query(StudentMastery).filter(StudentMastery.student_id == student_id).all()
    }

    # Identify unlocked concepts
    unlocked = []
    for c in concepts:
        c_id = c["id"]
        prereqs = c["prerequisites"]
        prereqs_met = True
        for p in prereqs:
            p_mastery = masteries.get(p, BKT_PRIOR_L0)
            if p_mastery < MASTERY_THRESHOLD:
                prereqs_met = False
                break
        if prereqs_met:
            current_m = masteries.get(c_id, BKT_PRIOR_L0)
            unlocked.append((c, current_m))

    if not unlocked:
        # Fallback to root concepts
        root = concepts[0]
        unlocked = [(root, masteries.get(root["id"], BKT_PRIOR_L0))]

    # Sort by lowest mastery first
    unlocked.sort(key=lambda x: x[1])
    target_concept, target_mastery = unlocked[0]

    # Find candidate questions for target concept
    candidate_questions = (
        db.query(Question)
        .filter(Question.concept_id == target_concept["id"])
        .all()
    )

    if not candidate_questions:
        # Fallback to any available question
        candidate_questions = db.query(Question).all()

    if not candidate_questions:
        return None

    # Prioritize question not yet passed
    completed_qids = {
        s.question_id
        for s in db.query(Submission)
        .filter(Submission.student_id == student_id, Submission.status == "passed")
        .all()
    }

    selected_q = None
    for q in candidate_questions:
        if q.id not in completed_qids:
            selected_q = q
            break

    if not selected_q:
        selected_q = candidate_questions[0]

    reason = (
        f"Targeting concept '{target_concept['name']}' (Mastery: {int(target_mastery * 100)}%). "
        f"All prerequisites satisfied. Practice recommended to strengthen mastery."
    )

    import json
    visible_tests = []
    if selected_q.visible_tests:
        try:
            visible_tests = json.loads(selected_q.visible_tests)
        except Exception:
            visible_tests = []

    return {
        "recommended_concept": {
            "id": target_concept["id"],
            "name": target_concept["name"],
            "description": target_concept["description"],
            "category": target_concept["category"],
            "learning_content": target_concept["learning_content"],
            "prerequisites": target_concept["prerequisites"],
        },
        "recommended_question": {
            "id": selected_q.id,
            "concept_id": selected_q.concept_id,
            "concept_name": target_concept["name"],
            "title": selected_q.title,
            "description": selected_q.description,
            "difficulty": selected_q.difficulty,
            "allowed_languages": selected_q.allowed_languages,
            "starter_code": selected_q.starter_code,
            "visible_tests": visible_tests,
        },
        "reason": reason,
        "prerequisites_met": True,
        "current_mastery": target_mastery,
    }
