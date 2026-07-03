"""H3 Delta experiment — formalization checking reduces verified-wrong outputs.

BEGIN IMPLEMENTATION registered task: does an independent structural check
on the formalization stage reduce the rate of "Verified" answers that are
actually wrong, without cutting the overall verified-correct rate?

Required Precondition (must pass before H3 is tested): the formalization
error base rate on the registered evaluation split must be > 0, or the
intervention has no opportunity to act and the experiment must stop.

Dataset registration (frozen, not modified, not regenerated):
research/I1_validation/level3.jsonl — the "mixed"/adversarial paraphrase
level, 30 instances, byte-identical ground truth to the main benchmark.
Chosen because it is the only one of the three paraphrase levels with a
previously-diagnosed nonzero residual error under the CURRENT production
formalizer (research/I1b_structure/RESULTS.md: 88.9% schema accuracy,
pure omission, 0 fabrication/swaps).

Comparison arms (only the formalization stage differs; same frozen
Attempter/Executor/Verifier/Policy for both):
  - Baseline: StructuredFormalizer (production, unchecked)
  - Experimental: CheckedStructuredFormalizer (adds one independent
    structural cross-check; withholds the spec on disagreement)
Both run through the UNMODIFIED kernel.loop.run_kernel with
SolverAttempter + DeterministicExecutor + OptimalityVerifier
(kernel/edge_ai_solver.py, kernel/edge_ai.py — none touched), policy=None,
budget=Budget(attempts=1) (deterministic solver, no retry loop; H3 is
about formalization, not retry policy).

Interpretation order enforced by construction: (1) precondition checked
first — stop if base rate is 0; (2) base-rate report is itself proof the
intervention had an opportunity to act; (3) certificate correctness and
(4) independent-checker agreement are reconfirmed unchanged before (5)
the statistical comparison is read.

    python3 -m research.H3_formalization_checking.run
"""

from __future__ import annotations

import datetime
import json
import os

from benchmark.metrics import compare_paired, grade
from benchmark.schema import read_jsonl
from kernel.api import Budget
from kernel.edge_ai import DeterministicExecutor
from kernel.edge_ai_formalizer_1b import StructuredFormalizer
from kernel.edge_ai_solver import OptimalityVerifier, SolverAttempter
from kernel.loop import run_kernel
from kernel.state import ExecutionState
from research.G3_cert_independence.independent_checker import independent_recheck
from research.H0_formalization.metrics import score

from .checked_formalizer import CheckedStructuredFormalizer, independent_model_count

HERE = os.path.dirname(__file__)
DATASET = "research/I1_validation/level3.jsonl"  # frozen; not modified; not regenerated


def measure_base_rate(problems: list[dict]) -> tuple[int, list[dict]]:
    """Precondition. Reuses research/H0_formalization's existing score()
    metric unchanged — no new error metric invented for the gate."""
    f = StructuredFormalizer()
    rows = []
    errors = 0
    for p in problems:
        state = ExecutionState(problem_id=p["id"], problem_text=p["text"])
        result = f.formalize(state)
        m = score(p["ground_truth"], result.get("spec"))
        is_error = m["schema_accuracy"] < 0.999
        errors += int(is_error)
        rows.append({"id": p["id"], "schema_accuracy": m["schema_accuracy"], "error": is_error})
    return errors, rows


def run_arm(problems: list[dict], formalizer_factory) -> list[dict]:
    rows = []
    for p in problems:
        st = run_kernel(p, formalizer=formalizer_factory(), attempter=SolverAttempter(),
                        executor=DeterministicExecutor(), verifier=OptimalityVerifier(),
                        policy=None, budget=Budget(attempts=1))
        verified = st.trust_label == "Verified"
        answer = (st.execution_result or {}).get("answer")
        correct = bool(answer) and grade(p, answer)
        cert = (st.verifier_result or {}).get("certificate")
        indep_agrees = independent_recheck(cert)["accepted"] if (verified and cert) else None
        rows.append({"id": p["id"], "trust_label": st.trust_label, "verified": verified,
                     "correct": correct, "verified_wrong": verified and not correct,
                     "independent_recheck_agrees": indep_agrees})
    return rows


def main() -> None:
    problems = list(read_jsonl(DATASET))
    n = len(problems)

    # ---- Required Precondition ----
    error_count, base_rows = measure_base_rate(problems)
    base_rate = round(error_count / n, 4)
    print("=== Precondition: formalization error base rate ===")
    print(json.dumps({"n": n, "formalization_errors": error_count,
                      "formalization_error_rate": base_rate}, indent=2))

    result: dict = {"n": n, "dataset": DATASET,
                    "precondition": {"formalization_errors": error_count,
                                     "formalization_error_rate": base_rate}}

    if error_count == 0:
        result["stopped"] = True
        result["reason"] = "H3 not exercised because the intervention had no opportunity to act."
        print(result["reason"])
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        with open(os.path.join(HERE, f"report_{stamp}.json"), "w") as fh:
            json.dump(result, fh, indent=2)
        return

    # ---- Controls on the independent structural counter itself ----
    error_ids = {r["id"] for r in base_rows if r["error"]}
    counter_rows = []
    for p in problems:
        expected = independent_model_count(p["text"])
        true_n = len(p["ground_truth"]["models"])
        counter_rows.append({"id": p["id"], "has_known_formalization_error": p["id"] in error_ids,
                             "independent_count_matches_true_count": expected == true_n})
    false_flags_on_correct = sum(1 for r in counter_rows
                                 if not r["has_known_formalization_error"]
                                 and not r["independent_count_matches_true_count"])
    counter_correct_on_error_cases = sum(1 for r in counter_rows
                                         if r["has_known_formalization_error"]
                                         and r["independent_count_matches_true_count"])
    controls = {
        "positive_control_no_false_flags_on_error_free_instances":
            false_flags_on_correct == 0,
        "negative_control_counter_correctly_sized_on_all_error_instances":
            counter_correct_on_error_cases == error_count,
    }
    print("\n=== Controls ===")
    print(json.dumps(controls, indent=2))
    result["controls"] = controls

    # ---- Main comparison ----
    baseline_rows = run_arm(problems, StructuredFormalizer)
    experimental_rows = run_arm(problems, CheckedStructuredFormalizer)

    def summarize(rows, label):
        return {"verified_rate": round(sum(r["verified"] for r in rows) / n, 4),
                "verified_correct_rate": round(sum(r["correct"] and r["verified"] for r in rows) / n, 4),
                "verified_wrong_rate": round(sum(r["verified_wrong"] for r in rows) / n, 4),
                "verified_wrong_count": sum(r["verified_wrong"] for r in rows),
                "independent_checker_disagreements": sum(
                    1 for r in rows if r["independent_recheck_agrees"] is False)}

    baseline_summary = summarize(baseline_rows, "baseline")
    experimental_summary = summarize(experimental_rows, "experimental")
    print("\n=== Arms ===")
    print("Baseline (unchecked):", json.dumps(baseline_summary, indent=2))
    print("Experimental (checked):", json.dumps(experimental_summary, indent=2))
    result["baseline"] = baseline_summary
    result["experimental"] = experimental_summary

    # certificate correctness / independence unchanged (Success Criteria 4-5)
    cert_regression = (baseline_summary["independent_checker_disagreements"] > 0
                       or experimental_summary["independent_checker_disagreements"] > 0)
    result["certificate_correctness_regressed"] = cert_regression
    result["independent_checker_agreement_100pct"] = not cert_regression

    # ---- Statistical comparison (registered test: McNemar, via compare_paired) ----
    not_verified_wrong_a = [{"id": r["id"], "correct": not r["verified_wrong"]} for r in baseline_rows]
    not_verified_wrong_b = [{"id": r["id"], "correct": not r["verified_wrong"]} for r in experimental_rows]
    vw_stats = compare_paired(not_verified_wrong_a, not_verified_wrong_b)
    # relabel a/b -> baseline/experimental for clarity in the report
    vw_stats = {"baseline_not_verified_wrong_rate": vw_stats["a_rate"],
               "experimental_not_verified_wrong_rate": vw_stats["b_rate"],
               "baseline_only_not_verified_wrong": vw_stats["a_only_correct"],
               "experimental_only_not_verified_wrong": vw_stats["b_only_correct"],
               "p_value": vw_stats["p_value"], "verdict": vw_stats["verdict"],
               "n_paired": vw_stats["n_paired"]}

    correct_a = [{"id": r["id"], "correct": r["correct"]} for r in baseline_rows]
    correct_b = [{"id": r["id"], "correct": r["correct"]} for r in experimental_rows]
    correctness_stats = compare_paired(correct_a, correct_b)
    correctness_stats = {"baseline_correct_rate": correctness_stats["a_rate"],
                         "experimental_correct_rate": correctness_stats["b_rate"],
                         "p_value": correctness_stats["p_value"],
                         "verdict": correctness_stats["verdict"]}

    print("\n=== Statistical comparison (McNemar via compare_paired) ===")
    print("Verified-wrong (inverted to not-verified-wrong, higher=better):",
         json.dumps(vw_stats, indent=2))
    print("Overall correctness (must not regress):", json.dumps(correctness_stats, indent=2))
    result["verified_wrong_comparison"] = vw_stats
    result["overall_correctness_comparison"] = correctness_stats

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(os.path.join(HERE, f"report_{stamp}.json"), "w") as fh:
        json.dump({"summary": result,
                  "baseline_rows": baseline_rows, "experimental_rows": experimental_rows,
                  "counter_control_rows": counter_rows}, fh, indent=2)


if __name__ == "__main__":
    main()
