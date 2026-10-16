import sys
import os
import json
import time
import tempfile
import subprocess
from typing import List, Dict, Any, Tuple
from app.core.config import settings

TEST_HARNESS_TEMPLATE = """# -*- coding: utf-8 -*-
import sys
import json
import time
import traceback

# Student code execution sandbox wrapper
results = []
stdout_capture = []

def run_tests():
    # Load user code
    user_globals = {}
    try:
        with open("solution.py", "r", encoding="utf-8") as f:
            code = f.read()
        compiled = compile(code, "solution.py", "exec")
        exec(compiled, user_globals)
    except Exception as e:
        print(json.dumps({
            "status": "syntax_error",
            "error": traceback.format_exc(),
            "results": []
        }))
        return

    with open("tests.json", "r", encoding="utf-8") as f:
        tests = json.load(f)

    for idx, t in enumerate(tests):
        inp = t.get("input")
        expected = t.get("expected")
        t_start = time.perf_counter()
        passed = False
        actual = None
        err_msg = None

        try:
            # Check if user defined a target function
            target_fn = None
            for key in ["solution", "solve", "solve_problem", "main", "process"]:
                if key in user_globals and callable(user_globals[key]):
                    target_fn = user_globals[key]
                    break
            if target_fn is None:
                # Find any user-defined function
                for k, v in user_globals.items():
                    if callable(v) and not k.startswith("__"):
                        target_fn = v
                        break

            if target_fn is not None:
                if isinstance(inp, list):
                    actual = target_fn(*inp)
                elif isinstance(inp, dict):
                    actual = target_fn(**inp)
                elif inp is None:
                    actual = target_fn()
                else:
                    actual = target_fn(inp)
                passed = (actual == expected)
            else:
                err_msg = "No callable function found in solution. Please define a function (e.g. solution)."
                passed = False
        except Exception as e:
            err_msg = traceback.format_exc()
            passed = False

        t_elapsed = round((time.perf_counter() - t_start) * 1000, 2)
        results.append({
            "test_num": idx + 1,
            "input": inp,
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "error": err_msg,
            "execution_time_ms": t_elapsed
        })

    all_passed = len(results) > 0 and all(r["passed"] for r in results)
    print(json.dumps({
        "status": "passed" if all_passed else "failed",
        "results": results
    }))

if __name__ == "__main__":
    run_tests()
"""

def execute_code_sandboxed(
    code: str,
    test_cases: List[Dict[str, Any]],
    timeout_sec: float = None
) -> Dict[str, Any]:
    """
    Executes student code against test cases in an isolated temporary subprocess sandbox.
    Enforces timeout, output size limit, and clean environment.
    """
    if timeout_sec is None:
        timeout_sec = settings.SANDBOX_TIMEOUT_SECONDS

    start_time = time.perf_counter()

    with tempfile.TemporaryDirectory() as temp_dir:
        solution_path = os.path.join(temp_dir, "solution.py")
        tests_path = os.path.join(temp_dir, "tests.json")
        harness_path = os.path.join(temp_dir, "harness.py")

        with open(solution_path, "w", encoding="utf-8") as f:
            f.write(code)

        with open(tests_path, "w", encoding="utf-8") as f:
            json.dump(test_cases, f)

        with open(harness_path, "w", encoding="utf-8") as f:
            f.write(TEST_HARNESS_TEMPLATE)

        # Isolated minimal environment (no secrets or parent DB credentials)
        safe_env = {
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
            "PATH": os.environ.get("PATH", ""),
            "PYTHONIOENCODING": "utf-8",
        }

        try:
            proc = subprocess.run(
                [sys.executable, "harness.py"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                env=safe_env
            )
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            stdout = proc.stdout[:settings.SANDBOX_MAX_OUTPUT_CHARS]
            stderr = proc.stderr[:settings.SANDBOX_MAX_OUTPUT_CHARS]

            # Parse harness JSON output
            try:
                # Harness prints JSON on last line of stdout
                lines = [l for l in stdout.strip().splitlines() if l.strip()]
                last_line = lines[-1] if lines else "{}"
                harness_data = json.loads(last_line)
                test_results = harness_data.get("results", [])
                status = harness_data.get("status", "failed")
                error = harness_data.get("error")
                if error:
                    stderr = error

                passed_count = sum(1 for r in test_results if r.get("passed"))
                return {
                    "status": status,
                    "stdout": "\n".join(lines[:-1]) if len(lines) > 1 else "",
                    "stderr": stderr,
                    "passed_tests": passed_count,
                    "total_tests": len(test_cases),
                    "test_results": test_results,
                    "execution_time_ms": elapsed_ms,
                }
            except Exception:
                return {
                    "status": "error" if proc.returncode != 0 else "failed",
                    "stdout": stdout,
                    "stderr": stderr or "Failed to parse test execution output.",
                    "passed_tests": 0,
                    "total_tests": len(test_cases),
                    "test_results": [],
                    "execution_time_ms": elapsed_ms,
                }

        except subprocess.TimeoutExpired:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "status": "timeout",
                "stdout": "",
                "stderr": f"Execution timed out after {timeout_sec} seconds. Check for infinite loops or heavy recursion.",
                "passed_tests": 0,
                "total_tests": len(test_cases),
                "test_results": [],
                "execution_time_ms": elapsed_ms,
            }
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "status": "error",
                "stdout": "",
                "stderr": f"Sandbox execution error: {str(e)}",
                "passed_tests": 0,
                "total_tests": len(test_cases),
                "test_results": [],
                "execution_time_ms": elapsed_ms,
            }
