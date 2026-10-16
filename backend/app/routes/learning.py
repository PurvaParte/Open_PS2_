from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models import Concept, StudentMastery
from app.schemas import ConceptOut, StudentMasteryOut, AdaptiveRecommendationOut
from app.adaptive.engine import get_concept_graph, get_adaptive_recommendation

router = APIRouter(prefix="/api", tags=["Adaptive Learning"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/concepts")
def list_concepts(db: Session = Depends(get_db)):
    return get_concept_graph(db)

@router.get("/mastery/{student_id}", response_model=List[StudentMasteryOut])
def get_student_mastery(student_id: str, db: Session = Depends(get_db)):
    concepts = db.query(Concept).all()
    concept_map = {c.id: c.name for c in concepts}
    records = db.query(StudentMastery).filter(StudentMastery.student_id == student_id).all()

    # If student has no records yet, initialize defaults
    if not records:
        from app.adaptive.engine import get_or_create_mastery
        for c in concepts:
            get_or_create_mastery(db, student_id, c.id)
        records = db.query(StudentMastery).filter(StudentMastery.student_id == student_id).all()

    results = []
    for r in records:
        results.append(StudentMasteryOut(
            concept_id=r.concept_id,
            concept_name=concept_map.get(r.concept_id, r.concept_id),
            mastery=r.mastery,
            confidence=r.confidence,
            attempts_count=r.attempts_count,
            success_count=r.success_count,
            last_updated=r.last_updated
        ))
    return results

@router.get("/adaptive/recommendation/{student_id}", response_model=AdaptiveRecommendationOut)
def recommend_next_step(student_id: str, db: Session = Depends(get_db)):
    rec = get_adaptive_recommendation(db, student_id)
    if not rec:
        raise HTTPException(status_code=404, detail="No suitable adaptive recommendation available.")
    return rec
