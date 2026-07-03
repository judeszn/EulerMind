# H3 — Formalization Checking: RESULTS

**Date:** 2026-07-03 · `edge_ai_deployment`, `research/I1_validation/level3.jsonl`
(frozen, 30 instances, "mixed"/adversarial paraphrase level) · fully
offline. **Outcome: STOPPED — precondition technically satisfied, but the
measurement revealed a systematic defect that makes this split unable to
validly test H3's causal claim. A previously-undiscovered, severe
formalization bug was found as a side effect. No verdict on H3 is
recorded; the experiment is Completed / Inconclusive, not Supported or
Rejected.**

## Registered Configuration

| Field | Value |
|---|---|
| Dataset | `research/I1_validation/level3.jsonl` (frozen; not modified; not regenerated) |
| Baseline | `StructuredFormalizer` (production, unchecked) |
| Experimental | `CheckedStructuredFormalizer` (independent structural cross-check; withholds spec on disagreement) |
| Pipeline (both arms, unmodified) | `kernel.loop.run_kernel` — `SolverAttempter` → `DeterministicExecutor` → `OptimalityVerifier`, `policy=None`, `Budget(attempts=1)` |
| Metric | Verified-wrong rate (`trust_label=="Verified"` AND `benchmark.metrics.grade()==False`) |

## 1. Required Precondition

**Formalization error rate: 30/30 = 100%** (`schema_accuracy < 0.999` on
every instance, via the existing, unmodified `research/H0_formalization/metrics.py::score()`).
Precondition technically satisfied (>0) — but this number is far higher
than the previously-published 88.9% mean schema accuracy for this exact
split (`research/I1b_structure/RESULTS.md`), which needed investigation
before proceeding.

## 2. What the 100% actually is — a systematic defect, not general noise

Every one of the 30 instances has the **same two-part defect**: exactly 2
of the 5 true models are missing, **and** the extractor fabricates a
spurious sixth "model" literally named **`Constraints`**. Verified
directly (not sampled): 30/30 instances show a `Constraints` key in
`spec["models"]`.

**Root cause, diagnosed precisely:** `kernel/edge_ai_extractors.py`'s
`_looks_like_catalog_line()` misclassifies the level-3 template's
labeled constraints paragraph (`"Constraints: total memory must stay
under 3.7GB..."`) as a catalog (per-model) segment — confirmed directly:
`_looks_like_catalog_line()` returns `True` on that exact sentence. The
value-semantic extractor then takes the leading capitalized token
("Constraints") as a model name and binds whatever RAM/GFLOPS/accuracy/
latency-shaped numbers it finds nearby (the budget and threshold values)
to it as if they were one model's specs. This is L3-structure-specific:
L1's "Budget limits: ..." and L2's prose-embedded budget phrasing do not
trigger it (both are 100% schema accuracy under 1B per
`research/I1b_structure/RESULTS.md`) — only L3's literally-labeled
"Constraints:" paragraph does.

**Why the historical 88.9% number never caught this:** `score()` computes
field-level accuracy *only for ground-truth model names* — it has no
check for extra, non-ground-truth entries in the extracted spec, so a
fabricated `Constraints` pseudo-model is invisible to it by construction.
The 88.9% figure is real and correctly computed for what it measures
(per-field accuracy against known models); it was never validated against
end-to-end Verified-correctness, because L3 was never run through
`solve_optimal` → `OptimalityVerifier` → `grade()` before this experiment.
**This is the first time this split's downstream correctness was
measured**, and Gamma's own certification claims are unaffected — Gamma
and Gamma+1 both used the native (non-paraphrased) dev set, which does
not exhibit this bug.

## 3. Why the main comparison is not a valid H3 test on this split

| | Baseline (unchecked) | Experimental (checked) |
|---|---|---|
| Verified rate | 100% (30/30) | 0% (0/30) |
| Verified-correct rate | **0%** | 0% |
| Verified-wrong rate | **100%** (30/30) | **0%** |
| Independent-checker disagreements (either arm) | 0 | 0 |

McNemar on verified-wrong: p=0.0, "experimental better." McNemar on
overall correctness: p=1.0, "indistinguishable" (0% vs 0%).

**This is not evidence for H3.** The experimental arm's 0% verified-wrong
is achieved by withholding *every single spec* — a defective input set,
not selective error-catching. H3's actual claim is that checking reduces
wrongness *while preserving correct cases*; this split has **zero correct
cases in the baseline to preserve**, so the "does not cut verified-correct
rate" criterion is satisfied only vacuously (0% cannot go lower), and the
comparison cannot distinguish "the check works" from "the check refuses
everything." The positive control (no false flags on error-free instances)
is likewise vacuous — there are no error-free instances in this split to
test it against.

What *is* validly demonstrated: the independent structural counter itself
is accurate — it matches the true model count on all 30 instances
(verified against `ground_truth`, used only as a calibration oracle, not
fed into the check's runtime logic) — and certificate correctness/
independence are unaffected in both arms (0 disagreements), consistent
with the established Trust Boundary: a "Verified" label here is
correct *relative to the (defective) formalized spec* — the defect is a
formalization-fidelity problem, a different, already-documented property
from certificate correctness, not a regression of Gamma's results.

## 4. New finding, logged (not fixed — Frozen Constraints held)

**A previously-undiscovered, systematic defect in `kernel/edge_ai_extractors.py`:**
on `constraint_csp`-unrelated `edge_ai_deployment` "mixed"-paraphrase
(L3-style) input containing a paragraph literally labeled `"Constraints:"`,
the catalog-segment classifier fabricates a spurious model from the
budget/threshold sentence, on top of independently omitting ~2 real
models per instance (the previously-known residual). Reproduced
100% (30/30), deterministic, root-caused to a specific function. **Not
fixed here** — `kernel/edge_ai_extractors.py` is a Frozen Constraint
under this registered task (no Formalizer changes). Logged as a concrete,
actionable item for a properly-scoped future registered task.

## 5. Deliverables

1. Registered experiment — this document.
2. Base-rate report — §1 (100%, technically nonzero, but see §2 for why the number needed investigation rather than being taken at face value).
3. Controls — run, but both are vacuous on this split (§3); the independent counter's own accuracy (30/30 vs ground-truth-oracle) is the one non-vacuous validation obtained.
4. Statistical analysis — §3 (reported; not interpreted as an H3 verdict, per §3's reasoning).
5. Evidence classification — Internal reproduction, deterministic (parser-first, no stochastic component); scope: this exact split only.
6. Scientific conclusion — **H3: no verdict.** Neither Supported nor Rejected. The registered split cannot test the hypothesis validly (degenerate baseline). A new, separately-actionable defect was found and logged.
7. `docs/SCIENTIFIC_STATE.md` updated accordingly (not a governance edit).

## Interpretation Order (as required)

1. Intervention opportunity exists — yes, but not in the anticipated form (§1-2).
2. Intervention executed — yes, both arms ran to completion.
3. Certificate correctness — unaffected (0 disagreements either arm).
4. Certificate independence — unaffected (independent recheck used throughout, 0 disagreements).
5. Statistical outcome — computed (§3) but **not interpreted as an H3 verdict**, because step 1's "opportunity" turned out to be a degenerate, not representative, condition — the same discipline that produced the H1a/H1b decomposition and the Gamma-2 mechanism-gate finding: a valid-looking precondition pass does not by itself certify the comparison that follows is meaningful.

## Stop Condition

Stopped per the registered Stop Condition after evidence classification.
No H4, no H5, no further Delta experiment started. Awaiting review: the
newly-discovered `Constraints`-fabrication defect is a candidate for a
follow-up registered task (fix + re-test), separate from this one.
