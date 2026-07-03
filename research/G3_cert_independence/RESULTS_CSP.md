# Gamma+2 — Certificate Independence, CSP vertical (H-Independence-CSP): RESULTS

**Date:** 2026-07-03 · `constraint_csp` (5 engineers × 7 projects, P(7,5)=2520
permutation search space), 52 dev certificates (42 SAT, 10 UNSAT) · fully
offline. CSP analogue of the completed edge_ai Gamma+1 experiment.
Registered task: upgrade CSP Certificate Independence from **Partial** to
Supported or Rejected by evidence.

## Registered Configuration

| Field | Value |
|---|---|
| Vertical | constraint_csp (5 engineers into 7 projects, 4 constraint kinds) |
| Dataset | `benchmark/datasets/v1`, dev split, 52 problems (42 SAT / 10 UNSAT) |
| Formalizer | CSPFormalizer (parser-first template matching, 0 LLM fallback) |
| Solver / primary checker | `kernel/csp_solver.py` — generate-all-permutations-then-filter; `recheck_certificate` calls the same `_check()` / `_enumerate_solutions()` `solve()` depends on |
| Independent checker | `research/G3_cert_independence/independent_csp_checker.py` — backtracking DFS with incremental per-step pruning; separately-written full-assignment evaluator; imports nothing from `kernel.csp_solver` |
| Certificate | unchanged (`make_certificate`, both types: satisfying-assignment and minimal-conflict) |

## 1. Independence design review

The gap: production `recheck_certificate` calls `_check()` and
`_enumerate_solutions()` — the exact functions `solve()` uses to produce
the answer. A bug there (e.g. a constraint mis-evaluated, or a pruning
error in `_minimal_conflict`) would fool the solver and its own checker
identically.

The independent checker differs on **two independent axes**, not one:
- **Search algorithm**: the solver generates all permutations and filters;
  the independent checker does backtracking DFS with incremental
  per-engineer pruning — a different algorithm over the same search space
  (all injective engineer→project maps), not just a different function.
- **Constraint evaluator**: separately written (`_full_satisfies`, a
  positive "all constraints hold" formulation) vs the solver's negative
  "return False on first violation" loop.

CSP has **two certificate types** (SAT: satisfying assignment; UNSAT:
minimal conflict + exhaustion), unlike edge_ai's single type — both are
exercised in this experiment (42 SAT, 10 UNSAT certificates) and both are
covered by dedicated positive and negative controls.

**Third-oracle cross-check**: for every certificate, an independent FULL
enumeration (no limit, same backtracking search) counts all solutions to
the certified spec and is compared against the benchmark dataset's own
precomputed `ground_truth.solution_count` — a value computed independently
at dataset-build time, by neither the solver nor the independent checker.

## 2–4. Controls

| Control | Type | Result |
|---|---|---|
| Positive — accepts a true SAT assignment | SAT | **accept** ✓ |
| Positive — accepts a true UNSAT minimal-conflict certificate | UNSAT | **accept** ✓ |
| Negative — assignment violates a forbidden constraint | SAT | **reject** ✓ |
| Negative — claimed conflict set is actually satisfiable (empty set) | UNSAT | **reject** ✓ |
| Negative — claimed conflict is the full constraint list, not minimal | UNSAT | **reject** ✓ |

## 5. Agreement matrix

| Comparison | Agree / total |
|---|---|
| Primary (shared search) vs Independent (backtracking, separate evaluator) | **52 / 52** |
| Independent full-enumeration count vs benchmark ground-truth `solution_count` | **52 / 52** |
| SAT certificates | 42 / 42 |
| UNSAT certificates | 10 / 10 |
| Disagreements | **0** |

## 6. False-certification report

**0** false certifications under the independent check (every certificate
the independent checker accepted also matched the benchmark's
independently precomputed ground truth — SAT solution count or the UNSAT
zero-count).

## 7. Evidence classification

Internal reproduction, deterministic (parser-first formalizer + exhaustive
search — no stochastic component; bit-identical on rerun). Scope:
constraint_csp vertical, dev split, 52 problems (both SAT and UNSAT
certificate types).

## 8. Success / failure criteria

All five success criteria met: (1) no shared search implementation —
different algorithm (backtracking vs generate-then-filter) *and* a
separately-written evaluator; (2) positive controls pass, both certificate
types; (3) negative controls pass, covering constraint violation,
false-conflict, and non-minimality; (4) all 52 previously-Verified
certificates rechecked; (5) accept/reject decisions match exactly (52/52).
No failure criterion triggered: no shared logic, no disagreement, false
certification stayed 0, no corrupted certificate accepted.

## 9. Decision — KEEP

**Certificate Independence — constraint_csp: Partial → Supported, within
tested scope.** A checker sharing no search algorithm and no evaluator
code with the solver reaches identical decisions on all 52 certificates of
both types, and agrees with a third independent enumeration (the
benchmark's precomputed ground truth). Combined with Gamma+1 (edge_ai),
both validated verticals now carry Supported certificate correctness *and*
Supported certificate independence.

### Honest scope (Evidence Escalation Rule)

- **Implementation-independent (different algorithm + different
  evaluator), not paradigm-independent.** No SAT/CSP solver (e.g.
  OR-Tools/CP-SAT) was used as a third paradigm; both checkers perform
  exhaustive search by construction over a small (≤2520-permutation) space,
  which is already complete and exact for this problem size — a different
  paradigm would add confidence about implementation bugs beyond what two
  algorithmically-distinct exhaustive searches already provide, but was
  judged unnecessary at this scale. Scoped accordingly, matching the
  precedent set in Gamma+1's edge_ai RESULTS.
- Native (parser-matched) format, dev split, 52 problems. Holdout untouched.
- Minimality checking (for UNSAT certificates) inherits the independent
  search's completeness argument but was only exercised on the 10 UNSAT
  dev problems' actual minimal-conflict sizes (up to 7 constraints);
  larger conflict sets are untested.

## Stopping Reason

Success criterion reached — independence upgraded to Supported for the CSP
vertical, all controls passed (both certificate types), evidence
classified. Per the Stop Condition: no new hypothesis, no H2/H3, no UI, no
architecture change.
