"""Intervention 1B evaluation: StructuredFormalizer vs the same 3 paraphrase
levels used to invalidate 1A. Reuses the existing validation dataset - no
new data, no new generators.

    python3 -m research.I1b_structure.run --level all
"""

from __future__ import annotations

import argparse
import datetime
import json
import os

from benchmark.schema import read_jsonl
from kernel.edge_ai_formalizer_1b import StructuredFormalizer
from kernel.state import ExecutionState
from research.H0_formalization.metrics import score
from research.H0_formalization.run import summarize

HERE = os.path.dirname(__file__)
VAL = os.path.join(os.path.dirname(HERE), "I1_validation")


def run_level(level_file: str, level_name: str):
    problems = read_jsonl(os.path.join(VAL, level_file))
    formalizer = StructuredFormalizer()
    rows = []
    for p in problems:
        state = ExecutionState(problem_id=p["id"], problem_text=p["text"])
        result = formalizer.formalize(state)
        m = score(p["ground_truth"], result.get("spec"))
        m.update({"id": p["id"], "base_id": p["base_id"],
                  "variant": p.get("variant", "paraphrase"),  # summarize() expects this key
                  "source": result.get("source"),
                  "structure_type": result.get("structure_type"),
                  "det_models_found": result.get("det_models_found", 0)})
        rows.append(m)
        print(f"[{level_name}] {p['id']}: schema={m['schema_accuracy']:.2f} "
              f"source={m['source']} struct={m['structure_type']} det={m['det_models_found']}")

    summary = summarize(rows)
    det_rows = [r for r in rows if r["source"] in ("parser", "parser_recovered")]
    fallback_rows = [r for r in rows if r["source"] == "llm_fallback"]
    summary["deterministic_success_rate"] = round(len(det_rows) / len(rows), 4)
    summary["llm_fallback_invocation_rate"] = round(len(fallback_rows) / len(rows), 4)
    correct_det = sum(1 for r in det_rows if r["schema_accuracy"] >= 0.999)
    summary["deterministic_route_accuracy"] = (
        round(correct_det / len(det_rows), 4) if det_rows else None)
    return rows, summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", choices=["1", "2", "3", "all"], default="all")
    args = ap.parse_args()
    levels = {"1": "level1.jsonl", "2": "level2.jsonl", "3": "level3.jsonl"}
    to_run = levels.items() if args.level == "all" else [(args.level, levels[args.level])]

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = {}
    for lvl, fname in to_run:
        print(f"\n=== Level {lvl} ===")
        rows, summary = run_level(fname, f"L{lvl}")
        out[f"level{lvl}"] = summary
        with open(os.path.join(HERE, f"raw_level{lvl}_{stamp}.json"), "w") as fh:
            json.dump(rows, fh, indent=2)
    with open(os.path.join(HERE, f"summary_{stamp}.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print("\n" + json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
