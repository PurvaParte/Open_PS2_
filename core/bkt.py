"""
Bayesian Knowledge Tracing (BKT).

Estimates a student's mastery probability after an answer.
"""


def update_mastery(
    p_mastery,
    is_correct,
    p_learn=0.10,
    p_guess=0.20,
    p_slip=0.10,
):
    """
    Update mastery probability after one assessment response.

    p_mastery: Current probability that the concept is mastered.
    is_correct: True if the answer is correct, otherwise False.
    p_learn: Probability of learning after this opportunity.
    p_guess: Probability of guessing correctly without mastery.
    p_slip: Probability of answering incorrectly despite mastery.

    Returns:
        Updated mastery probability between 0 and 1.
    """

    if not 0 <= p_mastery <= 1:
        raise ValueError("p_mastery must be between 0 and 1.")

    for name, value in [
        ("p_learn", p_learn),
        ("p_guess", p_guess),
        ("p_slip", p_slip),
    ]:
        if not 0 <= value <= 1:
            raise ValueError(f"{name} must be between 0 and 1.")

    if p_mastery == 0 and not is_correct:
        return p_learn

    if p_mastery == 1 and is_correct:
        return 1.0

    if is_correct:
        numerator = p_mastery * (1 - p_slip)
        denominator = numerator + (1 - p_mastery) * p_guess
    else:
        numerator = p_mastery * p_slip
        denominator = (
            numerator + (1 - p_mastery) * (1 - p_guess)
        )

    if denominator == 0:
        return p_mastery

    posterior = numerator / denominator

    # Account for learning after the assessment opportunity.
    updated_mastery = (
        posterior + (1 - posterior) * p_learn
    )

    return updated_mastery