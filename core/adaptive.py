"""
Adaptive question selection for the learning platform.
"""

from core.concepts import CONCEPTS


def recommend_next(student_id, mastery_map, questions, threshold=0.70):
    """
    Recommend a question targeting the weakest eligible concept.

    mastery_map:
        Dictionary mapping concept IDs to mastery probabilities.

    questions:
        List of dictionaries containing question_id and concept_id.
    """

    eligible_concepts = []

    for concept_id, concept in CONCEPTS.items():
        prerequisites = concept["prerequisites"]

        # A concept is eligible only when its prerequisites
        # meet the mastery threshold.
        prerequisites_mastered = all(
            mastery_map.get(prerequisite, 0.0) >= threshold
            for prerequisite in prerequisites
        )

        if prerequisites_mastered:
            mastery = mastery_map.get(concept_id, 0.0)

            eligible_concepts.append((concept_id, mastery))

    if not eligible_concepts:
        return {
            "student_id": student_id,
            "question": None,
            "reason": "No concept is currently eligible.",
        }

    # Choose the eligible concept with the lowest mastery.
    concept_id, mastery = min(
        eligible_concepts,
        key=lambda item: item[1],
    )

    # Find a question belonging to the selected concept.
    matching_questions = [
        question
        for question in questions
        if question["concept_id"] == concept_id
    ]

    if not matching_questions:
        return {
            "student_id": student_id,
            "question": None,
            "reason": f"No questions are available for {concept_id}.",
        }

    selected_question = matching_questions[0]

    return {
        "student_id": student_id,
        "concept_id": concept_id,
        "mastery": mastery,
        "question": selected_question,
        "reason": (
            f"{CONCEPTS[concept_id]['name']} is the weakest "
            f"eligible concept, with mastery {mastery:.0%}."
        ),
    }