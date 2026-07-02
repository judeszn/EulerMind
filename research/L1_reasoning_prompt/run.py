"""Run L1 on the same deterministic dev subset as L0 (paired by design).

    python3 -m research.L1_reasoning_prompt.run --model qwen2.5:1.5b --bases 5
"""

from __future__ import annotations

import argparse
import datetime
import json
import os

from benchmark.metrics import summarize
from benchmark.runner import run
from benchmark.schema import read_jsonl
from research.B0_direct_answer.run import subset

from .solver import OllamaReasoningSolver

HERE = os.path.dirname(__file__)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5:1.5b")
    ap.add_argument("--dataset", default="benchmark/datasets/v0/problems.jsonl")
    ap.add_argument("--bases", type=int, default=5)
    args = ap.parse_args()

    problems = [p for p in read_jsonl(args.dataset) if p["split"] == "dev"]
    problems = subset(problems, args.bases)

    solver = OllamaReasoningSolver(model=args.model)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    results = run(solver, problems,
                  trace_path=os.path.join(HERE, f"trace_{stamp}.jsonl"))
    summary = summarize(problems, results)

    with open(os.path.join(HERE, f"report_{stamp}.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
