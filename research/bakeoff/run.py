"""Model bake-off at L1 (see PLAN.md).

    python3 -m research.bakeoff.run

Runs every candidate on the standard 30-problem dev subset with the L1
reasoning prompt, recording accuracy AND tokens/sec (S_perf is 30% of the
final score). deepseek-r1 gets a larger token budget so its <think> phase
can finish — its verbosity then shows up honestly in the tokens/sec and
latency columns.
"""

from __future__ import annotations

import datetime
import json
import os

from benchmark.metrics import summarize
from benchmark.runner import run
from benchmark.schema import read_jsonl
from research.B0_direct_answer.run import subset
from research.L1_reasoning_prompt.solver import OllamaReasoningSolver

HERE = os.path.dirname(__file__)

CANDIDATES = [
    # (model, num_predict)
    ("qwen2.5:1.5b", 1500),        # incumbent — rerun to capture tokens/sec
    ("gemma3:1b", 1500),
    ("llama3.2:1b", 1500),
    ("deepseek-r1:1.5b", 3500),    # reasoning-tuned: needs room to think
]


class MeteredSolver(OllamaReasoningSolver):
    """Adds tokens/sec accounting from Ollama's eval counters."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_tokens = 0
        self.total_eval_ns = 0

    def _generate(self, prompt):
        out = super()._generate(prompt)
        self.total_tokens += out.get("eval_count", 0)
        self.total_eval_ns += out.get("eval_duration", 0)
        return out

    @property
    def tps(self):
        return (self.total_tokens / (self.total_eval_ns / 1e9)
                if self.total_eval_ns else None)


def main():
    problems = [p for p in read_jsonl("benchmark/datasets/v0/problems.jsonl")
                if p["split"] == "dev"]
    problems = subset(problems, 5)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    rows = []
    for model, num_predict in CANDIDATES:
        solver = MeteredSolver(model=model, num_predict=num_predict,
                               timeout_s=600)
        tag = model.replace(":", "-").replace("/", "-")
        results = run(solver, problems,
                      trace_path=os.path.join(HERE, f"trace_{tag}_{stamp}.jsonl"))
        summary = summarize(problems, results)
        row = {
            "model": model,
            "l1_correct_rate": summary["correct_rate"],
            "messy_delta": summary.get("robustness", {}).get("delta"),
            "mean_latency_s": summary["timing"]["mean_s"],
            "tokens_per_sec": round(solver.tps, 1) if solver.tps else None,
            "mean_tokens": round(solver.total_tokens / len(problems), 1),
        }
        rows.append(row)
        print(json.dumps(row))
        with open(os.path.join(HERE, f"report_{tag}_{stamp}.json"), "w") as fh:
            json.dump(summary, fh, indent=2)

    with open(os.path.join(HERE, f"bakeoff_{stamp}.json"), "w") as fh:
        json.dump(rows, fh, indent=2)
    print("\nFINAL TABLE")
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
