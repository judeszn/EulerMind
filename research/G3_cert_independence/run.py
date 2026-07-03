"""Gamma+1 (H-Independence) experiment.

For every edge_ai_deployment dev problem: regenerate the certificate the
system produces (StructuredFormalizer -> solve_optimal -> make_certificate,
all deterministic on native format), then compare two verdicts:
  - PRIMARY: kernel.edge_ai_solver.recheck_certificate (shares the solver's
    pruned DFS search)
  - INDEPENDENT: research.G3_cert_independence.independent_checker
    (brute-force, no pruning, no shared search code)

Plus a third, oracle-level cross-check: the independent optimum vs the
benchmark's separately-implemented ground-truth score.

Controls (mandatory Evidence Protocol):
  - positive: independent checker accepts the true optimum certificate.
  - negative: independent checker rejects corrupted certificates
    (inflated score, infeasible counts, feasible-but-suboptimal).

    python3 -m research.G3_cert_independence.run
"""

from __future__ import annotations

import copy
import datetime
import json
import os

from benchmark.schema import read_jsonl
from kernel.edge_ai_formalizer_1b import StructuredFormalizer
from kernel.edge_ai_solver import make_certificate, recheck_certificate, solve_optimal
from kernel.state import ExecutionState

from .independent_checker import independent_recheck, independent_optimum

HERE = os.path.dirname(__file__)
DATASET = "benchmark/datasets/v1/problems.jsonl"


def main() -> None:
    problems = [p for p in read_jsonl(DATASET)
               if p["category"] == "edge_ai_deployment" and p["split"] == "dev"]
    formalizer = StructuredFormalizer()

    rows = []
    disagreements = []
    fallback_specs = 0
    for p in problems:
        state = ExecutionState(problem_id=p["id"], problem_text=p["text"])
        result = formalizer.formalize(state)
        spec = result.get("spec")
        if spec is None:
            fallback_specs += 1
            continue
        sol = solve_optimal(spec)
        if not sol["feasible"]:
            continue
        cert = make_certificate(spec, sol["counts"], sol["score"])

        primary = recheck_certificate(cert)["accepted"]
        indep = independent_recheck(cert)
        indep_ok = indep["accepted"]

        # oracle cross-check: independent optimum vs benchmark ground truth
        gt_score = p["ground_truth"]["score"]
        indep_opt = indep.get("independent_optimum")
        matches_ground_truth = (indep_opt == gt_score)

        row = {"id": p["id"], "primary": primary, "independent": indep_ok,
               "agree": primary == indep_ok,
               "independent_optimum": indep_opt, "ground_truth_score": gt_score,
               "matches_ground_truth": matches_ground_truth}
        rows.append(row)
        if primary != indep_ok or not matches_ground_truth:
            disagreements.append({**row, "reason": indep["reason"]})

    # ---- controls ----
    sample = next(p for p in problems if p["split"] == "dev")
    ss = ExecutionState(problem_id=sample["id"], problem_text=sample["text"])
    sspec = formalizer.formalize(ss)["spec"]
    ssol = solve_optimal(sspec)
    good = make_certificate(sspec, ssol["counts"], ssol["score"])

    pos = independent_recheck(good)["accepted"]

    neg = {}
    c1 = copy.deepcopy(good); c1["claimed_score"] = ssol["score"] + 1000
    neg["inflated_score"] = not independent_recheck(c1)["accepted"]
    names = list(sspec["models"])
    c2 = copy.deepcopy(good); c2["claimed_counts"] = {n: 99 for n in names}
    c2["claimed_score"] = ssol["score"]
    neg["infeasible_counts"] = not independent_recheck(c2)["accepted"]
    # feasible-but-suboptimal: one high-acc model only
    sub = {n: 0 for n in names}
    for n in names:
        if sspec["models"][n]["accuracy"] >= sspec["high_acc_threshold"]:
            sub[n] = 1; break
    subscore = sum(sub[n] * sspec["models"][n]["score"] for n in names)
    c3 = copy.deepcopy(good); c3["claimed_counts"] = sub; c3["claimed_score"] = subscore
    neg["feasible_suboptimal"] = (subscore == ssol["score"]) or (not independent_recheck(c3)["accepted"])

    n = len(rows)
    summary = {
        "n_certificates": n,
        "formalizer_fallback_specs": fallback_specs,
        "primary_independent_agreement": sum(r["agree"] for r in rows),
        "agreement_rate": round(sum(r["agree"] for r in rows) / n, 4) if n else None,
        "independent_matches_ground_truth": sum(r["matches_ground_truth"] for r in rows),
        "ground_truth_match_rate": round(sum(r["matches_ground_truth"] for r in rows) / n, 4) if n else None,
        "false_certifications_under_independent_check": sum(
            1 for r in rows if r["independent"] and r["independent_optimum"] != r["ground_truth_score"]),
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
