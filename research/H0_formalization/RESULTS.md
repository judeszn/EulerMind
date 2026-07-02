# H0 / Stage A — Formalization Accuracy: RESULTS

**Date:** 2026-07-02 · **Model:** `llama3.2:1b` (Ollama, temp 0)
**Scope:** Formalizer only — single `formalize()` call per problem, no
solving, no retry, no policy, no executor, no verifier.
**Sample:** all 60 `edge_ai_deployment` dev problems (30 clean + 30 messy,
dataset v1). No kernel/API/architecture files modified to produce this.

## Metrics

| Metric | Value |
|---|---|
| Spec present rate (parsed at all) | 88.3% |
| Variable Extraction Accuracy (model-name F1) | 83.2% |
| Numeric Extraction Accuracy | 72.3% |
| **Field Association Accuracy** | 93.1% (mean-of-problems); 96.7% pooled across all checked fields |
| **Unit Normalization Accuracy** | **28.3%** |
| Constraint Extraction Accuracy | 66.7% |
| Objective Extraction Accuracy | N/A — this domain's objective formula (0.7·acc + 0.3/latency) is fixed and stated identically in every instance; it is not a per-instance extracted field in the schema, so scoring it would fabricate a number for a metric that doesn't structurally apply here |
| **Overall Schema Accuracy** | 74.0% |

By variant: clean 74.7% vs messy 73.3% overall schema accuracy — messy's
lower spec-present rate (93.3% vs 83.3%, i.e. messy actually *parsed* more
often) is a modest reminder that distractor text and the unit-conversion
challenge don't destroy the formalizer outright; the damage is concentrated
in specific fields, not spread evenly.

## Error taxonomy (pooled across all 60 problems, 4 numeric fields × up to
5 models each)

| Category | Count | Share |
|---|---|---|
| Correct | 843 | 82.9% |
| Fabricated (matches no true value anywhere) | 112 | 11.0% |
| Missing (model never extracted) | 54 | 5.3% |
| Swapped (correct value, wrong model) | 29 | 2.9% |

## Dominant failure modes, in order of measured impact

1. **Unit normalization (28.3% accuracy) is the single worst metric in
   the report**, confirming and precisely quantifying what the earlier
   single-instance run found anecdotally (RAM budget extracted as `1`
   instead of `3.7`). This is a narrow, specific weakness — three other
   constraint fields (FLOPS budget, latency budget, accuracy threshold)
   are not measured separately here but were correct in the earlier
   single-instance inspection, and constraint_extraction_accuracy (66.7%)
   being well above unit_normalization_accuracy (28.3%) confirms the
   damage is concentrated in the MB→GB conversion specifically, not
   spread across all constraint fields evenly.
2. **Fabrication (112) and missing models (54) dominate over swaps (29)
   by roughly 6:1.** This refines the earlier read from a single
   instance ("the model hallucinated the catalog") into something more
   precise: the model is not usually *confusing* which model owns which
   number (Field Association Accuracy is high — 93–97%). It is more often
   *inventing* a plausible-looking number that corresponds to nothing in
   the source, or *dropping* a model from the catalog entirely.
3. Field Association Accuracy (93–97%) is the strongest metric in the
   report. When a number is right or wrong, it's rarely because it was
   attached to the wrong entity.

## Why this matters for the frozen H0→H1/H3 sequencing

Fabrication, missing-models, and unit-conversion failures are exactly the
class of error the already-frozen Stage B principle ("deterministic
extraction wherever structure is explicit, LLM only for semantic content")
targets directly — the model catalog is a consistently-formatted bulleted
list in every instance, and the RAM budget is an explicit digit+unit
token in the text. A parser reading literal digits off structured text
cannot fabricate, cannot drop an entry it's scanning line-by-line, and
converts units by arithmetic, not by guessing. The much smaller residual
— genuine field-association errors (2.9–6.9% depending on how it's
counted) — is exactly the class of error the design review already
assigned to H3 (verification-guided formalization checking) as the
*remaining* problem after Stage B removes the mechanical one. The
measured data doesn't just fail to contradict that sequencing — it
confirms the ordering was right, and gives it a concrete priority: fix
unit conversion first (worst metric), fix catalog-line parsing second
(addresses both fabrication and missing-models, likely the same root
cause — the model free-associating instead of reading line by line).

## Recommended threshold (proposed here, not previously specified)

The original instruction did not supply a numeric target for resuming
H1/H3. Given this data: **overall_schema_accuracy ≥ 90% and
unit_normalization_accuracy ≥ 90%** as the bar before H1/H3 measurements
are trusted. Rationale: deterministic parsing of digit-bearing structured
text should approach ~100% reliability on the fields it covers (modulo
phrasing edge cases), so 90% is a conservative, achievable target for
Stage B to clear — not an arbitrary round number.

## Decision

**PIVOT** — to Stage B (parser-first extraction for the model catalog and
the RAM budget figure), exactly as already specified in the frozen
design. This is not a change of direction; it's confirmation, with
numbers, that the already-planned next step targets the actual measured
problem. Not KEEP (74% overall / 28% on the worst metric is not reliable
enough to trust H1/H3 measurements built on top of it — this is precisely
the risk H0 existed to check). Not DELETE (no evidence the domain or
approach is unsalvageable — the error is concentrated exactly where a
already-designed, cheap fix applies).

Per the reporting constraint: **Stage B is not started in this turn.**
