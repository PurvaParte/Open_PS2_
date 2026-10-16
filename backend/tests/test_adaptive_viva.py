import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.database.seed import seed_initial_data
from app.adaptive.engine import (
    get_concept_graph,
    get_or_create_mastery,
    update_bkt_mastery,
    get_adaptive_recommendation,
)
from app.assessment.viva import generate_viva_questions_from_code, evaluate_viva_response

@pytest.fixture
def seeded_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    seed_initial_data(session)
    try:
        yield session
    finally:
        session.close()

def test_concept_graph(seeded_db):
    graph = get_concept_graph(seeded_db)
    assert len(graph["concepts"]) >= 5
    assert len(graph["edges"]) >= 4

def test_bkt_mastery_update(seeded_db):
    # Initial mastery
    m_init = get_or_create_mastery(seeded_db, "learner_1", "python_basics")
    init_val = m_init.mastery

    # Correct submission updates mastery upwards
    m_up = update_bkt_mastery(seeded_db, "learner_1", "python_basics", is_correct=True)
    assert m_up.mastery > init_val
    assert m_up.attempts_count == 1
    assert m_up.success_count == 1

    # Incorrect submission adjusts probability
    m_down = update_bkt_mastery(seeded_db, "learner_1", "python_basics", is_correct=False)
    assert m_down.attempts_count == 2
    assert m_down.success_count == 1

def test_adaptive_recommendation(seeded_db):
    rec = get_adaptive_recommendation(seeded_db, "new_student")
    assert rec is not None
    assert "recommended_concept" in rec
    assert "recommended_question" in rec
    assert "reason" in rec

def test_ast_viva_generation_dict_code():
    code_with_dict = """
def solution(nums):
    seen = {}
    for i, n in enumerate(nums):
        seen[n] = i
    return seen
"""
    viva = generate_viva_questions_from_code(code_with_dict)
    assert len(viva) >= 2
    types = [q["question_type"] for q in viva]
    assert "data_structure" in types

def test_ast_viva_generation_loop_and_if():
    code_with_if_loop = """
def solution(s):
    if not s:
        return True
    for ch in s:
        if ch == 'a':
            return False
    return True
"""
    viva = generate_viva_questions_from_code(code_with_if_loop)
    assert len(viva) >= 2
    types = [q["question_type"] for q in viva]
    assert "complexity" in types
    assert "edge_case" in types

def test_viva_response_evaluation():
    eval_res = evaluate_viva_response(
        question_text="Why use a dictionary?",
        question_type="data_structure",
        response_text="I chose a dictionary because it provides constant O(1) time complexity for hash key lookup operations instead of O(N) array scans."
    )
    assert eval_res["score"] >= 0.7
    assert "O(1)" in eval_res["feedback"] or "o(1)" in eval_res["feedback"].lower()
