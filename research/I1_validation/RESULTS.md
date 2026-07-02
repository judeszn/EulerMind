# Intervention 1 — Validation Under Controlled Perturbation: RESULTS

**Date:** 2026-07-02 · 30 unique `edge_ai_deployment` base instances (deduped
from 60 — see bug note below), rendered at 3 paraphrase levels (90 total),
same ground truth as the original benchmark, only natural-language
expression changed. `ParserFirstFormalizer` run **unchanged** — nothing
in `kernel/edge_ai_parser.py` was modified for this validation.

## Bug found and fixed in the validation harness itself (disclosed, not a
parser/kernel issue)

`edge_ai_deployment`'s 60 dev rows are 30 unique instances × clean/messy
*text* variants sharing one `ground_truth`. Paraphrase rendering depends
only on `ground_truth` (by design — guarantees zero numeric drift), so
generating from all 60 rows silently produced 30 duplicate-id pairs per
level. Fixed in `research/I1_validation/generate.py` by deduplicating to
one representative per `base_id` before rendering. 30 unique instances
per level (90 total) is the honest, correct count — not 60.

## Comparison table

| Metric | Baseline (H0) | Intervention 1 (own format) | Validation L1 (format) | Validation L2 (prose) | Validation L3 (mixed) |
|---|---|---|---|---|---|
| Overall Schema Accuracy | 74.0% | 100% | 86.0% | 93.7%* | **52.8%** |
| Unit Normalization Accuracy | 28.3% | 100% | 80.0% | 63.3% | 3.3%** |
| Variable Extraction Accuracy | 83.2% | 100% | 88.9% | 96.3% | 42.1%** |
| Field Association Accuracy | 93.1% | 100% | 94.4% | 98.6% | 99.6% |
| Parser Success Rate | n/a | 100% | **0%** | **0%** | **0%** |
| LLM Fallback Invocation Rate | 100% (always LLM) | 0% | **100%** | **100%** | **100%** |
| Structure Detector Accuracy | n/a | n/a (no fallback cases) | n/a (no parser cases) | n/a | n/a |
| n (unique instances) | 60 | 60 | 30 | 30 | 30 |

\* Level 2's overall figure looks best of the three validation levels —
consistent with it being closest in spirit to the original messy variant
(distractor-laden prose), which the LLM fallback (unmodified from
baseline) was already reasonably competent at.
\** See the Level 3 deep-dive below — this number is driven almost
entirely by one specific, precisely diagnosed mechanism, not general
LLM weakness.

Structure Detector Accuracy is reported `n/a` because I defined it as a
false-positive check *among parser-routed cases* (did trusting the
parser's match turn out correct) — with 0% parser routing across all
three levels, there are no such cases to evaluate. This itself is the
finding: the detector never routed anything to the parser on paraphrased
input, so its accuracy on that population is undefined, not good or bad.

## Parser Success Rate / LLM Fallback Usage

**Parser Success Rate: 0% on all three levels, including Level 1
("formatting changes only").** `MODEL_LINE_RE` and the budget regexes
require the literal phrasing `GB RAM,` / `GFLOPS,` / `accuracy=` /
`latency=...ms` in that exact sequence. None of the Level 1 renderers
(markdown table, semicolon-separated bullets, pipe-separated bullets) use
that literal sequence, so **the parser fails even on modest formatting
variation of numerically identical information** — this is not a
semantic-understanding gap, it's a literal-string-matching gap.

**LLM Fallback Invocation Rate: 100% on all three levels.** The fallback
engaged correctly every time it was needed — it never silently failed to
trigger, and the splice logic (parser-found fields, if any, overwrite the
LLM's guess) executed without error throughout.

## Root cause, precisely diagnosed (Level 3 deep-dive)

Level 3's Overall Schema Accuracy (52.8%) and Variable Extraction Accuracy
(42.1%) are dramatically worse than Levels 1–2. Directly tested on a
10-problem sample by tracking which true model names came from the
table half of the text versus the prose-embedded half (`research/I1_validation/paraphrase.py`'s `make_level3` deliberately
splits the catalog this way):

```
table-listed models:   found 13/20 (65%)
prose-embedded models: found  0/30 (0%)  <- every single one dropped
```

**The LLM systematically drops catalog entries stated as incidental
prose asides** ("note: X also exists as an option, needing...") even
though the numbers are fully present as digits in the text. It does not
partially extract them or fabricate wrong values for them — it drops
them entirely, treating them as distractor-like content rather than
catalog data. This is a distinct, more severe failure mode than anything
seen in the H0 baseline or Levels 1–2, and it explains why Level 3's
`missing_models` share (109 of 273 checks, ~40%) is roughly 8× the H0
baseline's missing-model share (5.3%).

## Error breakdown by component (all three levels combined)

| Component | Verdict | Evidence |
|---|---|---|
| **Structure Detector** | Correct within its vocabulary, too narrow in coverage | Never produced a false positive (0 parser routes attempted on any paraphrase — it never claimed success on text it couldn't actually parse). But it also never recognized any of the 90 paraphrased instances as "structured," including format changes a human would consider trivially equivalent (bullets → semicolons, bullets → pipe-separated). Detection logic is sound; pattern vocabulary is narrow. |
| **Parser** | No bugs found | 0 cases were ever routed to it, so there is no evidence of correct *or* incorrect parser behavior on this validation set — only that it was never given the chance. |
| **LLM Fallback** | Engaged correctly, quality varies sharply by presentation | Never failed to trigger. Accuracy on Level 1/2 (86–94%) is roughly in line with or better than the H0 baseline (74%). Accuracy on Level 3 (52.8%) is substantially worse, attributable almost entirely to the prose-embedded-catalog-entry drop pattern above, not to numeric fabrication (fabrication counts stayed low across all levels: 22, 17, 9). |

## Failure analysis (grouped by root-cause pattern — 74 individual failing
instances across 90 total share one of two patterns; listing each
separately would not add information)

| Pattern | Levels affected | Component | Root cause | Suggested fix (not applied) |
|---|---|---|---|---|
| Regex literal-phrasing mismatch → correct fallback → residual LLM imperfection (baseline-level, 74–94% typical) | L1, L2, and the table-half of L3 | Structure Detector (routing) + LLM Fallback (residual accuracy) | Detector's known-pattern vocabulary is exactly one phrasing; any lexical variation (even bullets→semicolons) fails the match and correctly falls through, after which the fallback's accuracy is whatever the unmodified `LLMFormalizer` already measured in H0 | Broaden the regex vocabulary (multiple known separators/orderings) to reduce fallback reliance, OR accept the fallback rate and improve the LLM prompt specifically — both out of scope for this validation |
| Prose-embedded catalog entries dropped entirely (severe, L3-specific) | L3 only | LLM Fallback | The LLM treats catalog data phrased as an incidental aside as non-essential/distractor-like content and omits it, rather than partially extracting or fabricating a value for it | Recognize this as a distinct presentation-sensitivity failure, not a general accuracy problem — a targeted prompt instruction ("extract every model mentioned anywhere in the text, including asides") or a lighter-weight sentence-level scan for the `model X needs Y` pattern could plausibly fix it, but this is optimization, correctly out of scope here |

No new *error category* appeared (fabrication/missing/swap are the same
three types measured in H0) — but Level 3 shows a new *severity
distribution* within the missing-models category, concentrated in one
identifiable, testable presentation pattern.

## Success criteria assessment

| Criterion | Result |
|---|---|
| Deterministic parser succeeds across formatting variations | **FAILS** — 0% success on Level 1, which was specifically "formatting changes only" |
| Structure detector routes correctly | **Partially holds** — never false-positive, but coverage is too narrow to route anything on paraphrased input to the parser at all |
| Fallback behaves correctly when required | **Holds** — engaged every time, spliced correctly, no crashes; residual accuracy is presentation-dependent (86–94% typical, 52.8% under the prose-embedding pattern) |
| No new dominant failure mode appears | **Mostly holds** — same error categories, but a new severe *concentration* of missing-models under one specific, diagnosed presentation pattern |

**Intervention 1 is not validated as generalizing.** The 100% result
from the prior turn was real and correctly caveated at the time ("this
validates the digit-bearing/structured half exactly as scoped... a judge
typing the problem differently... would hit the untested fallback path,
not this 100%") — this run is that untested path, now tested, and it
shows the parser's coverage is narrower than "formatting-robust" would
require.

## Decision

**DEFER.**

Not KEEP: the parser demonstrably does not generalize past its exact
training phrasing, including to changes a human would consider trivial.
Declaring Intervention 1 complete and building further stages on top of
an assumption that formalization is solved would repeat exactly the
mistake H0 was built to catch, one level down.

Not DELETE: the architecture behaved exactly as designed within its
scope — the detector never produced a false positive, the fallback
engaged reliably and correctly every time, and on the benchmark's actual
phrasing the parser still delivers 100%, which is what the live demo and
automated scoring will actually see if the pinned instance's phrasing is
controlled. The problem is regex vocabulary breadth, not a broken
concept.

DEFER means: do not proceed to Intervention 2 treating H0/Intervention 1
as closed. Per the stop condition, no fix is applied here — this is
diagnosis only, reported for a decision, not acted on.
