"""D5 — submission-compliance regression tests: the shipped ADTC test
prompts must parse, solve, certify, and independently verify in the
certified pipeline, and benchmark-format parsing must be unchanged.

    python3 -m research.D5_prompt_compat.test_prompt_compat
"""

from __future__ import annotations

import unittest

from kernel.state import ExecutionState

LAGOS = ("A furniture workshop in Lagos makes two products: chairs and "
         "tables. Each chair needs 3 hours of carpentry and 2 hours of "
         "finishing; each table needs 5 hours of carpentry and 3 hours of "
         "finishing. The workshop has 240 carpentry hours and 150 finishing "
         "hours available this month. Each chair earns N4,500 profit and "
         "each table N7,000. How many chairs and tables should the workshop "
         "make to maximize profit, and what is the maximum profit? Show "
         "your reasoning and verify that your plan stays within both labour "
         "limits.")

NAIROBI = ("A community health programme in Nairobi must assign four "
           "volunteers - Amina, Baraka, Chausiku, and David - to four "
           "clinics: Kibera, Kasarani, Embakasi, and Westlands, with "
           "exactly one volunteer per clinic. Amina cannot be assigned to "
           "Kibera. Baraka must be assigned to either Kasarani or "
           "Embakasi. If Chausiku is assigned to Kasarani, then David must "
           "be assigned to Westlands. David cannot be assigned to "
           "Embakasi. Find a valid assignment of volunteers to clinics, or "
           "explain clearly why none exists, and check your answer against "
           "every constraint.")


class TestShippedPromptsCertify(unittest.TestCase):

    def test_lagos_lp_full_pipeline(self):
        from kernel.lp_formalizer import try_parse
        from kernel.lp_solver import make_certificate, recheck_certificate, solve_optimal
        from research.D2_lp_vertical.independent_checker import independent_recheck
        spec = try_parse(LAGOS)
        self.assertIsNotNone(spec)
        sol = solve_optimal(spec)
        # Hand-solved (pre-registered in the metadata prompt design):
        # unique interior optimum 30 chairs + 30 tables, profit 345,000.
        self.assertEqual(sol["status"], "optimal")
        self.assertAlmostEqual(sol["x"], 30.0)
        self.assertAlmostEqual(sol["y"], 30.0)
        self.assertAlmostEqual(sol["profit"], 345000.0)
        cert = make_certificate(spec, sol)
        self.assertTrue(recheck_certificate(cert)["accepted"])
        self.assertTrue(independent_recheck(cert)["accepted"])

    def test_nairobi_csp_full_pipeline(self):
        from kernel.csp_formalizer import CSPFormalizer
        from kernel.csp_solver import make_certificate, recheck_certificate, solve
        from research.G3_cert_independence.independent_csp_checker import independent_recheck
        st = ExecutionState(problem_id="d5", problem_text=NAIROBI)
        r = CSPFormalizer().formalize(st)
        self.assertEqual(r["source"], "parser_prose")
        spec = r["spec"]
        self.assertEqual(len(spec["engineers"]), 4)
        self.assertEqual(len(spec["projects"]), 4)
        # 5 captured constraints: 2 explicit forbidden, either-or -> 2
        # forbidden (complement), 1 implies.
        kinds = sorted(c["kind"] for c in spec["constraints"])
        self.assertEqual(kinds, ["forbidden"] * 4 + ["implies"])
        sol = solve(spec)
        self.assertTrue(sol["satisfiable"])
        cert = make_certificate(spec, sol)
        self.assertTrue(recheck_certificate(cert)["accepted"])
        self.assertTrue(independent_recheck(cert)["accepted"])

    def test_benchmark_lp_phrasing_unchanged(self):
        from kernel.lp_formalizer import try_parse
        spec = try_parse(
            "Each unit of small drones requires 3 hours of cutting and 5 "
            "hours of finishing. Each unit of large drones requires 5 hours "
            "of cutting and 4 hours of finishing.\n\nThe workshop has 247 "
            "hours of cutting capacity and 286 hours of finishing capacity "
            "available.\n\nEach unit of small drones yields $40 profit and "
            "each unit of large drones yields $63 profit.")
        self.assertIsNotNone(spec)
        self.assertEqual(spec["c1"], 247.0)
        self.assertEqual(spec["p2"], 63.0)

    def test_prose_family_fails_closed(self):
        from kernel.csp_formalizer import parse_assignment_prose
        self.assertIsNone(parse_assignment_prose("Assign things to places."))
        self.assertIsNone(parse_assignment_prose(
            "We must assign two people - Ann and Ben - to three rooms: "
            "R1, R2, and R3. No recognizable constraint sentences here."))


if __name__ == "__main__":
    unittest.main(verbosity=2)
