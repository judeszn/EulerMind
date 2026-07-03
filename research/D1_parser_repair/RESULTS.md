# Delta Intervention D1 — Parser Repair: RESULTS

**Date:** 2026-07-03 · engineering intervention (not a hypothesis) ·
fully offline, deterministic. **Outcome: SUCCESS — defect eliminated,
all regression controls pass bit-exact, Gamma outputs unchanged.**

## 1. Root-cause confirmation (Interpretation Order step 1)

Re-confirmed before touching anything: `_looks_like_catalog_line()`
returned `True` on the exact L3 `"Constraints: total memory must stay
under 3.7GB..."` paragraph, and the before-repair snapshot reproduced the
full registered picture — **30/30 L3 instances fabricated a `Constraints`
pseudo-model AND 30/30 had missing models**, while native/L1/L2 were
100% clean (`snapshot_before.json`).

## 2. The repair (minimal, two entry points of one flaw)

The locked root cause — catalog extraction consuming budget/requirement
text — manifests through two entry points, both repaired; nothing else
touched:

1. **`_looks_like_catalog_line()`** now excludes budget/requirement text
   via a new direct helper `_is_budget_or_requirement_text()`, defined as
   membership in the regions the *existing* `extract_budgets()`
   (`_BUDGET_CUE`) and `extract_threshold()` (`_THRESHOLD_PATTERNS`)
   already own. No new vocabulary was invented — the fix is "catalog
   extraction must not consume the regions the other two extractors own,"
   using their own frozen region definitions. This eliminates the
   fabricated pseudo-model.
2. **`_all_catalog_segments()`** (the direct helper implementing that
   parser logic): (a) its sentence and clause paths previously duplicated
   the catalog-line check inline *without* going through
   `_looks_like_catalog_line()` — all paths now gate through the named
   (now guarded) function; (b) the `;`-clause split previously operated
   across the whole document, so a clause could swallow an adjacent table
   or the budget paragraph, poisoning its own field resolution (multiple
   GB/GFLOPS/ms values → the never-guess rule correctly refuses → the
   aside model silently dropped). Clause splitting is now scoped per
   line — a clause boundary cannot span a line break. This recovers the
   dropped models.

**Diagnostic refinement, disclosed:** the locked root cause attributed
both symptoms to the misclassification. Precisely: the misclassification
alone caused the *fabrication*; the *omissions* were caused by the
document-wide clause contamination (same design flaw — catalog
segmentation ingesting non-catalog regions — different entry point).
Repairing only the named function would have contradicted the locked
diagnosis's claim that this defect explains the omissions (and failed
Success Criterion 2), so the direct-helper repair was required — per the
task's own "unless the repair contradicts this diagnosis" clause and
within the permitted scope ("direct helper functions required by that
parser logic"). No new failure mode appeared: both symptoms were inside
the locked 30/30 reproduction.

## 3. Controls (Interpretation Order steps 3–5)

| Control | Requirement | Result |
|---|---|---|
| Positive — previously-failing L3 cases | parse correctly | **30/30 exact name match** (was 0/30); schema accuracy 0.8889 → **1.0**; fabricated 30 → **0**; missing 30 → **0** |
| Negative — native catalog parsing | unchanged | **60/60 specs byte-identical** before vs after |
| Negative — paraphrase L1/L2 | unchanged | **30/30 + 30/30 specs byte-identical** |
| Regression — native benchmark vs frozen Gamma outputs | identical | **60/60** — post-repair pipeline reproduces `research/G3_cert_independence/report_20260703-124811.json` exactly (primary accept, independent accept, independent optimum, per problem) |
| Parser unit tests | all pass | **9/9** (`test_parser.py`; the 4 positive-control tests failed before the repair, demonstrating they bind) |
| Selftest | passes completely | **pass** ("the ruler is calibrated") |

Precisely the defect population changed and nothing else: L3 specs
changed 30/30 (every instance had the defect); native/L1/L2 changed 0/120.

## 4. Success / failure criteria

All 8 success criteria met: (1) `Constraints` pseudo-model eliminated;
(2) all legitimate models extracted (30/30 exact, correct values —
spot-asserted in unit tests); (3) L3 passes structural validation
(30/30 exact name sets, schema 1.0); (4) native behaviour byte-identical;
(5) Gamma results unchanged (60/60 vs frozen report); (6) unit tests
9/9; (7) selftest passes; (8) this regression report. No failure
criterion triggered: native accuracy did not decrease (identical), no
Gamma result changed, no *new* failure mode appeared (§2 refinement is
inside the locked reproduction, not a new mode), fabrication eliminated.

## 5. Evidence classification

Internal reproduction, deterministic (pure parser, no stochastic
component; snapshots and unit tests bit-stable on rerun). Scope: the
four measured splits (native dev n=60, paraphrase L1/L2/L3 n=30 each) —
all template-generated; the standing I1b caveat applies (gains on
template-generated text are a lower bound on, not proof of,
real-phrasing robustness).

## 6. Scientific conclusion

The deterministic parser defect found by Delta H3-1 is repaired at its
root, with bit-exact non-regression demonstrated on every previously
validated behaviour and zero change to any Gamma output. The L3
paraphrase split now formalizes at 100% schema accuracy with zero
fabrication. Downstream H3 implications are **not** interpreted here,
per the registered Interpretation Order ("Do not interpret downstream
H3 implications") — noting only the fact that H3's blocking defect no
longer exists; whether/how to re-run H3 is a separate registration
decision.

## Stopping Reason

Stopped after evidence classification per the registered Stop Condition.
H3 NOT re-run. H4 NOT begun. No architecture changes proposed. Awaiting
scientific review.
