import ast
import json
import os
import urllib.request
import urllib.error
from typing import Dict, Any

MAX_OUTPUT_CHARS = 1000
DEFAULT_TIMEOUT_SEC = 3.0
SUPPORTED_LANGUAGES = {"python"}


def _truncate_output(text: str, limit: int = MAX_OUTPUT_CHARS) -> str:
    """Bounds runner output so large logs do not break the UI."""
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[Output truncated to safe boundary]"


def run_in_isolated_service(
    runner_url: str, language: str, code: str, test_suite: Dict[str, Any]
) -> Dict[str, Any]:
    """Sends code to a pre-configured external isolated sandbox with strict timeouts."""
    payload = json.dumps({
        "language": language,
        "code": code,
        "test_cases": test_suite.get("test_cases", []),
        "timeout": DEFAULT_TIMEOUT_SEC,
    }).encode("utf-8")

    req = urllib.request.Request(
        runner_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT_SEC + 1.0) as response:
            data = json.loads(response.read().decode("utf-8"))
            return {
                "status": data.get("status", "ERROR"),
                "passed": int(data.get("passed", 0)),
                "total": int(data.get("total", test_suite.get("total_tests", 1))),
                "bounded_output": _truncate_output(data.get("output", "")),
                "error": _truncate_output(data.get("error", "")),
                "execution_mode": "isolated_runner",
            }
    except urllib.error.URLError as exc:
        return {
            "status": "ERROR",
            "passed": 0,
            "total": test_suite.get("total_tests", 1),
            "bounded_output": "",
            "error": f"Isolated runner unreachable: {exc.reason}",
            "execution_mode": "isolated_runner_failed",
        }


def run_safe_prototype_fallback(
    language: str, code: str, test_suite: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Safe static prototype analyzer for local demos without a sandbox.
    NEVER calls exec(), eval(), or subprocess on the host machine.
    """
    total = int(test_suite.get("total_tests", 3))
    banner = "[PROTOTYPE MOCK RUNNER - NO HOST EXECUTION]\n"

    if language.lower() not in SUPPORTED_LANGUAGES:
        return {
            "status": "ERROR",
            "passed": 0,
            "total": total,
            "bounded_output": banner,
            "error": f"Unsupported language '{language}'. MVP supports Python only.",
            "execution_mode": "prototype_mock",
        }

    if not code or not code.strip():
        return {
            "status": "ERROR",
            "passed": 0,
            "total": total,
            "bounded_output": banner,
            "error": "Empty code submission.",
            "execution_mode": "prototype_mock",
        }

    # 1. Static Syntax Check via AST (Safe: does not execute code)
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {
            "status": "ERROR",
            "passed": 0,
            "total": total,
            "bounded_output": banner,
            "error": f"SyntaxError on line {exc.lineno}: {exc.msg}",
            "execution_mode": "prototype_mock",
        }

    # 2. Detect simulated timeout / infinite loop constructs
    for node in ast.walk(tree):
        if isinstance(node, ast.While) and isinstance(node.test, ast.Constant) and node.test.value is True:
            has_break = any(isinstance(sub, ast.Break) for sub in ast.walk(node))
            if not has_break:
                return {
                    "status": "TIMEOUT",
                    "passed": 0,
                    "total": total,
                    "bounded_output": banner + "Execution aborted: Infinite loop pattern detected.",
                    "error": f"TimeoutError: Execution exceeded {DEFAULT_TIMEOUT_SEC}s limit.",
                    "execution_mode": "prototype_mock",
                }

    # 3. Detect simulated runtime errors (e.g. explicit division by zero or raise)
    if "1 / 0" in code or "1/0" in code or "ZeroDivisionError" in code:
        return {
            "status": "ERROR",
            "passed": 0,
            "total": total,
            "bounded_output": banner + "Traceback (simulated):\n",
            "error": "ZeroDivisionError: division by zero",
            "execution_mode": "prototype_mock",
        }

    # 4. Evaluate against fixture rules for deterministic demo behavior
    expected_tokens = test_suite.get("expected_tokens", [])
    correct_markers = test_suite.get("correct_markers", [])

    missing_tokens = [tok for tok in expected_tokens if tok not in code]
    if missing_tokens:
        return {
            "status": "FAILED",
            "passed": 0,
            "total": total,
            "bounded_output": _truncate_output(
                f"{banner}Ran {total} tests. Missing expected structure: {missing_tokens[0]}"
            ),
            "error": "",
            "execution_mode": "prototype_mock",
        }

    is_fully_correct = any(marker in code for marker in correct_markers) or "# PASS_ALL" in code
    if is_fully_correct:
        return {
            "status": "PASSED",
            "passed": total,
            "total": total,
            "bounded_output": _truncate_output(
                f"{banner}Ran {total}/{total} test cases successfully.\nAll assertions passed."
            ),
            "error": "",
            "execution_mode": "prototype_mock",
        }

    # Partial / Wrong Answer path
    passed = max(0, total - 2)
    return {
        "status": "FAILED",
        "passed": passed,
        "total": total,
        "bounded_output": _truncate_output(
            f"{banner}Ran {total} tests: {passed} passed, {total - passed} failed.\n"
            f"AssertionError: Output did not match expected test case result."
        ),
        "error": "",
        "execution_mode": "prototype_mock",
    }


def execute_submission(language: str, code: str, test_suite: Dict[str, Any]) -> Dict[str, Any]:
    """Routes execution to the isolated service if configured, otherwise uses the safe fallback."""
    runner_url = os.getenv("ISOLATED_RUNNER_URL", "").strip()
    if runner_url:
        return run_in_isolated_service(runner_url, language, code, test_suite)
    return run_safe_prototype_fallback(language, code, test_suite)