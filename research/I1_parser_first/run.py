"""Intervention 1: parser-first extraction, measured against the H0 baseline.

Same evaluator (research/H0_formalization/metrics.py, unmodified logic,
only additive fields), same 60 dev problems, same scoring - only the
Formalizer implementation under test changes (ParserFirstFormalizer
instead of LLMFormalizer), so the comparison is apples-to-apples.

    python3 -m research.I1_parser_first.run --n 60
"""

from __future__ import annotations

import argparse
import datetime
import json
import os

from benchmark.schema import read_jsonl
from kernel.edge_ai_parser import ParserFirstFormalizer
from kernel.state import ExecutionState
from research.H0_formalization.metrics import NUMERIC_FIELDS, score
from research.H0_formalization.run import summarize

HERE = os.path.dirname(__file__)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="benchmark/datasets/v1/problems.jsonl")
    ap.add_argument("--n", type=int, default=60)
    args = ap.parse_args()

    problems = [p for p in read_jsonl(args.dataset)
               if p["category"] == "edge_ai_deployment" and p["split"] == "dev"][:args.n]

    formalizer = ParserFirstFormalizer()
    rows = []
    fallback_count = 0
    for p in problems:
        state = ExecutionState(problem_id=p["id"], problem_text=p["text"])
        result = formalizer.formalize(state)
        if result.get("source") == "llm_fallback":
            fallback_count += 1
        m = score(p["ground_truth"], result.get("spec"))
        m.update({"id": p["id"], "base_id": p["base_id"], "variant": p["variant"],
                  "source": result.get("source"), "structure_detected": result.get("structure_detected")})
        rows.append(m)
        print(f"{p['id']}: schema_accuracy={m['schema_accuracy']:.2f} "
              f"source={m['source']} spec_present={m['spec_present']}")

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(os.path.join(HERE, f"raw_{stamp}.json"), "w") as fh:
        json.dump(rows, fh, indent=2)

    summary = summarize(rows)
    summary["fallback_engaged_count"] = fallback_count
    summary["fallback_engaged_rate"] = round(fallback_count / len(rows), 4) if rows else None

    by_field = {f: {"correct": 0, "swapped": 0, "fabricated": 0} for f in NUMERIC_FIELDS}
    for r in rows:
        for f in NUMERIC_FIELDS:
            for k in ("correct", "swapped", "fabricated"):
                by_field[f][k] += r["by_field"][f][k]
    for f in NUMERIC_FIELDS:
        total = sum(by_field[f].values())
        by_field[f]["fabrication_rate"] = round(by_field[f]["fabricated"] / total, 4) if total else None
    summary["fabrication_by_field"] = by_field

    with open(os.path.join(HERE, f"summary_{stamp}.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
