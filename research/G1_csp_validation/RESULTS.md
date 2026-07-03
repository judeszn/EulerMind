# Phase Gamma — Thesis Validation: constraint_csp RESULTS

**Date:** 2026-07-02 · `llama3.2:1b` · 52-problem `constraint_csp` dev set
(42 satisfiable, 10 unsatisfiable) · fully offline. Solver confined to
certification (Tasks 2–5); the LLM is the candidate generator under test
in Task 6, preserving verification-asymmetry (checking O(constraints);
finding a solution over 2520 permutations by unaided reasoning is not).

## 1. Implementation Summary

Built the missing pipeline for `constraint_csp`, mirroring the knapsack
precedent exactly:

- **Formalizer** (`kernel/csp_formalizer.py`) — parser-first, template
  matching the generator's four fixed constraint renderings; LLM fallback
  wired but structurally inert here (all four templates are always
  deterministic-matchable by construction — this dataset never exercises it).
- **Solver** (`kernel/csp_solver.py`) — exhaustive permutation search
  (2520 permutations), complete, offline, produces a satisfying assignment
  or a minimal conflict set + completeness proof.
- **Verifier** (`CSPCertifyingVerifier`) — certifies exactly the benchmark's
  predicate. Critical design point found during implementation, not assumed:
  a bare LLM UNSAT claim carries no proof (the LLM cannot search 2520
  permutations itself), so the verifier must independently run the solver
  to confirm or refute the claim before any label is assigned — never
  trust "I couldn't find one" as "none exists" (Law 1).
- **Certificate** — SAT: the assignment. UNSAT: minimal conflict set +
  search exhaustion count.
- **Independent checker** (`recheck_certificate`) — separately-implemented
  constraint evaluator (not imported from the generator or the solver's
  own check), re-enumerates independently for UNSAT claims.

## 2. Component Audit

| Component | Contract compliance |
|---|---|
| Formalizer | ✅ parser-first, LLM association-only, never invoked here (60/60 deterministic match in unit test) |
| Solver | ✅ deterministic, complete, offline, matches ground truth 30/30 in isolation |
| Executor | ✅ shape-validation only, no reasoning |
| Verifier | ✅ certifies feasible+valid (SAT) or exhaustively-confirmed-unsatisfiable (UNSAT) — identical to `_grade_csp`'s predicate |
| Trust labels | ✅ Verified only on independently-rechecked certificates; Open on no-candidate or budget exhaustion (Guardrail 5, existing kernel behavior, not new) |
| Certificate | ✅ re-checkable, both branches |

## 3. Positive/Negative Control Results (Task 5)

| Control | Case | Result |
|---|---|---|
| Positive (SAT) | true satisfying assignment | ACCEPT |
| Negative (SAT) | duplicate project | REJECT |
| Negative (SAT) | wrong engineer set | REJECT |
| Negative (SAT) | unknown project | REJECT |
| Negative (SAT) | forced constraint violation (constructed to guarantee a real violation, not a coincidental valid alternate) | REJECT |
| Positive (UNSAT) | true minimal conflict | ACCEPT |
| Negative (UNSAT) | satisfiable set claimed as conflict | REJECT |
| Negative (UNSAT) | non-minimal (full constraint list) claimed as minimal | REJECT |

One test-construction bug was caught and fixed during this process: an
initial "swap two assignments" corruption attempt returned ACCEPT,
which looked like a checker bug — it wasn't. That instance had 892 valid
solutions, so an arbitrary swap had high odds of landing on another
genuinely correct assignment. Fixed by constructing a corruption
*guaranteed* to violate a named constraint rather than an arbitrary swap.
Documented because it's exactly the kind of test-validity check the
control protocol exists to force.

## 4. Certificate Examples

**SAT** (`csp-00001`, illustrative): `{"type": "satisfying_assignment_over_exhaustive_search", "certified_property": "assignment_satisfies_all_constraints", "claimed_assignment": {...}}` — rechecked by re-evaluating every constraint from scratch against the claimed assignment.

**UNSAT** (`csp-00000`, illustrative): `{"type": "minimal_conflict_with_search_exhaustion", "certified_property": "no_assignment_satisfies_all_constraints", "claimed_conflict": [...]}` — rechecked by (a) confirming the conflict set is independently re-enumerated as unsatisfiable and (b) confirming removing any single constraint from it restores ≥1 solution (irreducibility).

## 5. H1 Experiment Report (Task 6)

| Metric | B2 (blind) | B3 (guided) | Δ (B3−B2) |
|---|---|---|---|
| Verified-Correct Rate | 19.23% | 19.23% | **0.0** |
| False Certification Rate | **0.0%** | **0.0%** | 0.0 |
| Coverage | 19.23% | 19.23% | 0.0 |
| Coverage @ Zero False Certification | 19.23% | 19.23% | 0.0 |
| Mean Attempts | 2.73 | 2.62 | −0.11 |
| Mean Latency | 2.72s | 1.27s | −1.45s |
| Every Verified cert rechecked | true (10/10) | true (10/10) | — |
| **McNemar p** | — | — | **1.0** |

Aggregate is a dead tie — but the composition beneath it is not:

| | B2 verified | B3 verified |
|---|---|---|
| On SAT instances (42 total) | 6 | **0** |
| On UNSAT instances (10 total) | 4 | **10 (all of them)** |
| Overlap between arms | 4/16 union (dis­cordant pairs: 6 vs 6) | |

B3 solves every UNSAT instance and zero SAT instances. B2 solves a mix of
both. The aggregate Δ=0 conceals two structurally different behaviors
that happen to sum to the same total — a McNemar-perfect 6-vs-6 discordant
split, about as clean a symmetric null as the statistic can produce.

## 6. Decisive finding: the guided attempter's retries are confirmed
non-functional

Checked across **all 52 problems**, not a sample: of the 42 problems where
B3 needed more than one attempt, **42/42 produced the identical failure
signal on every retry** — zero variation. At temperature 0, given the same
base prompt plus appended feedback, the model generates the same output
every time regardless of what the feedback says.

This is not a hedge or a possible confound — it is a full-sample-confirmed
fact. It means **B3 is not testing "guided feedback vs blind retry."** It
is testing "single-shot temp=0 vs multi-shot temp=0.6 resampling," because
the feedback path was never functionally exercised in 42 of 52 cases. The
10 UNSAT successes happened on attempt 1 (the model's temp=0 default
happens to be a strong UNSAT bias, which is correct exactly on the 10
truly-unsatisfiable instances and wrong on all 42 satisfiable ones) — none
of them involved feedback changing an outcome, because none of them needed
a second attempt to change anything.

## 7. Evidence Protocol Compliance Audit

| Requirement | Status |
|---|---|
| Positive control | ✅ §3 |
| Negative control | ✅ §3 (including a caught-and-fixed test-construction error) |
| Independent checker | ✅ separately implemented, not reused from generator or solver's internal path |
| Frozen benchmark | ✅ `benchmark/datasets/v1`, immutable |
| Frozen success metric | ✅ Verified-Correct Rate, registered before the run |
| Reproducible execution record | ✅ trace + report JSON on disk |

**All six boxes check. This is not an INVALID-experiment case under the
protocol's own STOP rule** (that rule gates data hygiene, which passed
cleanly here — unlike the earlier knapsack H1 run, verifier soundness held
at 0% false-certification throughout). The finding in §6 is a *separate*
question: not "was the science hygienic" (yes) but "did the experiment
exercise the causal mechanism it claims to test" (no, confirmed).

## 8. Decision

**DEFER — narrower and more precisely reasoned than the knapsack DEFER.**

Two things this DEFER is *not*: it is not a validity failure of the
verifier (0% false-certification, every certificate independently
rechecked — the soundness problem that invalidated H1's first run is
fully resolved here). It is not a capability floor (19.23% coverage is
real, non-degenerate signal, unlike knapsack's ~0-5%).

What it is: the specific implementation of "guided" tested here —
temperature-0 prompt-appended feedback — is confirmed, on the full
sample, not to change model output at all. Applying the pre-registered
kill threshold (Δ≥7pts, p<0.05) to this measurement would report "feedback
doesn't help," but the evidence in §6 shows feedback was never delivered
in a way the model responded to. That is a different scientific claim,
and reporting the kill-threshold verdict as if it answered H1 would
overclaim past what was measured — exactly the standard this project's
own Evidence Protocol exists to hold.

Per the stop condition: not proposing a fix, not redesigning the
attempter, not beginning another phase. The specific, falsifiable
open question for whoever runs this next: **does the guided attempter
produce different output on retry when given the SAME feedback content
at a nonzero temperature** — a minimal, targeted check, not a new
architecture.

## 9. Updated Scientific State

| Level | edge_ai_deployment (bounded optimization) | constraint_csp (verification-asymmetric) |
|---|---|---|
| Architecture | Locked | Locked |
| Implementation | Executed | Executed |
| Internal reproducibility | Reported | Reported (this run) |
| H1 (thesis) status | Retired on this vertical (exact solver, no generation gap) | **Untested — confirmed-confounded attempt, not a valid measurement** |
| Independent/Replication/External | Not established | Not established |

The central thesis (verifier-guided feedback beats blind retry) remains
**untested** after two attempts on two verticals — the first invalidated
by verifier unsoundness, the second by a confirmed-inert feedback
mechanism. Both failures are now precisely characterized, not vague. No
valid measurement of H1 exists yet.
