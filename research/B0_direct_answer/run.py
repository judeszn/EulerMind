"""Run the B0 baseline on a dev subset.

    python3 -m research.B0_direct_answer.run --model qwen2.5:1.5b --bases 5

Subsampling is deterministic: the first N base_ids (sorted) per category,
taking both clean and messy variants, so robustness deltas are paired and
reruns are comparable.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os

from benchmark.metrics import summarize
from benchmark.runner import run
from benchmark.schema import read_jsonl

from .solver import OllamaDirectSolver

HERE = os.path.dirname(__file__)


def subset(problems, bases_per_category):
    picked = []
    by_cat = {}
    for p in sorted(problems, key=lambda p: p["id"]):
        by_cat.setdefault(p["category"], []).append(p)
    for cat, ps in sorted(by_cat.items()):
        base_ids = sorted({p["base_id"] for p in ps})[:bases_per_category]
        picked += [p for p in ps if p["base_id"] in base_ids]
    return picked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5:1.5b")
    ap.add_argument("--dataset", default="benchmark/datasets/v0/problems.jsonl")
    ap.add_argument("--bases", type=int, default=5,
                    help="base instances per category (x2 variants)")
    args = ap.parse_args()

    problems = [p for p in read_jsonl(args.dataset) if p["split"] == "dev"]
    problems = subset(problems, args.bases)

    solver = OllamaDirectSolver(model=args.model)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    trace = os.path.join(HERE, f"trace_{stamp}.jsonl")
    results = run(solver, problems, trace_path=trace)
    summary = summarize(problems, results)

    with open(os.path.join(HERE, f"report_{stamp}.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
