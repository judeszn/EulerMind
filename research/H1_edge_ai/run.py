"""Intervention 2 / H1 on edge_ai_deployment:
policy=None (B2, blind retry) vs policy=DeterministicPolicy() (B3, guided).

    python3 -m research.H1_edge_ai.run --bases 30 --model llama3.2:1b

Same kernel, same executor, same verifier, same Formalizer (Intervention
1B's StructuredFormalizer - the completed, frozen artifact) for both arms.
`policy` drives next_action inside the loop; the two Attempter classes
differ in temperature/feedback-visibility by design of the pre-registered
experiment (whitepaper/HYPOTHESES.md H1) - a temp=0, feedback-blind
attempter under policy=None would produce three byte-identical failed
attempts, which is not a meaningful blind-retry baseline, just a
mislabeled single-shot.

Truth for scoring comes from benchmark.metrics.grade() against the REAL
ground truth, kept outside the kernel on purpose (the kernel must never
see ground truth or import benchmark/) - comparing that against the
kernel's own trust_label is exactly the False-Verification-Rate measure.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import time

from benchmark.metrics import compare_paired, grade
from benchmark.schema import read_jsonl
from kernel.api import Budget
from kernel.edge_ai import (BlindAttempter, DeterministicExecutor,
                            GuidedAttempter, KnapsackVerifier)
from kernel.edge_ai_formalizer_1b import StructuredFormalizer
from kernel.loop import run_kernel
from kernel.policy import DeterministicPolicy
from kernel.state import TraceLogger

HERE = os.path.dirname(__file__)


def run_arm(problems, *, model, policy, attempter_cls, budget, trace_path):
    from kernel.edge_ai import LLMFormalizer
    formalizer = StructuredFormalizer(fallback_formalizer=LLMFormalizer(model=model))
    attempter = attempter_cls(model=model)
    executor = DeterministicExecutor()
    verifier = KnapsackVerifier()
    logger = TraceLogger(trace_path)
    results = []
    try:
        for problem in problems:
            t0 = time.perf_counter()
            state = run_kernel(problem, formalizer=formalizer, attempter=attempter,
                               executor=executor, verifier=verifier, policy=policy,
                               budget=budget, logger=logger)
            duration_s = time.perf_counter() - t0
            answer = (state.execution_result or {}).get("answer")
            raw_correct = grade(problem, answer)
            verified_correct = state.trust_label == "Verified" and raw_correct
            false_verified = state.trust_label == "Verified" and not raw_correct
            results.append({
                "id": problem["id"], "base_id": problem["base_id"],
                "category": problem["category"], "variant": problem["variant"],
                "split": problem["split"],
                "trust_label": state.trust_label,
                "raw_correct": raw_correct,       # final answer right, regardless of label
                "verified_correct": verified_correct,
                "false_verified": false_verified,  # Verified label but WRONG answer
                # H1's claim is about VERIFIED correctness, not bare
                # correctness - compare_paired reads this field's name.
                "correct": verified_correct,
                "attempts": state.attempt,
                "duration_s": round(duration_s, 4), "peak_rss_bytes": 0,
            })
    finally:
        logger.close()
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="llama3.2:1b")
    ap.add_argument("--dataset", default="benchmark/datasets/v1/problems.jsonl")
    ap.add_argument("--bases", type=int, default=10)
    ap.add_argument("--only", default=None, help="run a single problem id (e.g. the demo instance)")
    ap.add_argument("--attempts", type=int, default=3)
    ap.add_argument("--timeout", type=float, default=180.0)
    args = ap.parse_args()

    problems = [p for p in read_jsonl(args.dataset)
               if p["category"] == "edge_ai_deployment" and p["split"] == "dev"]
    if args.only:
        problems = [p for p in problems if p["id"] == args.only]
    else:
        base_ids = sorted({p["base_id"] for p in problems})[:args.bases]
        problems = [p for p in problems if p["base_id"] in base_ids]

    budget = Budget(attempts=args.attempts, timeout_s=args.timeout)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    print(f"B2 (blind retry) on {len(problems)} problems...")
    b2 = run_arm(problems, model=args.model, policy=None, attempter_cls=BlindAttempter,
                budget=budget, trace_path=os.path.join(HERE, f"trace_b2_{stamp}.jsonl"))

    print(f"B3 (guided retry) on {len(problems)} problems...")
    b3 = run_arm(problems, model=args.model, policy=DeterministicPolicy(),
                attempter_cls=GuidedAttempter, budget=budget,
                trace_path=os.path.join(HERE, f"trace_b3_{stamp}.jsonl"))

    cmp = compare_paired(b2, b3)

    def arm_stats(rows):
        n = len(rows)
        return {
            "verified_correct_rate": round(sum(r["verified_correct"] for r in rows) / n, 4),
            "false_verification_rate": round(sum(r["false_verified"] for r in rows) / n, 4),
            "mean_attempts": round(sum(r["attempts"] for r in rows) / n, 4),
            "mean_latency_s": round(sum(r["duration_s"] for r in rows) / n, 4),
            "trust_label_breakdown": {
                label: sum(1 for r in rows if r["trust_label"] == label)
                for label in ("Verified", "Derived", "Heuristic", "Open")
            },
        }

    out = {
        "n": len(problems), "model": args.model, "budget": budget.to_dict(),
        "b2": arm_stats(b2), "b3": arm_stats(b3),
        "delta_verified_correct_rate": round(
            arm_stats(b3)["verified_correct_rate"] - arm_stats(b2)["verified_correct_rate"], 4),
        "mcnemar_p": cmp["p_value"], "verdict": cmp["verdict"],
    }
    with open(os.path.join(HERE, f"report_{stamp}.json"), "w") as fh:
        json.dump({"summary": out, "b2": b2, "b3": b3}, fh, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
