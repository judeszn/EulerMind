# Dataset changelog

Datasets are **immutable**: never regenerate in place. A new generation is a
new versioned directory (v1/, v2/, ...) with its own entry here, and old
versions are kept so every historical report stays reproducible.

## v0 — 2026-07-02

- 240 problems: 40 base instances × 3 categories × (clean + messy).
- Categories: optimization_lp, calculus_poly, constraint_csp.
- 15% of CSP instances unsatisfiable, with minimal conflict sets.
- Split: deterministic sha256(base_id), 25% holdout.
- Generator seeds 0–39, `--start-seed 0`.
- Known limitation: 40 bases/category is development-scale; kill decisions
  need a larger build (±7pt noise floor at n≈100 pairs). Still open.

## v1 — 2026-07-02

- Added `edge_ai_deployment`: an integer knapsack (5 model types, integer
  deploy-counts, RAM/FLOPS/latency budgets, "at least one high-accuracy
  model" constraint). Ground truth by brute-force enumeration, stdlib
  only. Adopted from a proposed 5-family "Edge AI Optimization" pitch —
  this is the one family built; the rest were rejected or already covered
  (see research/edge_ai_family_decision.md).
- Everything else unchanged from v0: same lp/calculus/csp generators,
  same 40 bases/category, same split logic. Per-category count was
  deliberately left at 40 here too, so this version isolates exactly one
  change (the new category) rather than conflating it with the still-open
  sample-size limitation above.
- 320 problems total (240 from v0's three categories + 80 new).
