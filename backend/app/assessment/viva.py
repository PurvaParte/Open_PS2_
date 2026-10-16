import ast
from typing import List, Dict, Any, Tuple

def generate_viva_questions_from_code(code: str) -> List[Dict[str, str]]:
    """
    Deterministically analyze student Python source code via AST and generate
    2-3 targeted viva questions testing conceptual and structural comprehension.
    """
    questions: List[Dict[str, str]] = []

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return [
            {
                "question_text": "Your submitted code had a syntax error during parsing. How would you debug syntax errors before executing your solution?",
                "question_type": "debugging",
                "context": "Syntax structure"
            },
            {
                "question_text": "What steps do you take to verify expected function arguments and return types?",
                "question_type": "verification",
                "context": "Input validation"
            }
        ]

    has_for_loop = False
    has_while_loop = False
    has_dict = False
    has_if = False
    has_recursion = False
    for_lineno = None
    if_lineno = None
    func_names = set()

    # Scan top-level and inner nodes
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_names.add(node.name)
        elif isinstance(node, ast.For):
            has_for_loop = True
            if for_lineno is None:
                for_lineno = getattr(node, "lineno", 1)
        elif isinstance(node, ast.While):
            has_while_loop = True
            if for_lineno is None:
                for_lineno = getattr(node, "lineno", 1)
        elif isinstance(node, (ast.Dict, ast.DictComp)):
            has_dict = True
        elif isinstance(node, ast.If):
            has_if = True
            if if_lineno is None:
                if_lineno = getattr(node, "lineno", 1)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in func_names:
                has_recursion = True

    # 1. Data structure or complexity question
    if has_dict:
        questions.append({
            "question_text": "Your solution utilizes a dictionary / hash map. Why did you choose this data structure over an ordered list, and what is the expected time complexity for key lookups?",
            "question_type": "data_structure",
            "context": "Dictionary selection & lookup complexity"
        })
    elif has_for_loop or has_while_loop:
        line_ref = f" around line {for_lineno}" if for_lineno else ""
        questions.append({
            "question_text": f"Your solution contains an iteration loop{line_ref}. What is the time complexity of this loop relative to input size N, and what would happen if inputs were already sorted?",
            "question_type": "complexity",
            "context": f"Iteration complexity{line_ref}"
        })

    # 2. Edge case and condition question
    if has_if:
        line_ref = f" on line {if_lineno}" if if_lineno else ""
        questions.append({
            "question_text": f"Examine the conditional branch{line_ref}. What specific edge case or boundary condition is this logic guarding against, and what would occur if the input were empty or null?",
            "question_type": "edge_case",
            "context": f"Branch logic{line_ref}"
        })
    else:
        questions.append({
            "question_text": "How does your implementation handle edge cases such as an empty collection or boundary input values?",
            "question_type": "edge_case",
            "context": "Boundary handling"
        })

    # 3. Alternative approach or algorithmic trade-off question
    if has_recursion:
        questions.append({
            "question_text": "You implemented recursion. What guarantees the termination of the recursive call stack, and what are the space complexity implications compared to an iterative solution?",
            "question_type": "recursion",
            "context": "Recursive base case & call stack"
        })
    else:
        questions.append({
            "question_text": "If the input size scaled to 1,000,000 elements, where would the primary memory or processing bottleneck occur in this implementation?",
            "question_type": "scalability",
            "context": "Algorithmic scalability"
        })

    return questions[:3]

def evaluate_viva_response(question_text: str, question_type: str, response_text: str) -> Dict[str, Any]:
    """
    Evaluate student's explanation objectively against conceptual criteria.
    Provides transparent scoring and constructive feedback.
    """
    clean_resp = response_text.strip().lower()
    words = clean_resp.split()
    word_count = len(words)

    if word_count < 4:
        return {
            "score": 0.2,
            "feedback": "The explanation is very brief. Elaborate on the mechanics and reason behind your code structure to demonstrate full conceptual understanding."
        }

    # Rubric keywords based on question type
    keywords_by_type = {
        "data_structure": ["o(1)", "constant", "hash", "key", "lookup", "fast", "search", "dictionary", "map"],
        "complexity": ["o(n)", "linear", "quadratic", "nested", "time", "complexity", "iterations", "loop", "scale"],
        "edge_case": ["empty", "null", "none", "zero", "boundary", "condition", "guard", "error", "handle"],
        "recursion": ["base case", "stack", "call", "overflow", "terminate", "iterative", "memory", "frame"],
        "scalability": ["memory", "bottleneck", "ram", "space", "chunk", "linear", "stream", "big o"]
    }

    target_keywords = keywords_by_type.get(question_type, ["code", "function", "input", "output", "test"])
    matched = [kw for kw in target_keywords if kw in clean_resp]
    match_ratio = len(matched) / max(len(target_keywords) * 0.4, 1.0)

    # Score calculation
    base_score = 0.5 if word_count >= 10 else 0.35
    bonus = min(match_ratio * 0.5, 0.5)
    final_score = round(min(base_score + bonus, 1.0), 2)

    feedback_parts = []
    if final_score >= 0.8:
        feedback_parts.append("Excellent explanation. You clearly articulated the design rationale and underlying computational principles.")
    elif final_score >= 0.5:
        feedback_parts.append("Good response covering the basic logic.")
    else:
        feedback_parts.append("Adequate start, but you could provide deeper detail regarding computational constraints or data structure properties.")

    if matched:
        feedback_parts.append(f"Demonstrated awareness of: {', '.join(matched[:3])}.")

    return {
        "score": final_score,
        "feedback": " ".join(feedback_parts)
    }
