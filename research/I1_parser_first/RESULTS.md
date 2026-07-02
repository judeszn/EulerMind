# Intervention 1 — Parser-First Extraction: RESULTS

**Date:** 2026-07-02 · Same 60 `edge_ai_deployment` dev problems as the H0
baseline, same evaluator (`research/H0_formalization/metrics.py`,
additive-only changes — old baseline record remains valid and comparable).

## Comparison table

| Metric | Baseline (H0) | Intervention 1 | Δ |
|---|---|---|---|
| Spec present rate | 88.3% | **100%** | +11.7pts |
| Variable Extraction Accuracy | 83.2% | **100%** | +16.8pts |
| Numeric Extraction Accuracy | 72.3% | **100%** | +27.7pts |
| Field Association Accuracy | 93.1% | **100%** | +6.9pts |
| **Unit Normalization Accuracy** | **28.3%** | **100%** | **+71.7pts** |
| Constraint Extraction Accuracy | 66.7% | **100%** | +33.3pts |
| Overall Schema Accuracy | 74.0% | **100%** | +26.0pts |
| Fabricated (pooled count) | 112 | **0** | -112 |
| Missing models (pooled count) | 54 | **0** | -54 |
| Swapped (pooled count) | 29 | **0** | -29 |
| LLM fallback engaged | n/a (always LLM) | **0/60 (0%)** | — |

Fabrication by field (all zero): ram_gb 0/300, flops_g 0/300, accuracy
0/300, latency_ms 0/300.

## Which metrics improved

All of them, to the ceiling. Unit Normalization Accuracy — the worst
metric in the baseline and the specific, named target of this
intervention — improved the most in absolute terms (28.3% → 100%),
exactly matching the diagnosis: the RAM budget's MB→GB conversion is now
arithmetic (divide by 1024), not a model's guess.

## Which metrics did not improve

None regressed. But **this result validates less than "100%" suggests**,
and I want to be precise about the gap rather than oversell it:

- **The LLM fallback path was never exercised** (0/60). It's implemented
  and spliced correctly in code, but this run contains zero evidence it
  works in practice — the structure detector matched every single
  instance, so the fallback branch is untested, not proven.
- **This measures the benchmark's exact phrasing, which the parser was
  built to match.** The two budget regexes were written against
  `benchmark/generator/edge_ai.py`'s two known templates. A live judge
  typing the problem differently, or worded quantities ("about three
  quarters of a gigabyte"), would hit the untested fallback path, not
  this 100%. The digit-bearing caveat from the design review — parser
  owns digits, LLM owns words — still applies exactly as scoped; this
  result confirms the digit-bearing half works, not the whole system.
- Association Accuracy's 6.9pt gain is smaller than the others because it
  was already high in the baseline (93.1%) — consistent with the earlier
  finding that the LLM rarely confused *which* model a number belonged
  to; it more often fabricated or dropped values outright, which is
  exactly what the parser eliminates.

## Gate 2 evaluation

Stated interpretation (phrasing was ambiguous, resolved before running):
pass bar is the *easier* of the two stated conditions per metric.

- Unit Accuracy pass bar: min(28.3+15, 80) = 43.3%. **Measured: 100%. PASS**, decisively.
- Fabrication Rate pass bar: max(11.0×0.5, 5) = 5.5%. **Measured: 0%. PASS**, decisively.

Both conditions clear by a wide margin — not a borderline call.

## Decision

**KEEP.**

## Recommendation for next intervention (evidence-based, not executed)

Gate 2 passed emphatically, which under the frozen roadmap points toward
Intervention 2 ("Resume Formalizer"). But the ceiling result changes what
that step should mean: Intervention 1 didn't just clear the formalization
bottleneck for structured input, it eliminated it for this benchmark's
data entirely (0% fabrication, 0% missing, 0% unit error). The formalizer
component of the H0→H1/H3 dependency gate is now cleared — both H1 and H3
were blocked on this. Two candidate next steps, not both required:

1. **Validate the untested fallback path** before trusting it for live
   judging — construct a small set of deliberately unstructured/reworded
   instances (same content, prose phrasing, worded quantities) and
   confirm the LLM fallback + splice logic actually produces a usable
   spec, since this run gives zero evidence either way.
2. **Resume H1** (B2 vs blind retry vs guided retry) using
   `ParserFirstFormalizer` as the Formalizer stage — the confound H0
   existed to check is now removed for this domain's benchmark data, so
   H1's Δ Verified-Correct Rate would no longer be dominated by
   formalization noise.

Not started. Per the stop condition, waiting for further instruction.
