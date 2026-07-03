"""H1b-Gamma-2: sampling robustness of the H1b-Gamma-1 conclusion.

New experiment, not a rerun: seed is the independent variable. Every other
registered field is held identical to Gamma-1 (model, benchmark, dataset,
prompts, verifier, certificate, executor, policy, temperature 0.6, retry
budget). Five independent seed batches (offsets 0, 1000, 2000, 3000, 4000)
- batch 0 is exactly the Gamma-1 configuration, serving as a positive
control that the harness still produces the known result.

Pre-registered N=5 (confirmatory batch, not power-driven: Gamma-1's p=0.79
is far from the 0.05 boundary, so the question is whether the qualitative
verdict survives sampling variation, which a small fixed batch answers).
Success = all 5 batches land on the same side of the kill threshold
(Δ≥7 AND p<0.05 would be needed to overturn "Rejected by the Registered
Decision Rule"). Repeated-measures on the same 52 problems - report each
batch separately, do NOT pool.

    python3 -m research.G2b_sampling_robustness.run
"""

from __future__ import annotations

import datetime
import json
import os
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
SEED_OFFSETS = [0, 1000, 2000, 3000, 4000]  # pre-registered N=5, fixed before any data
MECHANISM_THRESHOLD = 0.50  # inherited from Gamma-1, pre-registered


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
            state = run_kernel(problem, formalizer=formalizer, attempter=attempter,
                               executor=executor, verifier=verifier, policy=policy,
                               budget=budget, logger=logger)
            raw_correct = true_grade(problem, state)
            verified = state.trust_label == "Verified"
            results.append({
                "id": problem["id"], "trust_label": state.trust_label,
                "raw_correct": raw_correct,
                "verified_correct": verified and raw_correct,
                "false_certified": verified and not raw_correct,
                "correct": verified and raw_correct,
                "attempts": state.attempt,
                "certificate_rechecks": (
                    recheck_certificate((state.verifier_result or {}).get("certificate"))["accepted"]
                    if (state.verifier_result or {}).get("certificate") is not None else None),
            })
    finally:
        logger.close()
    return results


def variation_rate(trace_path: str) -> float | None:
    recs = [json.loads(l) for l in open(trace_path)]
    by_prob = defaultdict(list)
    for r in recs:
        by_prob[r["problem_id"]].append(r)
    identical = varied = 0
    for attempts in by_prob.values():
        if len(attempts) < 2:
            continue
        sigs = [tuple(sorted((s["kind"], str(s["evidence"])) for s in a["signals"]))
                for a in attempts]
        if len(set(sigs)) == 1:
            identical += 1
        else:
            varied += 1
    multi = identical + varied
    return round(varied / multi, 4) if multi else None


def arm_verified_correct_rate(rows):
    return round(sum(r["verified_correct"] for r in rows) / len(rows), 4)


def main() -> None:
    problems = [p for p in read_jsonl(DATASET)
               if p["category"] == "constraint_csp" and p["split"] == "dev"]
    budget = Budget(attempts=3, timeout_s=180.0)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    batches = []

    for offset in SEED_OFFSETS:
        tb2 = os.path.join(HERE, f"trace_b2_off{offset}_{stamp}.jsonl")
        tb3 = os.path.join(HERE, f"trace_b3_off{offset}_{stamp}.jsonl")
        b2 = run_arm(problems, policy=None,
                    attempter=BlindCSPAttempter(seed_offset=offset),
                    budget=budget, trace_path=tb2)
        b3 = run_arm(problems, policy=DeterministicPolicy(),
                    attempter=GuidedCSPAttempter(temperature=0.6, seed_offset=offset),
                    budget=budget, trace_path=tb3)
        cmp = compare_paired(b2, b3)
        b2_vcr, b3_vcr = arm_verified_correct_rate(b2), arm_verified_correct_rate(b3)
        mech_b2, mech_b3 = variation_rate(tb2), variation_rate(tb3)
        false_cert = (sum(r["false_certified"] for r in b2)
                     + sum(r["false_certified"] for r in b3))
        certs_ok = all(r["certificate_rechecks"] for r in (b2 + b3)
                      if r["trust_label"] == "Verified")
        # verdict vs kill threshold: overturned only if guided beats blind
        # by >=7pts AND p<0.05. Otherwise "Rejected by the Registered
        # Decision Rule" stands.
        overturned = ((b3_vcr - b2_vcr) * 100 >= 7) and (cmp["p_value"] < 0.05)
        batch = {
            "seed_offset": offset,
            "b2_verified_correct_rate": b2_vcr, "b3_verified_correct_rate": b3_vcr,
            "delta_pts": round((b3_vcr - b2_vcr) * 100, 2),
            "mcnemar_p": cmp["p_value"],
            "mechanism_b2": mech_b2, "mechanism_b3": mech_b3,
            "mechanism_gate_passed": (mech_b2 is not None and mech_b2 >= MECHANISM_THRESHOLD
                                      and mech_b3 is not None and mech_b3 >= MECHANISM_THRESHOLD),
            "false_certifications": false_cert,
            "all_verified_certs_recheck": certs_ok,
            "verdict_this_batch": "overturned" if overturned else "rejected_by_decision_rule",
        }
        batches.append(batch)
        print(json.dumps(batch))

    verdicts = {b["verdict_this_batch"] for b in batches}
    mech_all = all(b["mechanism_gate_passed"] for b in batches)
    false_all_zero = all(b["false_certifications"] == 0 for b in batches)
    out = {
        "experiment": "H1b-Gamma-2 sampling robustness",
        "n_batches": len(batches), "seed_offsets": SEED_OFFSETS,
        "batches": batches,
        "qualitative_verdict_unanimous": len(verdicts) == 1,
        "unanimous_verdict": next(iter(verdicts)) if len(verdicts) == 1 else None,
        "mechanism_gate_passed_all": mech_all,
        "false_certification_zero_all": false_all_zero,
        "delta_range_pts": [min(b["delta_pts"] for b in batches),
                            max(b["delta_pts"] for b in batches)],
        "p_range": [min(b["mcnemar_p"] for b in batches),
                    max(b["mcnemar_p"] for b in batches)],
    }
    with open(os.path.join(HERE, f"report_{stamp}.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print("\n=== SUMMARY ===")
    print(json.dumps({k: v for k, v in out.items() if k != "batches"}, indent=2))


if __name__ == "__main__":
    main()
