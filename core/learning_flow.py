
from core.bkt import update_mastery
from core.adaptive import recommend_next


def process_assessment_result(
    student_id,
    concept_id,
    mastery_map,
    assessment_result,
    questions,
):
    """Update mastery after an assessment and recommend the next question."""

    if "score_correct" not in assessment_result:
        raise ValueError("Assessment result is missing score_correct.")

    is_correct = assessment_result["score_correct"]

    if not isinstance(is_correct, bool):
        raise ValueError("score_correct must be True or False.")

    old_mastery = mastery_map.get(concept_id, 0.0)
    new_mastery = update_mastery(old_mastery, is_correct)

    updated_mastery = dict(mastery_map)
    updated_mastery[concept_id] = new_mastery

    recommendation = recommend_next(
        student_id,
        updated_mastery,
        questions,
    )

    return {
        "student_id": student_id,
        "concept_id": concept_id,
        "is_correct": is_correct,
        "old_mastery": old_mastery,
        "new_mastery": new_mastery,
        "updated_mastery": updated_mastery,
        "recommendation": recommendation,
    }
