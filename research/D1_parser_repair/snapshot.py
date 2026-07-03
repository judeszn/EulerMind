"""D1 regression harness: snapshot formalizer behaviour on every relevant
split. Run BEFORE the repair (baseline) and AFTER (comparison); the diff
of the two snapshots IS the regression report.

Splits: native edge_ai dev (60), paraphrase L1/L2/L3 (30 each, frozen).
Captured per instance: extracted model-name set, full spec (sorted JSON),
schema accuracy (research/H0_formalization metric, unchanged), source,
fabricated names (extracted - ground truth), missing names (ground truth
- extracted). The LLM fallback is stubbed out (returns nothing) so the
snapshot is fully deterministic and any fallback engagement is visible
as spec=None rather than a network call.

    python3 -m research.D1_parser_repair.snapshot --tag before
"""

from __future__ import annotations

import argparse
import json
import os

from benchmark.schema import read_jsonl
from kernel.edge_ai_formalizer_1b import StructuredFormalizer
from kernel.state import ExecutionState
from research.H0_formalization.metrics import score

HERE = os.path.dirname(__file__)

SPLITS = {
    "native_dev": ("benchmark/datasets/v1/problems.jsonl", "edge_ai_deployment"),
    "paraphrase_L1": ("research/I1_validation/level1.jsonl", None),
    "paraphrase_L2": ("research/I1_validation/level2.jsonl", None),
    "paraphrase_L3": ("research/I1_validation/level3.jsonl", None),
}


class _StubFallback:
    def formalize(self, state):
        return {"kind": "knapsack", "spec": None, "formalizer_tokens": 0}


def snapshot_split(path: str, category: str | None) -> list[dict]:
    problems = [p for p in read_jsonl(path)
               if (category is None or p["category"] == category)
               and p.get("split", "dev") == "dev"]
    f = StructuredFormalizer(fallback_formalizer=_StubFallback())
    rows = []
    for p in problems:
        st = ExecutionState(problem_id=p["id"], problem_text=p["text"])
        r = f.formalize(st)
        spec = r.get("spec")
        models = spec.get("models", {}) if spec else {}
        true_names = set(p["ground_truth"]["models"])
        m = score(p["ground_truth"], spec)
        rows.append({
            "id": p["id"],
            "source": r.get("source"),
            "schema_accuracy": round(m["schema_accuracy"], 6),
            "extracted_names": sorted(models),
            "fabricated": sorted(set(models) - true_names),
            "missing": sorted(true_names - set(models)),
            "spec": json.dumps(spec, sort_keys=True),
        })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()
    out = {}
    for name, (path, cat) in SPLITS.items():
        rows = snapshot_split(path, cat)
        n = len(rows)
        out[name] = {
            "n": n,
            "mean_schema_accuracy": round(sum(r["schema_accuracy"] for r in rows) / n, 4),
            "instances_with_fabrication": sum(1 for r in rows if r["fabricated"]),
            "instances_with_missing": sum(1 for r in rows if r["missing"]),
            "instances_exact_name_match": sum(
                1 for r in rows if not r["fabricated"] and not r["missing"]),
            "rows": rows,
        }
        print(f"{name}: n={n} schema={out[name]['mean_schema_accuracy']} "
              f"fabricated={out[name]['instances_with_fabrication']} "
              f"missing={out[name]['instances_with_missing']} "
              f"exact={out[name]['instances_exact_name_match']}")
    with open(os.path.join(HERE, f"snapshot_{args.tag}.json"), "w") as fh:
        json.dump(out, fh, indent=2)


if __name__ == "__main__":
    main()
