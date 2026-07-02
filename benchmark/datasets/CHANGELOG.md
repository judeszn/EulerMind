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
  need v1 with ≥100 bases/category (±7pt noise floor at n≈100 pairs).
