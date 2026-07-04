"""Sigma-1 — answer checker unit tests. The checker must (a) confirm
correct answers, (b) CATCH wrong answers, (c) fail closed on everything
else. (b) is the product: a tutor that flags its own wrong answers.

    python3 -m research.S1_tutor_lane.test_checker
"""

from __future__ import annotations

import unittest

from app.answer_checker import check_answer, safe_eval


class TestSafeEval(unittest.TestCase):
    def test_basics(self):
        self.assertAlmostEqual(safe_eval("2x^2+7x+3", x=-3), 0.0)
        self.assertAlmostEqual(safe_eval("x^2 sin x", x=1.0),
                               __import__("math").sin(1.0))
        self.assertAlmostEqual(safe_eval("(x+1)(x-1)", x=3), 8.0)
        self.assertAlmostEqual(safe_eval("sqrt(16) + 2*3"), 10.0)

    def test_rejects_dangerous(self):
        from app.answer_checker import CheckError
        for evil in ("__import__('os')", "().__class__", "open('x')", "a[0]"):
            with self.assertRaises(CheckError):
                safe_eval(evil)


class TestQuadratic(unittest.TestCase):
    Q = "Solve 2x^2 + 7x + 3 = 0."

    def test_correct_roots_pass(self):
        r = check_answer(self.Q, "steps...\nFINAL ANSWER: x = -1/2, x = -3")
        self.assertEqual(r["label"], "Derived")
        self.assertTrue(r["passed"])

    def test_wrong_root_caught(self):
        r = check_answer(self.Q, "steps...\nFINAL ANSWER: x = 1, x = -3")
        self.assertEqual(r["label"], "Heuristic")
        self.assertIs(r["passed"], False)   # check RAN and failed - loud


class TestSimultaneous(unittest.TestCase):
    Q = "Solve the simultaneous equations 2x + 3y = 12 and x - y = 1."

    def test_correct(self):
        r = check_answer(self.Q, "FINAL ANSWER: x = 3, y = 2")
        self.assertEqual(r["label"], "Derived")

    def test_wrong_caught(self):
        r = check_answer(self.Q, "FINAL ANSWER: x = 2, y = 3")
        self.assertIs(r["passed"], False)


class TestDerivative(unittest.TestCase):
    Q = "Differentiate x^2 sin(x) with respect to x."

    def test_correct(self):
        r = check_answer(self.Q, "FINAL ANSWER: 2x sin(x) + x^2 cos(x)")
        self.assertEqual(r["label"], "Derived")

    def test_wrong_caught(self):
        r = check_answer(self.Q, "FINAL ANSWER: 2x cos(x)")
        self.assertIs(r["passed"], False)


class TestArithmetic(unittest.TestCase):
    def test_correct(self):
        r = check_answer("Evaluate 17 * 24 + 19.", "FINAL ANSWER: 427")
        self.assertEqual(r["label"], "Derived")

    def test_wrong_caught(self):
        r = check_answer("Evaluate 17 * 24 + 19.", "FINAL ANSWER: 421")
        self.assertIs(r["passed"], False)


class TestLatexAnswers(unittest.TestCase):
    """Exact output format captured from a live local model run
    (2026-07-04) - math models answer in LaTeX and put the answer on the
    lines AFTER the marker."""

    LIVE_TAIL = ("2. \\( x = \\frac{-7 - 5}{4} = \\frac{-12}{4} = -3 \\)\n\n"
                 "**Final Answer:**\n\n\\[\nx = -\\frac{1}{2}, \\quad x = -3\n\\]")

    def test_latex_multiline_final_answer(self):
        r = check_answer("Solve 2x^2 + 7x + 3 = 0.", self.LIVE_TAIL)
        self.assertEqual(r["label"], "Derived", r)
        self.assertTrue(r["passed"])

    def test_latex_wrong_answer_still_caught(self):
        wrong = self.LIVE_TAIL.replace("-\\frac{1}{2}", "\\frac{1}{2}")
        r = check_answer("Solve 2x^2 + 7x + 3 = 0.", wrong)
        self.assertIs(r["passed"], False, r)


class TestFailClosed(unittest.TestCase):
    def test_explanation_question_is_heuristic(self):
        r = check_answer("Explain why completing the square works.",
                         "Because a quadratic can be rewritten...\n"
                         "FINAL ANSWER: see explanation")
        self.assertEqual(r["label"], "Heuristic")
        self.assertFalse(r["checked"])

    def test_no_final_answer_line(self):
        r = check_answer("Solve x^2 - 4 = 0.", "The roots are two and minus two.")
        self.assertEqual(r["label"], "Heuristic")
        self.assertIn("no machine-readable", r["note"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
