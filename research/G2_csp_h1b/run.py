"""Gamma execution authorization: temperature-matched H1b on constraint_csp.

Step 1 (sanity check, gates everything else): confirm GuidedCSPAttempter()
at its default (temperature=0) still reproduces the frozen H1a finding -
42/42 identical signals across multi-attempt problems - proving the seed
refactor didn't silently alter the already-registered configuration.

Step 2 (main experiment): BlindCSPAttempter (temp=0.6, seed=attempt, no
feedback) vs GuidedCSPAttempter(temperature=0.6) (temp=0.6, seed=attempt,
WITH feedback) - single-variable design, feedback-presence is the only
deliberate difference. Formalizer/Solver/Executor/Verifier/Certificate
code is completely unchanged from research/G1_csp_validation/.

Step 3: mechanism check (>=50%, pre-registered) - only if it passes for
BOTH arms is the Delta/McNemar result interpreted as evidence about H1b.

    python3 -m research.G2_csp_h1b.run
"""

from __future__ import annotations

import datetime
import json
import os
import time
from collections import defaultdict

from benchmark.metrics import compare_paired
from benchmark.schema import read_jsonl
from kernel.api import Budget
from kernel.csp_attempters import BlindCSPAttempter, GuidedCSPAttempter
from kernel.csp_formalizer import CSPFormalizer
from kernel.csp_solver import CSPCertifyingVerifier, DeterministicCSPExecutor, recheck_certificate
from kernel.loop import run_kernel
from kernel.policy import DeterministicPolicy
from kernel.state import TraceLogger

HERE = os.path.dirname(__file__)
DATASET = "benchmark/datasets/v1/problems.jsonl"
MECHANISM_THRESHOLD = 0.50  # pre-registered before results were seen


def true_grade(problem, state) -> bool:
    gt = problem["ground_truth"]
    ans = (state.execution_result or {}).get("answer")
    if ans is None:
        return False
    if not gt["satisfiable"]:
        return ans.get("satisfiable") is False
    if ans.get("satisfiable") is not True:
        return False
    assignment = ans.get("assignment")
    if not isinstance(assignment, dict) or set(assignment) != set(gt["engineers"]):
        return False
    values = list(assignment.values())
    if len(set(values)) != len(values) or not set(values) <= set(gt["projects"]):
        return False
    from benchmark.generator.csp import check_assignment
    return check_assignment(gt["constraints_spec"], gt["project_tags"], assignment)


def run_arm(problems, *, policy, attempter, budget, trace_path):
    formalizer = CSPFormalizer()
    executor = DeterministicCSPExecutor()
    verifier = CSPCertifyingVerifier()
    logger = TraceLogger(trace_path)
    results = []
    try:
        for problem in problems:
            t0 = time.perf_counter()
            state = run_kernel(problem, formalizer=formalizer, attempter=attempter,
                               executor=executor, verifier=verifier, policy=policy,
                               budget=budget, logger=logger)
            duration_s = time.perf_counter() - t0
            raw_correct = true_grade(problem, state)
            verified = state.trust_label == "Verified"
            verified_correct = verified and raw_correct
            false_certified = verified and not raw_correct
            cert = (state.verifier_result or {}).get("certificate")
            cert_ok = recheck_certificate(cert)["accepted"] if cert is not None else None
            results.append({
                "id": problem["id"], "base_id": problem["base_id"],
                "trust_label": state.trust_label, "raw_correct": raw_correct,
                "verified_correct": verified_correct, "false_certified": false_certified,
                "correct": verified_correct, "attempts": state.attempt,
                "duration_s": round(duration_s, 4), "certificate_rechecks": cert_ok,
            })
    finally:
        logger.close()
    return results


def mechanism_variation_rate(trace_path: str) -> dict:
    """Fraction of multi-attempt problems where NOT every attempt produced
    the identical failure signal - the exact check that found 42/42 in the
    original run, now applied as a pre-registered gate."""
    recs = [json.loads(l) for l in open(trace_path)]
    by_prob = defaultdict(list)
    for r in recs:
        by_prob[r["problem_id"]].append(r)
    identical, varied, single = 0, 0, 0
    for pid, attempts in by_prob.items():
        if len(attempts) < 2:
            single += 1
            continue
        sigs = [tuple(sorted((s["kind"], str(s["evidence"])) for s in a["signals"]))
                for a in attempts]
        if len(set(sigs)) == 1:
            identical += 1
        else:
            varied += 1
    multi = identical + varied
    return {"multi_attempt_problems": multi, "identical": identical, "varied": varied,
           "single_attempt": single,
           "variation_rate": round(varied / multi, 4) if multi else None}


def main() -> None:
    problems = [p for p in read_jsonl(DATASET)
               if p["category"] == "constraint_csp" and p["split"] == "dev"]
    budget = Budget(attempts=3, timeout_s=180.0)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = {}

    # --- Step 1: sanity check (gates everything else) ---
    print("Step 1: sanity check - does GuidedCSPAttempter() default still reproduce 42/42?")
    sanity_trace = os.path.join(HERE, f"trace_sanity_temp0_{stamp}.jsonl")
    sanity_results = run_arm(problems, policy=DeterministicPolicy(),
                             attempter=GuidedCSPAttempter(), budget=budget,
                             trace_path=sanity_trace)
    sanity_mech = mechanism_variation_rate(sanity_trace)
    out["sanity_check_temp0"] = sanity_mech
    print(json.dumps(sanity_mech, indent=2))
    sanity_passed = sanity_mech["varied"] == 0 and sanity_mech["multi_attempt_problems"] > 0
    out["sanity_check_passed"] = sanity_passed
    print(f"Sanity check {'PASSED' if sanity_passed else 'FAILED'} "
         f"(expect varied=0, got varied={sanity_mech['varied']})")
    if not sanity_passed:
        print("STOP: refactor altered historical temp=0 behavior. Not proceeding.")
        with open(os.path.join(HERE, f"report_{stamp}.json"), "w") as fh:
            json.dump(out, fh, indent=2)
        return

    # --- Step 2: temperature-matched main experiment ---
    print("\nStep 2: temperature-matched H1b (both arms temp=0.6, seed=attempt)")
    trace_b2 = os.path.join(HERE, f"trace_b2_{stamp}.jsonl")
    trace_b3 = os.path.join(HERE, f"trace_b3_{stamp}.jsonl")
    b2 = run_arm(problems, policy=None, attempter=BlindCSPAttempter(),
                budget=budget, trace_path=trace_b2)
    b3 = run_arm(problems, policy=DeterministicPolicy(),
                attempter=GuidedCSPAttempter(temperature=0.6),
                budget=budget, trace_path=trace_b3)

    # --- Step 3: mechanism check gate ---
    mech_b2 = mechanism_variation_rate(trace_b2)
    mech_b3 = mechanism_variation_rate(trace_b3)
    out["mechanism_check"] = {"b2": mech_b2, "b3": mech_b3, "threshold": MECHANISM_THRESHOLD}
    gate_passed = (mech_b2["variation_rate"] is not None and mech_b2["variation_rate"] >= MECHANISM_THRESHOLD
                  and mech_b3["variation_rate"] is not None and mech_b3["variation_rate"] >= MECHANISM_THRESHOLD)
    out["mechanism_gate_passed"] = gate_passed
    print(f"\nmechanism variation rate: B2={mech_b2['variation_rate']}, "
         f"B3={mech_b3['variation_rate']} (threshold {MECHANISM_THRESHOLD})")
    print(f"mechanism gate: {'PASSED' if gate_passed else 'FAILED'}")

    cmp = compare_paired(b2, b3)

    def arm_stats(rows):
        n = len(rows)
        verified = [r for r in rows if r["trust_label"] == "Verified"]
        return {
            "verified_correct_rate": round(sum(r["verified_correct"] for r in rows) / n, 4),
            "false_certification_rate": round(sum(r["false_certified"] for r in rows) / n, 4),
            "mean_attempts": round(sum(r["attempts"] for r in rows) / n, 4),
            "every_verified_has_rechecked_certificate": (
                all(r["certificate_rechecks"] for r in verified) if verified else None),
        }

    b2_stats, b3_stats = arm_stats(b2), arm_stats(b3)
    out.update({
        "n": len(problems), "b2": b2_stats, "b3": b3_stats,
        "delta_verified_correct_rate": round(
            b3_stats["verified_correct_rate"] - b2_stats["verified_correct_rate"], 4),
        "mcnemar_p": cmp["p_value"], "verdict": cmp["verdict"],
        "interpretable_as_H1b_evidence": gate_passed,
    })
    with open(os.path.join(HERE, f"report_{stamp}.json"), "w") as fh:
        json.dump({"summary": out, "b2": b2, "b3": b3}, fh, indent=2)
    print("\n" + json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
