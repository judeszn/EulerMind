# Gamma+1 — Certificate Independence (H-Independence): RESULTS

**Date:** 2026-07-03 · `edge_ai_deployment` (bounded optimization), 60 dev
certificates · fully offline. Registered task: upgrade Certificate
Independence from **Partial** to Supported or Rejected by evidence.

## Registered Configuration

| Field | Value |
|---|---|
| Vertical | edge_ai_deployment (bounded integer knapsack) |
| Dataset | `benchmark/datasets/v1`, dev split, 60 problems |
| Formalizer | StructuredFormalizer (parser, 0 LLM fallback on native format) |
| Solver / primary checker | `kernel/edge_ai_solver.py` — recursive DFS + monotone pruning; `recheck_certificate` shares that search |
| Independent checker | `research/G3_cert_independence/independent_checker.py` — brute-force `itertools.product`, no pruning, imports nothing from the solver's search |
| Certificate | unchanged (`make_certificate`) |

## 1. Independence design review

The gap: the production `recheck_certificate` calls `_search_optimum`, the
*same* pruned-DFS function the solver uses to produce the answer. A bug in
that shared search (e.g. an over-aggressive pruning cut) would make the
solver miss a better point AND the checker fail to notice. Independence
requires a checker whose optimum-finding shares no code with the solver's.

The checker built here establishes the optimum by **brute-force
enumeration with no pruning** — the strongest possible optimality oracle
for a bounded problem, because there is no pruning logic that could be
wrong. It also recomputes the objective from raw accuracy/latency (does
not trust the spec's precomputed score field) and recomputes feasibility.
Completeness: per-model bounds `floor(min_budget/cost)` make the enumerated
box a superset of the feasible region, so every feasible point is visited.

**Three independent search implementations now exist and were compared:**
(1) the solver's pruned DFS, (2) this unpruned brute force, (3) the
benchmark generator's separate ground-truth enumeration.

## 2–4. Controls

| Control | Result |
|---|---|
| Positive — independent checker accepts the true optimum | **accept** ✓ |
| Negative — inflated score | **reject** ✓ |
| Negative — infeasible counts | **reject** ✓ |
| Negative — feasible-but-suboptimal | **reject** ✓ |

## 5. Agreement matrix

| Comparison | Agree / total |
|---|---|
| Primary (pruned DFS) vs Independent (brute force) | **60 / 60** |
| Independent optimum vs benchmark ground-truth score | **60 / 60** |
| Disagreements | **0** |

## 6. False-certification report

**0** false certifications under the independent check (every certificate
the independent checker accepted also matched the benchmark ground truth).

## 7. Evidence classification

Internal reproduction, deterministic (parser formalizer + exhaustive
search — no stochastic component; bit-identical on rerun). Scope: bounded
optimization vertical, native format, dev split.

## 8. Success / failure criteria

All five success criteria met: (1) no shared search implementation —
confirmed by construction (brute force, no import of the solver's search);
(2) positive controls pass; (3) negative controls pass; (4) all 60
previously-Verified certificates rechecked; (5) accept/reject decisions
match exactly (60/60). No failure criterion triggered: no shared logic, no
disagreement, false certification stayed 0, no corrupted certificate
accepted.

## 9. Decision — KEEP

**Certificate Independence: Partial → Supported, for the bounded
optimization vertical, within tested scope.** A checker sharing no search
logic with the solver reaches identical decisions on all 60 certificates,
and agrees with a third independent enumeration (the benchmark ground
truth). The project's strongest claim is now stronger: certificate
correctness holds under an independent verifier, not only the solver's own.

### Honest scope (Evidence Escalation Rule)

- **This vertical only.** The CSP vertical's `recheck_certificate` still
  shares logic with its `solve()`; CSP certificate independence remains
  **Partial** — not addressed by this experiment.
- **Implementation- and oracle-independent, not paradigm-independent.** The
  independent checker uses a different implementation of the same algorithm
  *class* (exhaustive enumeration), plus a third-oracle cross-check. It is
  not a different paradigm (e.g. an ILP/OR-Tools solver). For a bounded
  problem, unpruned brute force is already the strongest optimality oracle,
  so paradigm-independence would add little here — but the claim is scoped
  accordingly.
- Native format, dev split, 60 problems. Holdout untouched.

## Stopping Reason

Success criterion reached — independence upgraded to Supported for this
vertical, all controls passed, evidence classified. No new hypothesis, no
H2/H3, no CSP extension (that would be a separate registered task).
