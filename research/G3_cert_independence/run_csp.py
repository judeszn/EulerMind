"""Gamma+2 (H-Independence-CSP) experiment — CSP analogue of Gamma+1.

For every constraint_csp dev problem: regenerate the certificate the
system produces (CSPFormalizer -> solve -> make_certificate, all
deterministic parser-first), then compare two verdicts:
  - PRIMARY: kernel.csp_solver.recheck_certificate (shares solve()'s
    `_check` / `_enumerate_solutions`)
  - INDEPENDENT: research.G3_cert_independence.independent_csp_checker
    (backtracking search with incremental pruning, separately-written
    evaluator, no shared code)

Plus a third, oracle-level cross-check: an independent FULL enumeration
(no limit) of the certificate's spec, compared against the benchmark
dataset's own precomputed `ground_truth.solution_count` (SAT count, or 0
for UNSAT) — a value computed independently at dataset-build time by
neither the solver nor either checker.

Controls (mandatory Evidence Protocol) cover BOTH certificate types
(satisfying-assignment and minimal-conflict), since CSP — unlike
edge_ai's single certificate type — has two:
  - positive: independent checker accepts a true SAT certificate and a
    true UNSAT (minimal-conflict) certificate.
  - negative: independent checker rejects a constraint-violating
    assignment, a satisfiable set claimed as a conflict, and a
    non-minimal (non-irreducible) conflict set.

    python3 -m research.G3_cert_independence.run_csp
"""

from __future__ import annotations

import copy
import datetime
import json
import os

from benchmark.schema import read_jsonl
from kernel.csp_formalizer import CSPFormalizer
from kernel.csp_solver import make_certificate, recheck_certificate, solve
from kernel.state import ExecutionState

from .independent_csp_checker import backtracking_search, independent_recheck

HERE = os.path.dirname(__file__)
DATASET = "benchmark/datasets/v1/problems.jsonl"


def _oracle_count(cert: dict) -> int:
    """Third-oracle cross-check: independent FULL enumeration (no limit)
    over the certificate's spec, using the same backtracking search but
    with no cap on solutions found."""
    spec = cert["spec"]
    sols = backtracking_search(spec["engineers"], spec["projects"],
                               spec["project_tags"], spec["constraints"], limit=None)
    return len(sols)


def main() -> None:
    problems = [p for p in read_jsonl(DATASET)
               if p["category"] == "constraint_csp" and p["split"] == "dev"]
    formalizer = CSPFormalizer()

    rows = []
    disagreements = []
    fallback_specs = 0
    sat_certs = unsat_certs = 0
    for p in problems:
        state = ExecutionState(problem_id=p["id"], problem_text=p["text"])
        result = formalizer.formalize(state)
        spec = result.get("spec")
        if spec is None:
            fallback_specs += 1
            continue
        solution = solve(spec)
        cert = make_certificate(spec, solution)
        cert_type = cert["type"]
        if cert_type == "satisfying_assignment_over_exhaustive_search":
            sat_certs += 1
        else:
            unsat_certs += 1

        primary = recheck_certificate(cert)["accepted"]
        indep = independent_recheck(cert)
        indep_ok = indep["accepted"]

        oracle_count = _oracle_count(cert)
        gt_count = p["ground_truth"]["solution_count"]
        matches_ground_truth = (oracle_count == gt_count)

        row = {"id": p["id"], "cert_type": cert_type, "primary": primary,
               "independent": indep_ok, "agree": primary == indep_ok,
               "oracle_solution_count": oracle_count, "ground_truth_solution_count": gt_count,
               "matches_ground_truth": matches_ground_truth}
        rows.append(row)
        if primary != indep_ok or not matches_ground_truth:
            disagreements.append({**row, "reason": indep["reason"]})

    # ---- controls: need one SAT sample and one UNSAT sample ----
    sat_sample = next(p for p in problems if p["ground_truth"]["satisfiable"])
    unsat_sample = next(p for p in problems if not p["ground_truth"]["satisfiable"])

    ss = ExecutionState(problem_id=sat_sample["id"], problem_text=sat_sample["text"])
    sat_spec = formalizer.formalize(ss)["spec"]
    sat_sol = solve(sat_spec)
    good_sat = make_certificate(sat_spec, sat_sol)

    us = ExecutionState(problem_id=unsat_sample["id"], problem_text=unsat_sample["text"])
    unsat_spec = formalizer.formalize(us)["spec"]
    unsat_sol = solve(unsat_spec)
    good_unsat = make_certificate(unsat_spec, unsat_sol)

    pos = {
        "accepts_true_sat_assignment": independent_recheck(good_sat)["accepted"],
        "accepts_true_unsat_conflict": independent_recheck(good_unsat)["accepted"],
    }

    neg = {}
    # negative 1: SAT cert with an assignment that violates a forbidden constraint
    bad_assignment = dict(good_sat["claimed_assignment"])
    forbidden = next((c for c in sat_spec["constraints"] if c["kind"] == "forbidden"), None)
    if forbidden is not None:
        bad_assignment[forbidden["engineer"]] = forbidden["project"]
    c1 = copy.deepcopy(good_sat)
    c1["claimed_assignment"] = bad_assignment
    neg["constraint_violating_assignment"] = not independent_recheck(c1)["accepted"]

    # negative 2: UNSAT cert claiming a conflict set that is actually satisfiable (empty set)
    c2 = copy.deepcopy(good_unsat)
    c2["claimed_conflict"] = []
    neg["satisfiable_set_claimed_as_conflict"] = not independent_recheck(c2)["accepted"]

    # negative 3: UNSAT cert claiming a non-minimal conflict (the full constraint list,
    # when the true minimal conflict is a strict subset)
    c3 = copy.deepcopy(good_unsat)
    c3["claimed_conflict"] = unsat_spec["constraints"]
    is_actually_minimal = len(unsat_spec["constraints"]) == len(good_unsat["claimed_conflict"])
    neg["non_minimal_conflict"] = is_actually_minimal or (not independent_recheck(c3)["accepted"])

    n = len(rows)
    summary = {
        "n_certificates": n,
        "sat_certificates": sat_certs,
        "unsat_certificates": unsat_certs,
        "formalizer_fallback_specs": fallback_specs,
        "primary_independent_agreement": sum(r["agree"] for r in rows),
        "agreement_rate": round(sum(r["agree"] for r in rows) / n, 4) if n else None,
        "independent_matches_ground_truth": sum(r["matches_ground_truth"] for r in rows),
        "ground_truth_match_rate": round(sum(r["matches_ground_truth"] for r in rows) / n, 4) if n else None,
        "false_certifications_under_independent_check": sum(
            1 for r in rows if r["independent"] and not r["matches_ground_truth"]),
        "positive_controls": pos,
        "positive_controls_all_pass": all(pos.values()),
        "negative_controls": neg,
        "negative_controls_all_reject": all(neg.values()),
        "disagreements": disagreements,
    }
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(os.path.join(HERE, f"report_csp_{stamp}.json"), "w") as fh:
        json.dump({"summary": summary, "rows": rows}, fh, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
