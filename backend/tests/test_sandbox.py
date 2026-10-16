import pytest
from app.services.sandbox import execute_code_sandboxed

def test_sandbox_executes_correct_solution():
    code = """
def solution(nums):
    return sum(n for n in nums if n > 0)
"""
    tests = [
        {"input": [[1, -4, 7, 12]], "expected": 20},
        {"input": [[-1, -2]], "expected": 0}
    ]
    res = execute_code_sandboxed(code, tests)
    assert res["status"] == "passed"
    assert res["passed_tests"] == 2
    assert res["total_tests"] == 2

def test_sandbox_catches_wrong_solution():
    code = """
def solution(nums):
    return 999
"""
    tests = [
        {"input": [[1, 2]], "expected": 3}
    ]
    res = execute_code_sandboxed(code, tests)
    assert res["status"] == "failed"
    assert res["passed_tests"] == 0

def test_sandbox_handles_infinite_loop_timeout():
    code = """
def solution(nums):
    while True:
        pass
    return 0
"""
    tests = [{"input": [[1]], "expected": 1}]
    # Run with small timeout for quick test
    res = execute_code_sandboxed(code, tests, timeout_sec=0.8)
    assert res["status"] == "timeout"
    assert "timed out" in res["stderr"].lower()

def test_sandbox_handles_syntax_error():
    code = "def solution(:\n  return"
    tests = [{"input": [1], "expected": 1}]
    res = execute_code_sandboxed(code, tests)
    assert res["status"] in ("syntax_error", "error", "failed")
