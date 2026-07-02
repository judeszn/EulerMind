"""Stage A - Formalization Accuracy measurement. Formalizer only.

No solving, no retry, no policy, no executor, no verifier - a single
formalize() call per problem, graded against ground truth.

    python3 -m research.H0_formalization.run --n 60
"""

from __future__ import annotations

import argparse
import datetime
import json
import os

from benchmark.schema import read_jsonl
from kernel.edge_ai import LLMFormalizer
from kernel.state import ExecutionState

from .metrics import score

HERE = os.path.dirname(__file__)


def mean(rows, key):
    vals = [r[key] for r in rows if r[key] is not None]
    return round(sum(vals) / len(vals), 4) if vals else None


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    by_variant = {}
    for variant in ("clean", "messy"):
        sub = [r for r in rows if r["variant"] == variant]
        by_variant[variant] = {
            "n": len(sub),
            "overall_schema_accuracy": mean(sub, "schema_accuracy"),
            "spec_present_rate": round(sum(r["spec_present"] for r in sub) / len(sub), 4) if sub else None,
        }
    totals = {
        "correct": sum(r["counts"]["correct"] for r in rows),
        "swapped": sum(r["counts"]["swapped"] for r in rows),
        "fabricated": sum(r["counts"]["fabricated"] for r in rows),
        "missing_models": sum(r["counts"]["missing_models"] for r in rows),
    }
    return {
        "n": n,
        "spec_present_rate": round(sum(r["spec_present"] for r in rows) / n, 4) if n else None,
        "variable_extraction_accuracy": mean(rows, "var_f1"),
        "numeric_extraction_accuracy": mean(rows, "numeric_accuracy"),
        "field_association_accuracy": mean(rows, "association_accuracy"),
        "unit_normalization_accuracy": mean(rows, "unit_accuracy"),
        "constraint_extraction_accuracy": mean(rows, "constraint_accuracy"),
        "objective_extraction_accuracy": None,  # N/A - see RESULTS.md
        "overall_schema_accuracy": mean(rows, "schema_accuracy"),
        "by_variant": by_variant,
        "error_taxonomy_totals": totals,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="llama3.2:1b")
    ap.add_argument("--dataset", default="benchmark/datasets/v1/problems.jsonl")
    ap.add_argument("--n", type=int, default=60)
    args = ap.parse_args()

    problems = [p for p in read_jsonl(args.dataset)
               if p["category"] == "edge_ai_deployment" and p["split"] == "dev"][:args.n]

    formalizer = LLMFormalizer(model=args.model)
    rows = []
    for p in problems:
        state = ExecutionState(problem_id=p["id"], problem_text=p["text"])
        result = formalizer.formalize(state)
        m = score(p["ground_truth"], result.get("spec"))
        m.update({"id": p["id"], "base_id": p["base_id"], "variant": p["variant"],
                  "formalizer_tokens": result.get("formalizer_tokens", 0)})
        rows.append(m)
        print(f"{p['id']}: schema_accuracy={m['schema_accuracy']:.2f} spec_present={m['spec_present']}")

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(os.path.join(HERE, f"raw_{stamp}.json"), "w") as fh:
        json.dump(rows, fh, indent=2)

    summary = summarize(rows)
    with open(os.path.join(HERE, f"summary_{stamp}.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
