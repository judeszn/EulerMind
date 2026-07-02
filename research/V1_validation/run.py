"""Validation Phase 1 (Task 5): first contract-valid experiment.

Pipeline (contract Principle 2 order): StructuredFormalizer (1B) ->
SolverAttempter (deterministic optimum) -> DeterministicExecutor
(arithmetic) -> OptimalityVerifier (certifies feasible+optimal, emits a
re-checkable certificate). No LLM candidate generation, no retry policy
(the solver is exact). Truth for scoring is benchmark.metrics.grade()
against real ground truth, kept outside the kernel.

    python3 -m research.V1_validation.run --n 60
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import time

import resource
import sys

from benchmark.metrics import grade
from benchmark.schema import read_jsonl
from kernel.edge_ai import DeterministicExecutor, LLMFormalizer
from kernel.edge_ai_formalizer_1b import StructuredFormalizer
from kernel.edge_ai_solver import (OptimalityVerifier, SolverAttempter,
                                   recheck_certificate)
from kernel.state import ExecutionState

HERE = os.path.dirname(__file__)


def peak_rss_mb() -> float:
    ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return (ru if sys.platform == "darwin" else ru * 1024) / 1e6


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="benchmark/datasets/v1/problems.jsonl")
    ap.add_argument("--n", type=int, default=60)
    args = ap.parse_args()

    problems = [p for p in read_jsonl(args.dataset)
               if p["category"] == "edge_ai_deployment" and p["split"] == "dev"][:args.n]

    formalizer = StructuredFormalizer(fallback_formalizer=LLMFormalizer())
    attempter = SolverAttempter()
    executor = DeterministicExecutor()
    verifier = OptimalityVerifier()

    rows = []
    cert_gen_times, solve_times = [], []
    for p in problems:
        state = ExecutionState(problem_id=p["id"], problem_text=p["text"])
        state.formalization = formalizer.formalize(state)

        t0 = time.perf_counter()
        attempt = attempter.attempt(state)
        solve_times.append(time.perf_counter() - t0)

        execution = executor.execute(state, attempt)
        state.execution_result = execution

        t1 = time.perf_counter()
        verdict = verifier.verify(state, execution)
        cert_gen_times.append(time.perf_counter() - t1)
        state.trust_label = verdict.get("trust_label", "Open")

        answer = (execution or {}).get("answer")
        raw_correct = grade(p, answer)
        verified = state.trust_label == "Verified"
        verified_correct = verified and raw_correct
        false_certified = verified and not raw_correct

        # Independent re-check of every emitted certificate (success crit 5).
        cert = verdict.get("certificate")
        cert_rechecks = None
        if cert is not None:
            cert_rechecks = recheck_certificate(cert)["accepted"]

        rows.append({
            "id": p["id"], "base_id": p["base_id"], "variant": p["variant"],
            "trust_label": state.trust_label,
            "formalization_source": state.formalization.get("source"),
            "raw_correct": raw_correct,
            "verified_correct": verified_correct,
            "false_certified": false_certified,
            "has_certificate": cert is not None,
            "certificate_rechecks": cert_rechecks,
        })

    n = len(rows)
    verified = [r for r in rows if r["trust_label"] == "Verified"]
    summary = {
        "n": n,
        "verified_correct_rate": round(sum(r["verified_correct"] for r in rows) / n, 4),
        "false_certification_rate": round(sum(r["false_certified"] for r in rows) / n, 4),
        "coverage": round(len(verified) / n, 4),  # fraction receiving Verified
        "coverage_at_zero_false_certification": (
            round(len(verified) / n, 4) if sum(r["false_certified"] for r in rows) == 0 else 0.0),
        "trust_label_breakdown": {
            label: sum(1 for r in rows if r["trust_label"] == label)
            for label in ("Verified", "Derived", "Heuristic", "Open")},
        "every_verified_has_rechecked_certificate": all(
            r["has_certificate"] and r["certificate_rechecks"] for r in verified),
        "mean_solve_time_s": round(sum(solve_times) / n, 6),
        "mean_certificate_gen_time_s": round(sum(cert_gen_times) / n, 6),
        "peak_rss_mb": round(peak_rss_mb(), 1),
        "formalization_sources": {
            src: sum(1 for r in rows if r["formalization_source"] == src)
            for src in set(r["formalization_source"] for r in rows)},
    }

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(os.path.join(HERE, f"report_{stamp}.json"), "w") as fh:
        json.dump({"summary": summary, "rows": rows}, fh, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
