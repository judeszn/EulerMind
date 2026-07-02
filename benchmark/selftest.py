"""Harness self-test: validates the ruler before anything is measured with it.

    python -m benchmark.selftest

Checks:
1. Oracle scores 100% (graders accept known-correct answers).
2. Null scores 0% and all-Open (graders reject non-answers).
3. Graders reject adversarially wrong answers (not vacuously permissive).
4. Unsat CSP instances reject invented assignments (Law 1, mechanically).
5. McNemar exact test sanity values.
6. Generators are deterministic (same seed -> identical problem).
7. Oracle Mode: the real kernel loop passes 100% with mechanical stages,
   the retry path recovers from sabotaged attempts using verifier signals,
   budget exhaustion returns Open (Guardrail 5), and every attempt is
   logged with cost accounting + failure taxonomy (Guardrail 6).
"""

from __future__ import annotations

import sys

from .generator import calculus, csp, lp
from .metrics import compare_paired, grade, mcnemar_exact
from .runner import NullSolver, OracleSolver, run

FAILURES: list[str] = []


def check(name: str, ok: bool) -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        FAILURES.append(name)


def main() -> int:
    problems = []
    for seed in range(6):
        problems += lp.generate(seed)
        problems += calculus.generate(seed)
        problems += csp.generate(seed, force_unsat=(seed >= 4))

    print("harness self-test")
    oracle_results = run(OracleSolver(), problems)
    check("oracle scores 100%", all(r["correct"] for r in oracle_results))

    null_results = run(NullSolver(), problems)
    check("null scores 0%", not any(r["correct"] for r in null_results))
    check("null labels all Open",
          all(r["trust_label"] == "Open" for r in null_results))

    # Adversarial grading: wrong answers must be rejected.
    lp_p = next(p for p in problems if p["category"] == "optimization_lp")
    gt = lp_p["ground_truth"]
    check("lp: wrong profit rejected",
          not grade(lp_p, {"x": gt["x"], "y": gt["y"], "profit": gt["profit"] + 1}))
    check("lp: infeasible plan rejected",
          not grade(lp_p, {"x": gt["x"] * 100, "y": gt["y"] * 100,
                           "profit": gt["profit"]}))

    calc_p = next(p for p in problems if p["category"] == "calculus_poly")
    flipped = [{"x": c["x"],
                "type": "local_min" if c["type"] == "local_max" else "local_max"}
               for c in calc_p["ground_truth"]["critical_points"]]
    check("calculus: flipped classification rejected",
          not grade(calc_p, {"critical_points": flipped}))

    sat_p = next(p for p in problems if p["category"] == "constraint_csp"
                 and p["ground_truth"]["satisfiable"])
    dupe = {e: sat_p["ground_truth"]["projects"][0]
            for e in sat_p["ground_truth"]["engineers"]}
    check("csp: non-distinct assignment rejected",
          not grade(sat_p, {"satisfiable": True, "assignment": dupe}))

    unsat_p = next(p for p in problems if p["category"] == "constraint_csp"
                   and not p["ground_truth"]["satisfiable"])
    invented = dict(zip(unsat_p["ground_truth"]["engineers"],
                        unsat_p["ground_truth"]["projects"]))
    check("csp unsat: invented assignment rejected (Law 1)",
          not grade(unsat_p, {"satisfiable": True, "assignment": invented}))
    check("csp unsat: honest refusal accepted",
          grade(unsat_p, {"satisfiable": False}))
    check("csp unsat: minimal conflict recorded",
          len(unsat_p["ground_truth"]["minimal_conflict"]) >= 1)

    # Oracle Mode: mechanical EulerMind through the real kernel loop.
    from kernel.api import Budget
    from kernel.oracle import FlakyOracleAttempter, run_oracle_mode

    class ListLogger:
        def __init__(self):
            self.records = []

        def log(self, record):
            self.records.append(record)

    logger = ListLogger()
    states = [run_oracle_mode(p, logger=logger) for p in problems]
    check("oracle mode: 100% Verified through the kernel loop",
          all(s.trust_label == "Verified" and s.attempt == 1 for s in states))
    check("oracle mode: every attempt logged with budget + cost fields",
          len(logger.records) == len(problems)
          and all({"schema_version", "budget", "latency_ms", "tokens",
                   "failure_type"} <= set(r) for r in logger.records))

    flaky_logger = ListLogger()
    flaky_states = [run_oracle_mode(p, attempter=FlakyOracleAttempter(1),
                                    logger=flaky_logger) for p in problems]
    check("oracle mode: retry recovers from sabotaged first attempt",
          all(s.trust_label == "Verified" and s.attempt == 2 for s in flaky_states))
    check("oracle mode: failures carry taxonomy + signals",
          all(r["failure_type"] == "verification" and r["signals"]
              for r in flaky_logger.records if r["verification"] == "failed"))

    exhausted = run_oracle_mode(problems[0],
                                attempter=FlakyOracleAttempter(99),
                                budget=Budget(attempts=2))
    check("oracle mode: exhausted budget returns Open (Guardrail 5)",
          exhausted.trust_label == "Open" and exhausted.attempt == 2)

    # Statistics sanity.
    check("mcnemar: no discordant pairs -> p=1", mcnemar_exact(0, 0) == 1.0)
    check("mcnemar: 10-0 discordant is significant", mcnemar_exact(0, 10) < 0.05)
    check("mcnemar: 6-4 discordant is not significant", mcnemar_exact(6, 4) > 0.05)
    cmp = compare_paired(oracle_results, null_results)
    check("compare_paired: oracle beats null decisively",
          cmp["verdict"] == "a_better" and cmp["p_value"] < 0.001)

    # Determinism.
    check("generators deterministic",
          lp.generate(3) == lp.generate(3)
          and calculus.generate(3) == calculus.generate(3)
          and csp.generate(3, force_unsat=True) == csp.generate(3, force_unsat=True))

    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURE(S): {FAILURES}")
        return 1
    print("\nall checks passed — the ruler is calibrated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
