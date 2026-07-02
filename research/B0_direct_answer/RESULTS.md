# B0 — naive direct answer: RESULTS

**Date:** 2026-07-02 · **Model:** qwen2.5:1.5b (Ollama, temp 0, JSON-forced)
**Subset:** 30 dev problems (5 bases × 3 categories × clean+messy)

## Numbers

| Metric | Value |
|---|---|
| Correct rate | **6.7%** (2/30) |
| Verified-correct rate | 0.0% (no verifier exists in B0, by construction) |
| optimization_lp | 0/10 |
| calculus_poly | 0/10 |
| constraint_csp | 2/10 |
| Clean vs messy (paired) | 13.3% vs **0.0%** (delta 13.3pts) |
| Mean latency | 1.13 s/problem |

## Reading

- **This is the floor.** A target-class 1.5B model answering directly, with
  reasoning suppressed (JSON-forced output → no chain of thought), solves
  almost nothing. Every point above 6.7% that later systems score is
  measured, attributable value.
- **The formalization-robustness signal already works**: messy variants
  score 0 even where clean variants score. The messy delta exists at the
  floor, as predicted.
- Known caveats: general model (not Qwen2.5-Math); JSON-forcing suppresses
  CoT — both deliberate. B0 measures "no reasoning at all," not "the model's
  best effort." B1 is the model's best unaided effort.

## Decision (48-hour rule)

**KEEP — as the permanent reference floor.** B0 is a baseline, not a
feature; it is rerun whenever the dataset or model changes.

## Next rungs (in order)

1. **B1 — CoT then answer**: same model, reason first, JSON last. The
   model's best unaided score.
2. **B2 — tool loop, blind retry**: kernel loop + SymPy/Z3 executor,
   resample on failure. The H1 control arm.
3. **B3 — verifier feedback (H1 treatment)**: failure signals in context.
   B3 vs B2, paired McNemar, is the bet.
