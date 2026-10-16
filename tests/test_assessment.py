import unittest
from core.assessment import submit_code, evaluate_submission


class TestCodeAssessment(unittest.TestCase):

    def test_valid_solution_passes(self):
        """1. Test a valid passing solution."""
        code = (
            "def calculate_discount(price, discount):\n"
            "    return price * (1 - discount)\n"
        )
        status, summary, bounded_output, error = submit_code("python", code, "test_funcs_01")
        self.assertEqual(status, "PASSED")
        self.assertIn("3/3 tests passed", summary)
        self.assertEqual(error, "")
        self.assertTrue(len(bounded_output) > 0)

    def test_wrong_answer_fails_cleanly(self):
        """2. Test a wrong answer (valid syntax, fails unit tests)."""
        code = (
            "def calculate_discount(price, discount):\n"
            "    return price + discount\n"
        )
        status, summary, bounded_output, error = submit_code("python", code, "test_funcs_01")
        self.assertEqual(status, "FAILED")
        self.assertIn("FAILED", summary)
        self.assertIn("AssertionError", bounded_output)
        self.assertEqual(error, "")

    def test_syntax_error_handled(self):
        """3a. Test a syntax error submission."""
        code = "def calculate_discount(price, discount)\n    return price"
        status, summary, bounded_output, error = submit_code("python", code, "test_funcs_01")
        self.assertEqual(status, "ERROR")
        self.assertIn("0/3", summary)
        self.assertIn("SyntaxError", error)

    def test_runtime_error_handled(self):
        """3b. Test a runtime error submission."""
        code = (
            "def calculate_discount(price, discount):\n"
            "    x = 1 / 0\n"
            "    return x\n"
        )
        status, summary, bounded_output, error = submit_code("python", code, "test_funcs_01")
        self.assertEqual(status, "ERROR")
        self.assertIn("ZeroDivisionError", error)

    def test_infinite_loop_timeout_bounded(self):
        """4. Test timeout / infinite loop detection without hanging host."""
        code = (
            "def calculate_discount(price, discount):\n"
            "    while True:\n"
            "        pass\n"
            "    return price\n"
        )
        status, summary, bounded_output, error = submit_code("python", code, "test_funcs_01")
        self.assertEqual(status, "TIMEOUT")
        self.assertIn("TimeoutError", error)

    def test_integration_contract_fields(self):
        """5. Verify exact integration contract fields required by Member A and Member D."""
        code = (
            "def calculate_discount(price, discount):\n"
            "    return price * (1 - discount)\n"
        )
        result = evaluate_submission("python", code, "test_funcs_01", student_id="student_a")
        required_keys = {
            "submission_id",
            "language",
            "status",
            "passed",
            "total",
            "bounded_output",
            "error",
            "student_id",
            "code",
            "test_summary",
            "created_at",
        }
        self.assertTrue(required_keys.issubset(result.keys()))
        self.assertTrue(result["score_correct"])


if __name__ == "__main__":
    unittest.main()
