
from core.learning_flow import process_assessment_result


QUESTIONS = [
    {"question_id": "Q1", "concept_id": "C1", "prompt": "Variables question"},
    {"question_id": "Q2", "concept_id": "C2", "prompt": "Classes question"},
    {"question_id": "Q3", "concept_id": "C3", "prompt": "Encapsulation question"},
    {"question_id": "Q4", "concept_id": "C4", "prompt": "Inheritance question"},
    {"question_id": "Q5", "concept_id": "C5", "prompt": "Dependency injection question"},
]


def test_correct_assessment_updates_mastery_and_recommends_next():
    mastery = {"C1": 0.30, "C2": 0.0, "C3": 0.0, "C4": 0.0, "C5": 0.0}
    assessment_result = {"score_correct": True}

    result = process_assessment_result(
        student_id="Student_A",
        concept_id="C1",
        mastery_map=mastery,
        assessment_result=assessment_result,
        questions=QUESTIONS,
    )

    assert result["new_mastery"] > result["old_mastery"]
    assert result["updated_mastery"]["C1"] == result["new_mastery"]
    assert result["recommendation"]["question"] is not None


def test_incorrect_assessment_updates_mastery():
    mastery = {"C1": 0.30, "C2": 0.0, "C3": 0.0, "C4": 0.0, "C5": 0.0}
    assessment_result = {"score_correct": False}

    result = process_assessment_result(
        student_id="Student_B",
        concept_id="C1",
        mastery_map=mastery,
        assessment_result=assessment_result,
        questions=QUESTIONS,
    )

    assert result["new_mastery"] < result["old_mastery"]


def test_missing_correctness_result_is_rejected():
    try:
        process_assessment_result(
            student_id="Student_A",
            concept_id="C1",
            mastery_map={"C1": 0.30},
            assessment_result={},
            questions=QUESTIONS,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Missing score_correct should raise ValueError.")
