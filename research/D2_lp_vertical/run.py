"""Delta D2 (H-LP) experiment — the third certified vertical,
optimization_lp, and its Certificate Independence in the same registered
task (learning from Gamma/Gamma+1/+2's two-pass history: build
correctness and independence together from the start).

For every optimization_lp problem (dev + holdout, clean + messy - 80
total): formalize (LPFormalizer) -> solve (solve_optimal, vertex
enumeration / Fundamental Theorem of LP) -> certify (make_certificate)
-> compare two verdicts:
  - PRIMARY: kernel.lp_solver.recheck_certificate (shares the solver's
    vertex-enumeration search)
  - INDEPENDENT: research.D2_lp_vertical.independent_checker
    (LP Duality Theorem - complementary slackness + strong duality, zero
    search)

Plus oracle cross-check against benchmark.metrics.grade() (feasibility +
consistency + optimality against the dataset's own ground truth, computed
independently at generation time via exact-Fraction vertex enumeration).

Controls (mandatory Evidence Protocol):
  - positive: independent checker accepts the true optimum.
  - negative: independent checker rejects infeasible / suboptimal-feasible
    claims.
  - unbounded: solver classifies a synthetic unbounded instance correctly
    (the real dataset never contains one by construction - constructed
    per the standing rule that synthetic controls are for validating the
    mechanism, not for manufacturing benchmark evidence).

    python3 -m research.D2_lp_vertical.run
"""

from __future__ import annotations

import copy
import datetime
import json
import os

from benchmark.metrics import grade
from benchmark.schema import read_jsonl
from kernel.lp_formalizer import LPFormalizer
from kernel.lp_solver import make_certificate, recheck_certificate, solve_optimal
from kernel.state import ExecutionState

from .independent_checker import independent_recheck

HERE = os.path.dirname(__file__)
DATASET = "benchmark/datasets/v1/problems.jsonl"


def main() -> None:
    problems = [p for p in read_jsonl(DATASET) if p["category"] == "optimization_lp"]
    formalizer = LPFormalizer()

    rows = []
    disagreements = []
    fallback_specs = 0
    degenerate_no_witness = 0
    for p in problems:
        state = ExecutionState(problem_id=p["id"], problem_text=p["text"])
        result = formalizer.formalize(state)
        spec = result.get("spec")
        if spec is None:
            fallback_specs += 1
            continue
        sol = solve_optimal(spec)
        if sol["status"] != "optimal":
            continue  # real dataset is always feasible+bounded; defensive only
        cert = make_certificate(spec, sol)

        primary = recheck_certificate(cert)["accepted"]
        indep = independent_recheck(cert)
        indep_ok = indep["accepted"]
        if not indep_ok and "degenerate vertex" in indep["reason"]:
            degenerate_no_witness += 1

        graded_correct = grade(p, {"x": sol["x"], "y": sol["y"], "profit": sol["profit"]})

        row = {"id": p["id"], "split": p["split"], "variant": p["variant"],
               "primary": primary, "independent": indep_ok, "agree": primary == indep_ok,
               "graded_correct": graded_correct,
               "matches_ground_truth": graded_correct}
        rows.append(row)
        if primary != indep_ok or not graded_correct:
            disagreements.append({**row, "reason": indep["reason"],
                                  "x": sol["x"], "y": sol["y"], "profit": sol["profit"]})

    # ---- controls ----
    sample = next(p for p in problems if p["split"] == "dev")
    ss = ExecutionState(problem_id=sample["id"], problem_text=sample["text"])
    sspec = formalizer.formalize(ss)["spec"]
    ssol = solve_optimal(sspec)
    good = make_certificate(sspec, ssol)

    pos = independent_recheck(good)["accepted"]

    neg = {}
    c1 = copy.deepcopy(good)
    c1["claimed_x"], c1["claimed_y"] = sspec["c1"] / sspec["a1"] + 1000, 0.0  # blow past constraint1
    c1["claimed_profit"] = sspec["p1"] * c1["claimed_x"]
    neg["infeasible_claim_rejected"] = not independent_recheck(c1)["accepted"]

    c2 = copy.deepcopy(good)
    c2["claimed_x"], c2["claimed_y"] = 0.0, 0.0  # feasible (origin) but suboptimal for this instance
    c2["claimed_profit"] = 0.0
    neg["suboptimal_feasible_claim_rejected"] = (
        (ssol["x"] == 0.0 and ssol["y"] == 0.0) or not independent_recheck(c2)["accepted"])

    unb_spec = {"a1": 0, "b1": 1, "c1": 5, "a2": 0, "b2": 1, "c2": 5, "p1": 10, "p2": 1}
    unb_sol = solve_optimal(unb_spec)
    neg["unbounded_instance_classified_correctly"] = (unb_sol["status"] == "unbounded")

    inf_spec = {"a1": 1, "b1": 1, "c1": -5, "a2": 1, "b2": 1, "c2": 10, "p1": 1, "p2": 1}
    inf_sol = solve_optimal(inf_spec)
    neg["infeasible_instance_classified_correctly"] = (inf_sol["status"] == "infeasible")

    n = len(rows)
    summary = {
        "n_certificates": n,
        "formalizer_fallback_specs": fallback_specs,
        "degenerate_vertices_no_dual_witness": degenerate_no_witness,
        "primary_independent_agreement": sum(r["agree"] for r in rows),
        "agreement_rate": round(sum(r["agree"] for r in rows) / n, 4) if n else None,
        "independent_matches_ground_truth": sum(r["matches_ground_truth"] for r in rows),
        "ground_truth_match_rate": round(sum(r["matches_ground_truth"] for r in rows) / n, 4) if n else None,
        "false_certifications_under_independent_check": sum(
            1 for r in rows if r["independent"] and not r["matches_ground_truth"]),
        "positive_control_accepts_true_optimum": pos,
        "negative_controls": neg,
        "negative_controls_all_reject": all(neg.values()),
        "disagreements": disagreements,
    }
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(os.path.join(HERE, f"report_{stamp}.json"), "w") as fh:
        json.dump({"summary": summary, "rows": rows}, fh, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
