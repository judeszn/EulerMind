"""Benchmark runner: executes a solver over the dataset, grades every answer,
logs every run to a JSONL trace (Guardrail 6), and writes a report.

    python -m benchmark.runner --dataset benchmark/datasets/v0/problems.jsonl \
        --solver oracle --split dev

Reference solvers validate the harness itself:
- oracle: reads ground truth, must score 100% (proves graders accept truth)
- null:   always answers Open, must score 0%  (proves graders reject nothing-answers)

RAM note: peak_rss is process-lifetime maximum RSS — meaningful for solver
processes that dominate memory (Phase 1 runs llama.cpp in a subprocess and
will report the child's peak instead). Per-problem RSS deltas are NOT
reliable; only the run-level peak is reported.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import resource
import sys
import time

from .metrics import grade, summarize
from .schema import read_jsonl


def peak_rss_bytes() -> int:
    ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return ru if sys.platform == "darwin" else ru * 1024  # linux reports KiB


class OracleSolver:
    """Answers from ground truth. Harness validation only — proves the
    graders accept a known-correct answer for every problem."""
    name = "oracle"

    def solve(self, problem: dict) -> dict:
        gt = problem["ground_truth"]
        kind = problem["answer_spec"]["type"]
        if kind == "lp":
            answer = {"x": gt["x"], "y": gt["y"], "profit": gt["profit"]}
        elif kind == "calculus":
            answer = {"critical_points": gt["critical_points"]}
        elif kind == "csp":
            answer = {"satisfiable": gt["satisfiable"]}
            if gt["satisfiable"]:
                answer["assignment"] = gt["example"]
        elif kind == "knapsack":
            answer = {"counts": gt["counts"], "score": gt["score"]}
        else:
            raise ValueError(kind)
        return {"answer": answer, "trust_label": "Verified", "attempts": 1}


class NullSolver:
    """Always returns Open with no answer. Must score exactly 0%."""
    name = "null"

    def solve(self, problem: dict) -> dict:
        return {"answer": None, "trust_label": "Open", "attempts": 0}


SOLVERS = {"oracle": OracleSolver, "null": NullSolver}


def run(solver, problems: list[dict], trace_path: str | None = None) -> list[dict]:
    results = []
    trace = open(trace_path, "a", encoding="utf-8") if trace_path else None
    try:
        for problem in problems:
            t0 = time.perf_counter()
            out = solver.solve(problem)
            duration = time.perf_counter() - t0
            record = {
                "schema_version": 1,
                "id": problem["id"],
                "base_id": problem["base_id"],
                "category": problem["category"],
                "variant": problem["variant"],
                "split": problem["split"],
                "solver": solver.name,
                "correct": grade(problem, out.get("answer")),
                "trust_label": out.get("trust_label", "Open"),
                "attempts": out.get("attempts", 1),
                "duration_s": round(duration, 6),
                "peak_rss_bytes": peak_rss_bytes(),
            }
            results.append(record)
            if trace:
                trace.write(json.dumps(record) + "\n")
    finally:
        if trace:
            trace.close()
    return results


def _markdown_report(solver_name: str, split: str, summary: dict) -> str:
    lines = [
        f"# Benchmark report — solver `{solver_name}` (split: {split})",
        "",
        f"- problems: **{summary['n']}**",
        f"- correct rate: **{summary['correct_rate']}**",
        f"- verified-correct rate: **{summary['verified_correct_rate']}**",
    ]
    if "robustness" in summary:
        r = summary["robustness"]
        lines.append(f"- formalization robustness (clean − messy, {r['n_pairs']} pairs): "
                     f"clean {r['clean_rate']} vs messy {r['messy_rate']} "
                     f"(delta {r['delta']})")
    if "epistemic_unsat" in summary:
        e = summary["epistemic_unsat"]
        lines.append(f"- epistemic discipline (unsat instances, n={e['n']}): "
                     f"**{e['correct_rate']}**")
    if "timing" in summary:
        t = summary["timing"]
        lines.append(f"- timing: mean {t['mean_s']}s, p95 {t['p95_s']}s")
    if "peak_rss_mb" in summary:
        lines.append(f"- peak RSS: {summary['peak_rss_mb']} MB")
    lines += ["", "| category | n | correct | verified-correct |", "|---|---|---|---|"]
    for cat, s in summary["by_category"].items():
        lines.append(f"| {cat} | {s['n']} | {s['correct_rate']} "
                     f"| {s['verified_correct_rate']} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="Run a solver over the benchmark.")
    ap.add_argument("--dataset", default="benchmark/datasets/v0/problems.jsonl")
    ap.add_argument("--solver", choices=sorted(SOLVERS), required=True)
    ap.add_argument("--split", choices=["dev", "holdout", "all"], default="dev")
    ap.add_argument("--out", default="benchmark/reports")
    args = ap.parse_args()

    problems = read_jsonl(args.dataset)
    if args.split != "all":
        problems = [p for p in problems if p["split"] == args.split]

    os.makedirs(args.out, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tag = f"{args.solver}_{args.split}_{stamp}"

    solver = SOLVERS[args.solver]()
    results = run(solver, problems,
                  trace_path=os.path.join(args.out, f"trace_{tag}.jsonl"))
    summary = summarize(problems, results)

    with open(os.path.join(args.out, f"report_{tag}.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    md = _markdown_report(args.solver, args.split, summary)
    with open(os.path.join(args.out, f"report_{tag}.md"), "w") as fh:
        fh.write(md)
    print(md)


if __name__ == "__main__":
    main()
