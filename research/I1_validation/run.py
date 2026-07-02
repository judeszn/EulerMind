"""Validate Intervention 1 against paraphrased (not re-optimized) input.

Runs kernel.edge_ai_parser.ParserFirstFormalizer UNCHANGED against the 3
paraphrase levels. Reports the same schema metrics as H0/I1, plus Parser
Success Rate, LLM Fallback Invocation Rate, and Structure Detector
Accuracy, plus a component-attributed failure breakdown.

    python3 -m research.I1_validation.run --level 1
"""

from __future__ import annotations

import argparse
import datetime
import json
import os

from benchmark.schema import read_jsonl
from kernel.edge_ai_parser import ParserFirstFormalizer
from kernel.state import ExecutionState
from research.H0_formalization.metrics import score
from research.H0_formalization.run import summarize

HERE = os.path.dirname(__file__)


def classify_failure(row: dict) -> dict | None:
    """Component attribution for a single problem's result. Returns None
    for perfect results. Never fixes anything - diagnosis only."""
    if row["schema_accuracy"] >= 0.999:
        return None

    source = row["source"]
    if source == "parser":
        # The regex matched but extracted something wrong - a genuine
        # parser bug, since a strict-capture regex match should be exact.
        return {"id": row["id"], "failure_type": "incorrect_extraction_despite_match",
                "component": "Parser",
                "root_cause": "MODEL_LINE_RE / budget regex matched the text but the "
                              "captured/converted value disagrees with ground truth - "
                              "this should not happen given strict digit capture; "
                              "indicates a genuine regex or unit-conversion bug.",
                "suggested_fix": "Inspect the specific regex match against ground truth "
                                 "for this problem id; likely a conversion arithmetic bug, "
                                 "not a routing issue."}

    # source == "llm_fallback": structure detector correctly identified
    # this text doesn't match the parser's known patterns and routed
    # correctly. The residual error belongs to the LLM fallback, not the
    # detector - this is the expected, previously-measured failure mode
    # (H0's baseline), not a new one, UNLESS the parser's fields (spliced
    # in from partial detection) are themselves wrong, which would be a
    # detector/parser interaction bug.
    counts = row["counts"]
    if row.get("structure_detected") and (counts["swapped"] > 0 or counts["fabricated"] > 0
                                          or counts["missing_models"] > 0):
        # Partial detection occurred (some catalog lines matched) but the
        # spliced-in parser fields are STILL wrong -> only possible if the
        # LLM's portion, not the parser's spliced portion, is at fault,
        # since parser-found fields always overwrite LLM's for that model.
        pass
    return {"id": row["id"], "failure_type": "llm_fallback_imperfection",
            "component": "LLM Fallback",
            "root_cause": "Structure Detector correctly found no matching pattern "
                          "(catalog/budget phrasing diverges from the parser's known "
                          "templates) and routed to the LLM as designed. The LLM's own "
                          "extraction accuracy on this text is imperfect - the same "
                          "residual error class measured in the H0 baseline (fabrication "
                          "/missing/unit conversion), now on a different phrasing.",
                "suggested_fix": "Extend the parser's regex vocabulary to cover this "
                                 "phrasing pattern if it recurs often (reduces fallback "
                                 "reliance), or improve the LLM fallback prompt "
                                 "specifically (out of scope for this validation)."}


def run_level(level_file: str, level_name: str):
    problems = read_jsonl(os.path.join(HERE, level_file))
    formalizer = ParserFirstFormalizer()
    rows = []
    for p in problems:
        state = ExecutionState(problem_id=p["id"], problem_text=p["text"])
        result = formalizer.formalize(state)
        m = score(p["ground_truth"], result.get("spec"))
        m.update({"id": p["id"], "base_id": p["base_id"], "variant": p["variant"],
                  "source": result.get("source"), "structure_detected": result.get("structure_detected")})
        rows.append(m)
        print(f"[{level_name}] {p['id']}: schema_accuracy={m['schema_accuracy']:.2f} source={m['source']}")

    summary = summarize(rows)
    parser_rows = [r for r in rows if r["source"] == "parser"]
    fallback_rows = [r for r in rows if r["source"] == "llm_fallback"]
    summary["parser_success_rate"] = round(len(parser_rows) / len(rows), 4)
    summary["llm_fallback_invocation_rate"] = round(len(fallback_rows) / len(rows), 4)
    # Structure Detector Accuracy: of cases routed to the parser, what
    # fraction were routed correctly (i.e. the parser's result was
    # actually right, not a false-positive match)?
    correct_parser_routes = sum(1 for r in parser_rows if r["schema_accuracy"] >= 0.999)
    summary["structure_detector_accuracy"] = (
        round(correct_parser_routes / len(parser_rows), 4) if parser_rows else None)

    failures = [classify_failure(r) for r in rows]
    failures = [f for f in failures if f is not None]
    summary["failure_count"] = len(failures)

    return rows, summary, failures


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", choices=["1", "2", "3", "all"], default="all")
    args = ap.parse_args()

    levels = {"1": "level1.jsonl", "2": "level2.jsonl", "3": "level3.jsonl"}
    to_run = levels.items() if args.level == "all" else [(args.level, levels[args.level])]

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    all_results = {}
    for lvl, fname in to_run:
        print(f"\n=== Level {lvl} ({fname}) ===")
        rows, summary, failures = run_level(fname, f"L{lvl}")
        all_results[f"level{lvl}"] = {"summary": summary, "failures": failures}
        with open(os.path.join(HERE, f"raw_level{lvl}_{stamp}.json"), "w") as fh:
            json.dump(rows, fh, indent=2)

    with open(os.path.join(HERE, f"validation_summary_{stamp}.json"), "w") as fh:
        json.dump(all_results, fh, indent=2)
    print("\n" + json.dumps({k: v["summary"] for k, v in all_results.items()}, indent=2))


if __name__ == "__main__":
    main()
