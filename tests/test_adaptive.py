from core.adaptive import recommend_next


QUESTIONS = [
    {"question_id": "Q1", "concept_id": "C1", "prompt": "Variables question"},
    {"question_id": "Q2", "concept_id": "C2", "prompt": "Classes question"},
    {"question_id": "Q3", "concept_id": "C3", "prompt": "Encapsulation question"},
    {"question_id": "Q4", "concept_id": "C4", "prompt": "Inheritance question"},
    {"question_id": "Q5", "concept_id": "C5", "prompt": "Dependency injection question"},
]


def test_different_students_get_different_recommendations():
    student_a = {"C1": 0.95, "C2": 0.95, "C3": 0.95, "C4": 0.30, "C5": 0.10}
    student_b = {"C1": 0.95, "C2": 0.30, "C3": 0.10, "C4": 0.10, "C5": 0.10}

    result_a = recommend_next("A", student_a, QUESTIONS)
    result_b = recommend_next("B", student_b, QUESTIONS)

    assert result_a["concept_id"] == "C4"
    assert result_b["concept_id"] == "C2"
    assert result_a["question"]["question_id"] != result_b["question"]["question_id"]