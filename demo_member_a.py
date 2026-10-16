
import json
from pathlib import Path

from core.adaptive import recommend_next
from core.bkt import update_mastery

BASE_DIR = Path(__file__).parent


def load_json(filename):
    path = BASE_DIR / "data" / filename
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main():
    questions = load_json("demo_questions.json")
    students = load_json("demo_students.json")

    for student_id, mastery in students.items():
        result = recommend_next(student_id, mastery, questions)

        print(f"\nStudent: {student_id}")
        print(f"Recommended concept: {result.get('concept_id')}")
        print(f"Question: {result['question']}")
        print(f"Reason: {result['reason']}")

    old_mastery = 0.30
    new_mastery = update_mastery(old_mastery, True)

    print("\nBKT demonstration")
    print(f"Before correct answer: {old_mastery:.3f}")
    print(f"After correct answer:  {new_mastery:.3f}")


if __name__ == "__main__":
    main()
