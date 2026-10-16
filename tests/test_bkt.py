from core.bkt import update_mastery


def test_correct_answer_increases_mastery():
    result = update_mastery(0.3, True)
    assert result > 0.3


def test_incorrect_answer_decreases_mastery():
    result = update_mastery(0.3, False)
    assert result < 0.3


def test_mastery_stays_between_zero_and_one():
    result = update_mastery(0.5, True)
    assert 0 <= result <= 1