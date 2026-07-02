# Validation Phase 1 — RESULTS (first contract-valid experiment)

**Date:** 2026-07-02 · 60-problem `edge_ai_deployment` dev set · fully
offline · peak RSS 27.6 MB. Run under locked Research Contract v1.0.

## 0. Provenance & reproduction

Executed, not asserted. The pipeline was run via the shell in-session; the
report JSON (`report_20260702-230958.json`) is on disk. A fresh re-run
reproduced every correctness figure bit-identically (Verified-Correct 1.0,
False-Cert 0.0, solver-vs-ground-truth 60/60, negative control REJECT).
Two metrics are environment-noisy and vary run-to-run — peak RSS
(27.6↔27.7 MB) and mean solve time (76↔56 µs); report them as "≈27.7 MB,
sub-ms". All other figures are deterministic (exhaustive search has no
randomness) and reproduce exactly.

**Mandatory experiment-control protocol (adopted as standard):** every
EulerMind experiment must include a *positive control* (a known-valid
certificate is accepted), a *negative control* (corrupted certificates are
rejected), and an *independent re-check* (a separate implementation agrees).
This run satisfies all three; the protocol makes them required, not
incidental.

## 1. Implementation Summary

Replaced LLM candidate-generation with a deterministic solver for the
bounded-optimization vertical, and replaced the feasibility-checking
verifier with an optimality-certifying one. Pipeline (contract Principle 2
order): `StructuredFormalizer` (1B) → `SolverAttempter` (exact optimum) →
`DeterministicExecutor` (arithmetic) → `OptimalityVerifier` (certifies
feasible+optimal, emits a re-checkable certificate). No LLM candidate
generation, no retry policy — the solver is exact, so there is nothing to
retry (contract Principle 4).

## 2. Solver Description (Task 1)

`kernel/edge_ai_solver.py::solve_optimal`. Exhaustive DFS over the feasible
integer region, pruned by monotone additive resource bounds: at each model
it tries counts 0,1,2,… and stops the moment one more unit would exceed a
budget given resources already committed — valid because resource use is
additive and non-negative, so no larger count can become feasible later.
Complete by construction (every feasible integer point is visited). No LLM,
fully offline, mean solve time 76 µs, peak 27.6 MB. Verified against the
benchmark's independently-computed ground truth: **score match 60/60.**

## 3. Certificate Definition (Task 3)

| Field | Value |
|---|---|
| **Type** | `exhaustive_feasible_region_search` |
| **Certified property** | optimal over all feasible integer deployments under the (formalized) spec |
| **Contents** | claimed counts, claimed score, full spec (models/budgets/threshold), pruning method |
| **Independent verification procedure** | `recheck_certificate()` — recomputes feasibility from scratch, recomputes the score from counts, and re-searches for the optimum, then confirms claimed == found |

**Negative control (Task 3 rigor, demanded before trusting the label):**
the checker was fed corrupted certificates and **rejected every one** —
inflated score (`4249 ≠ recomputed 3249`), infeasible counts (`violates a
budget`), and **feasible-but-suboptimal** (`claimed 677 is not optimal,
true 3249`). That last rejection is the precise Verified≠Correct failure
that invalidated H1 — now caught, not stamped. The true optimum is
accepted. The certificate is a filter, not a rubber stamp.

## 4. Verification Alignment Report (Task 2)

The old `KnapsackVerifier` certified **feasibility + self-consistency**;
`grade()` requires **feasibility + optimality**. That gap was Mismatch 1
(H1 invalidation). `OptimalityVerifier` certifies **feasibility +
optimality** — identical to the benchmark grader's predicate. It assigns
`Verified` only when the certificate re-checks as optimal; a feasible-but-
uncertified answer would receive `Derived`, never `Verified`. Alignment
confirmed by the outcome: 0 false certifications across 60 problems.

## 5. Validation Results (Task 5)

| Metric | Value |
|---|---|
| Verified-Correct Rate | **1.00** |
| False Certification Rate | **0.00** |
| Coverage (fraction labelled Verified) | 1.00 |
| **Coverage at Zero False Certification** | **1.00** |
| Every Verified answer has a rechecked certificate | **true** (60/60) |
| Trust labels | Verified 60, Derived 0, Heuristic 0, Open 0 |
| Formalization source | parser 60/60 (0 LLM fallback) |
| Mean solve time / cert-gen time | 76 µs / 67 µs |
| Peak RSS | 27.6 MB |

**Contrast with Intervention 2** (LLM candidate generation, same task):
0% Verified-Correct, 5% false certification → **100% Verified-Correct, 0%
false certification.** That before/after is the contract's central thesis
measured: trust comes from certification (deterministic solver + checkable
optimality certificate), not generation (LLM guessing).

## 6. Coverage vs False Certification Table

| System | Coverage (Verified) | False Certification | Verified-Correct |
|---|---|---|---|
| Intervention 2 (LLM attempter) | 5% (3/60, all wrong) | 5% | 0% |
| **Validation Phase 1 (solver + optimality cert)** | **100%** | **0%** | **100%** |

The Goodhart trap (answer Open to everything → 0 false-cert but useless) is
avoided: coverage is 100% *at* zero false certification, the frontier's
best-possible corner for this task.

## 7. Contract Compliance Audit

| Success criterion | Result |
|---|---|
| 1. Verified certifies exactly the frozen benchmark predicate | ✅ feasible+optimal == grade()'s predicate |
| 2. False Certification Rate = 0 | ✅ 0.00 |
| 3. At least one answer Verified-Correct | ✅ 60 |
| 4. Coverage reported alongside False Certification | ✅ |
| 5. Every Verified answer has an independently checkable certificate | ✅ 60/60 recheck, negative control passes |

**Honest boundaries (not hidden):**
- **Scope:** 100%/0% holds on the *native registered task*, where 1B
  formalization is 100% (all 60 via parser, 0 fallback). On unstructured/
  paraphrased inputs formalization degrades (measured: L3 88.9%), which
  could reintroduce false certification — the solver would faithfully
  certify the optimum of a *wrong* spec. This validates the contract on
  the bounded-optimization vertical with structured inputs, not
  universally.
- **Independence caveat:** `recheck_certificate` recomputes feasibility and
  score independently but re-uses the solver's `_search_optimum` for the
  optimality bound — so the recheck is not fully code-independent.
  Genuine independence is established by a *different* route: the solver's
  output matches the benchmark's independently-implemented ground-truth
  enumeration on 60/60. Contract Principle 10 (reproducible by an
  independent implementation) is satisfied via that agreement, not via the
  recheck alone. A second, distinct optimality checker would close this
  fully.
- **H1 remains retired here, not revived:** the solver is exact, so
  verifier-guided *retry* has no gap to fill on this vertical — consistent
  with the earlier finding that knapsack cannot test H1.

## 8. Decision

**KEEP.**

All five success criteria met. The locked contract produced its first
experimentally valid Verified-Correct result — in fact a saturating one
(100% at zero false certification) — with every Verified answer carrying a
re-checkable optimality certificate that provably rejects the exact
failure mode (feasible-but-suboptimal) that invalidated H1. Under the
Evidence Hierarchy, this advances the bounded-optimization vertical from
"Implementation" to a first **Validation** data point, bounded to
structured inputs.

Per the stop condition: not beginning H2/H3, not expanding scope.
