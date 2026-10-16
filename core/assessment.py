import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple, Dict, Any

from services.runner_client import execute_submission

DEFAULT_TESTS_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_tests.json"


def load_test_fixtures(filepath: Path = DEFAULT_TESTS_PATH) -> Dict[str, Any]:
    """Loads sample test cases from JSON fixture file."""
    if not filepath.exists():
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def submit_code(
    language: str, code: str, test_ref: str
) -> Tuple[str, str, str, str]:
    """
    Primary Member B functional contract:
    submit_code(language, code, test_ref) -> status, summary, bounded_output, error
    """
    result = evaluate_submission(language=language, code=code, test_ref=test_ref)
    return (
        result["status"],
        result["test_summary"],
        result["bounded_output"],
        result["error"],
    )


def evaluate_submission(
    language: str,
    code: str,
    test_ref: str,
    student_id: str = "student_a",
    fixtures_path: Path = DEFAULT_TESTS_PATH,
) -> Dict[str, Any]:
    """
    Full integration contract combining the Assessment Result schema (B -> A and D)
    and the Submission data structure.
    """
    submission_id = f"sub_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()
    fixtures = load_test_fixtures(fixtures_path)

    if test_ref not in fixtures:
        return {
            "submission_id": submission_id,
            "student_id": student_id,
            "language": language,
            "code": code,
            "status": "ERROR",
            "passed": 0,
            "total": 0,
            "score_correct": False,
            "test_summary": "0/0 passed (Invalid test_ref)",
            "bounded_output": "",
            "error": f"Unknown test_ref: '{test_ref}'",
            "execution_mode": "none",
            "created_at": created_at,
        }

    test_suite = fixtures[test_ref]
    exec_result = execute_submission(language=language, code=code, test_suite=test_suite)

    status = exec_result["status"]
    passed = exec_result["passed"]
    total = exec_result["total"]
    test_summary = f"{passed}/{total} tests passed ({status})"

    return {
        "submission_id": submission_id,
        "student_id": student_id,
        "concept_id": test_suite.get("concept_id", ""),
        "language": language,
        "code": code,
        "status": status,
        "passed": passed,
        "total": total,
        "score_correct": status == "PASSED" and passed == total and total > 0,
        "test_summary": test_summary,
        "bounded_output": exec_result["bounded_output"],
        "error": exec_result["error"],
        "execution_mode": exec_result.get("execution_mode", "prototype_mock"),
        "created_at": created_at,
    }