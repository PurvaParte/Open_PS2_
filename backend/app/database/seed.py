import json
from sqlalchemy.orm import Session
from app.models import Concept, Prerequisite, Question, Session as SessionModel, StudentMastery

def seed_initial_data(db: Session):
    """Seed foundational curriculum concepts, prerequisites, and questions."""
    # Check if concepts already exist
    if db.query(Concept).first() is not None:
        return

    concepts_data = [
        {
            "id": "python_basics",
            "name": "Python Basics & Variables",
            "description": "Variable assignments, primitive data types (int, float, str, bool), and fundamental operators.",
            "category": "Fundamentals",
            "learning_content": "### Python Basics\nVariables in Python are dynamically typed references. Fundamental data types include integers, floating-point numbers, booleans, and strings."
        },
        {
            "id": "control_flow",
            "name": "Control Flow & Branching",
            "description": "Conditional statements (if/elif/else), boolean logic, and looping constructs (for, while).",
            "category": "Control Flow",
            "learning_content": "### Control Flow\nBranching allows conditional execution based on boolean truth values. Loops iterate across sequences or while conditions hold true."
        },
        {
            "id": "functions_scope",
            "name": "Functions & Modular Scope",
            "description": "Function definitions, parameters, return values, variable scope (local vs global), and pure functions.",
            "category": "Functions",
            "learning_content": "### Functions\nFunctions isolate modular units of logic, accept arguments, and return evaluated results while encapsulating scope."
        },
        {
            "id": "data_structures",
            "name": "Collections & Data Structures",
            "description": "Lists, dictionaries (hash maps), tuples, sets, and comprehension patterns.",
            "category": "Data Structures",
            "learning_content": "### Data Structures\nDictionaries provide average O(1) key lookups via hashing. Lists provide ordered sequence indexing."
        },
        {
            "id": "oop_classes",
            "name": "OOP & Encapsulation",
            "description": "Classes, object instantiations, methods, encapsulation, and instance state.",
            "category": "OOP",
            "learning_content": "### Object-Oriented Programming\nClasses bind state (attributes) and behavior (methods) into cohesive objects."
        },
        {
            "id": "algo_complexity",
            "name": "Algorithm Analysis & Complexity",
            "description": "Big O time and space complexity, two pointers, searching, and optimization techniques.",
            "category": "Algorithms",
            "learning_content": "### Algorithm Complexity\nAnalyze time complexity (O(1), O(N), O(N^2)) to design efficient algorithms for large datasets."
        }
    ]

    for c in concepts_data:
        db.add(Concept(**c))
    db.commit()

    prereqs_data = [
        ("control_flow", "python_basics"),
        ("functions_scope", "control_flow"),
        ("data_structures", "functions_scope"),
        ("oop_classes", "data_structures"),
        ("algo_complexity", "data_structures"),
    ]

    for cid, pid in prereqs_data:
        db.add(Prerequisite(concept_id=cid, prerequisite_id=pid))
    db.commit()

    questions_data = [
        {
            "concept_id": "python_basics",
            "title": "Sum of Positive Numbers",
            "description": "Write a function `solution(nums)` that takes a list of integers and returns the sum of all strictly positive numbers (> 0). If there are no positive numbers or the list is empty, return 0.",
            "difficulty": "easy",
            "allowed_languages": "python",
            "starter_code": "def solution(nums):\n    # Return sum of all positive integers\n    return 0\n",
            "visible_tests": json.dumps([
                {"input": [[1, -4, 7, 12]], "expected": 20},
                {"input": [[-1, -2, -3]], "expected": 0}
            ]),
            "hidden_tests": json.dumps([
                {"input": [[]], "expected": 0},
                {"input": [[0, 5, -2, 10]], "expected": 15},
                {"input": [[100, 200, -300]], "expected": 300}
            ])
        },
        {
            "concept_id": "control_flow",
            "title": "Count Even and Odd Numbers",
            "description": "Write a function `solution(nums)` that takes a list of integers and returns a dictionary with keys `'even'` and `'odd'` containing their respective counts.",
            "difficulty": "easy",
            "allowed_languages": "python",
            "starter_code": "def solution(nums):\n    # Return {'even': count_even, 'odd': count_odd}\n    return {'even': 0, 'odd': 0}\n",
            "visible_tests": json.dumps([
                {"input": [[1, 2, 3, 4, 5]], "expected": {"even": 2, "odd": 3}}
            ]),
            "hidden_tests": json.dumps([
                {"input": [[]], "expected": {"even": 0, "odd": 0}},
                {"input": [[2, 4, 6]], "expected": {"even": 3, "odd": 0}},
                {"input": [[1, 3, 5, 7]], "expected": {"even": 0, "odd": 4}}
            ])
        },
        {
            "concept_id": "functions_scope",
            "title": "Valid Palindrome String",
            "description": "Write a function `solution(s)` that determines if a given string is a palindrome, considering only alphanumeric characters and ignoring casing.",
            "difficulty": "medium",
            "allowed_languages": "python",
            "starter_code": "def solution(s):\n    # Return True if s is a palindrome, else False\n    return False\n",
            "visible_tests": json.dumps([
                {"input": ["A man, a plan, a canal: Panama"], "expected": True},
                {"input": ["race a car"], "expected": False}
            ]),
            "hidden_tests": json.dumps([
                {"input": [""], "expected": True},
                {"input": ["ab_a"], "expected": True},
                {"input": ["0P"], "expected": False}
            ])
        },
        {
            "concept_id": "data_structures",
            "title": "Word Frequency Mapping",
            "description": "Write a function `solution(text)` that takes a string of words and returns a dictionary containing the frequency count of each word. Ignore case differences, and words are separated by whitespace.",
            "difficulty": "medium",
            "allowed_languages": "python",
            "starter_code": "def solution(text):\n    # Return dictionary of word frequencies\n    return {}\n",
            "visible_tests": json.dumps([
                {"input": ["apple banana apple"], "expected": {"apple": 2, "banana": 1}}
            ]),
            "hidden_tests": json.dumps([
                {"input": ["Hello hello HELLO"], "expected": {"hello": 3}},
                {"input": [""], "expected": {}},
                {"input": ["one two three two one"], "expected": {"one": 2, "two": 2, "three": 1}}
            ])
        },
        {
            "concept_id": "algo_complexity",
            "title": "Two Sum Target Indices",
            "description": "Write a function `solution(nums, target)` that returns the indices [i, j] of two numbers that add up to target. Use an efficient dictionary lookup for O(N) time complexity.",
            "difficulty": "medium",
            "allowed_languages": "python",
            "starter_code": "def solution(nums, target):\n    # Return list of indices [i, j]\n    return []\n",
            "visible_tests": json.dumps([
                {"input": [[2, 7, 11, 15], 9], "expected": [0, 1]}
            ]),
            "hidden_tests": json.dumps([
                {"input": [[3, 2, 4], 6], "expected": [1, 2]},
                {"input": [[3, 3], 6], "expected": [0, 1]}
            ])
        }
    ]

    for q in questions_data:
        db.add(Question(**q))
    db.commit()

    # Pre-seed demo student masteries
    demo_students = ["student-1", "student-alice", "student-bob"]
    for sid in demo_students:
        for c in concepts_data:
            mastery_val = 0.75 if c["id"] == "python_basics" else (0.45 if c["id"] == "control_flow" else 0.20)
            db.add(StudentMastery(
                student_id=sid,
                concept_id=c["id"],
                mastery=mastery_val,
                confidence=0.6,
                attempts_count=2 if mastery_val > 0.4 else 0,
                success_count=1 if mastery_val > 0.4 else 0,
            ))
    db.commit()
