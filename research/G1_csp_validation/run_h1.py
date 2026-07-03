"""Gamma Task 6 — H1 on constraint_csp: policy=None (B2, blind) vs
policy=DeterministicPolicy() (B3, guided). Only experimental variable is
feedback visibility (mirrors kernel/loop.py's own design and the
knapsack precedent in research/H1_edge_ai/run.py). Solver is confined to
certification (SolverAttempter is NOT used here) - the LLM is the
candidate generator under test, preserving the verification asymmetry
(checking an assignment is O(constraints); finding one over 2520
permutations by unaided reasoning is not).

    python3 -m research.G1_csp_validation.run_h1 --n 60
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import time

from benchmark.metrics import compare_paired
from benchmark.schema import read_jsonl
from kernel.api import Budget
from kernel.csp_attempters import BlindCSPAttempter, GuidedCSPAttempter
from kernel.csp_formalizer import CSPFormalizer
from kernel.csp_solver import DeterministicCSPExecutor, CSPCertifyingVerifier, recheck_certificate
from kernel.loop import run_kernel
from kernel.policy import DeterministicPolicy
from kernel.state import TraceLogger

HERE = os.path.dirname(__file__)


def true_grade(problem: dict, state) -> bool:
    """Truth from the REAL ground truth, kept outside the kernel on
    purpose - the kernel's own verifier never sees this. Mirrors
    benchmark.metrics._grade_csp exactly but operates on the kernel's
    ExecutionState directly (no benchmark/ import into kernel/)."""
    gt = problem["ground_truth"]
    ans = (state.execution_result or {}).get("answer")
    if ans is None:
        return False
    if not gt["satisfiable"]:
        return ans.get("satisfiable") is False
    if ans.get("satisfiable") is not True:
        return False
    assignment = ans.get("assignment")
    if not isinstance(assignment, dict):
        return False
    if set(assignment) != set(gt["engineers"]):
        return False
    values = list(assignment.values())
    if len(set(values)) != len(values) or not set(values) <= set(gt["projects"]):
        return False
    from benchmark.generator.csp import check_assignment
    return check_assignment(gt["constraints_spec"], gt["project_tags"], assignment)


def run_arm(problems, *, policy, attempter_cls, budget, trace_path):
    formalizer = CSPFormalizer()
    attempter = attempter_cls()
    executor = DeterministicCSPExecutor()
    verifier = CSPCertifyingVerifier()
    logger = TraceLogger(trace_path)
    results = []
    try:
        for problem in problems:
            t0 = time.perf_counter()
            state = run_kernel(problem, formalizer=formalizer, attempter=attempter,
                               executor=executor, verifier=verifier, policy=policy,
                               budget=budget, logger=logger)
            duration_s = time.perf_counter() - t0
            raw_correct = true_grade(problem, state)
            verified = state.trust_label == "Verified"
            verified_correct = verified and raw_correct
            false_certified = verified and not raw_correct

            cert_ok = None
            cert = (state.verifier_result or {}).get("certificate")
            if cert is not None:
                cert_ok = recheck_certificate(cert)["accepted"]

            results.append({
                "id": problem["id"], "base_id": problem["base_id"],
                "category": problem["category"], "variant": problem["variant"],
                "split": problem["split"],
                "trust_label": state.trust_label,
                "raw_correct": raw_correct,
                "verified_correct": verified_correct,
                "false_certified": false_certified,
                "correct": verified_correct,  # compare_paired reads this
                "attempts": state.attempt,
                "duration_s": round(duration_s, 4),
                "certificate_rechecks": cert_ok,
                "formalization_source": state.formalization.get("source"),
            })
    finally:
        logger.close()
    return results


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="llama3.2:1b")
    ap.add_argument("--dataset", default="benchmark/datasets/v1/problems.jsonl")
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--attempts", type=int, default=3)
    ap.add_argument("--timeout", type=float, default=180.0)
    args = ap.parse_args()

    problems = [p for p in read_jsonl(args.dataset)
               if p["category"] == "constraint_csp" and p["split"] == "dev"][:args.n]

    budget = Budget(attempts=args.attempts, timeout_s=args.timeout)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    print(f"B2 (blind retry) on {len(problems)} problems...")
    b2 = run_arm(problems, policy=None, attempter_cls=BlindCSPAttempter,
                budget=budget, trace_path=os.path.join(HERE, f"trace_b2_{stamp}.jsonl"))

    print(f"B3 (guided retry) on {len(problems)} problems...")
    b3 = run_arm(problems, policy=DeterministicPolicy(), attempter_cls=GuidedCSPAttempter,
                budget=budget, trace_path=os.path.join(HERE, f"trace_b3_{stamp}.jsonl"))

    cmp = compare_paired(b2, b3)

    def arm_stats(rows):
        n = len(rows)
        verified = [r for r in rows if r["trust_label"] == "Verified"]
        return {
            "verified_correct_rate": round(sum(r["verified_correct"] for r in rows) / n, 4),
            "false_certification_rate": round(sum(r["false_certified"] for r in rows) / n, 4),
            "coverage": round(len(verified) / n, 4),
            "coverage_at_zero_false_certification": (
                round(len(verified) / n, 4) if sum(r["false_certified"] for r in rows) == 0 else 0.0),
            "mean_attempts": round(sum(r["attempts"] for r in rows) / n, 4),
            "mean_latency_s": round(sum(r["duration_s"] for r in rows) / n, 4),
            "trust_label_breakdown": {
                label: sum(1 for r in rows if r["trust_label"] == label)
                for label in ("Verified", "Derived", "Heuristic", "Open")},
            "every_verified_has_rechecked_certificate": all(
                r["certificate_rechecks"] for r in verified) if verified else None,
        }

    b2_stats, b3_stats = arm_stats(b2), arm_stats(b3)
    out = {
        "n": len(problems), "model": args.model, "budget": budget.to_dict(),
        "b2": b2_stats, "b3": b3_stats,
        "delta_verified_correct_rate": round(
            b3_stats["verified_correct_rate"] - b2_stats["verified_correct_rate"], 4),
        "mcnemar_p": cmp["p_value"], "verdict": cmp["verdict"],
    }
    with open(os.path.join(HERE, f"report_{stamp}.json"), "w") as fh:
        json.dump({"summary": out, "b2": b2, "b3": b3}, fh, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
