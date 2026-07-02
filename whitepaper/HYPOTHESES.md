# Pre-registered Hypotheses

Rules (frozen):
- Every hypothesis is registered here **before** its experiment is built.
- Decision by paired comparison on the same problems (McNemar exact test,
  `benchmark.metrics.compare_paired`), never by comparing raw rates.
- At n≈100 paired problems, differences under ~7 points are noise: treated as
  "equal", and **equal → delete**.
- The dev split is for iteration. The holdout split is run once per phase gate.
  Judges' problems are assumed unseen; nothing is ever tuned on holdout.
- The instruments (harness, generators, graders) are exempt from kill rules.

---

## H0 — Can a compact offline model accurately formalize optimization problems?

**Hypothesis.** A ~1-2B offline model can extract our schema (variables,
budgets/constraints, thresholds) from natural-language problems reliably
enough to trust downstream measurements built on top of it.
**Root of the dependency graph** — H1 and H3 are both blocked on H0
clearing its threshold, since both would otherwise be measuring retry
policy or checking mechanisms on top of noisy, unmeasured input quality.

```
H0
├──► H1  (blind retry vs guided retry - meaningless on corrupted input)
└──► H3  (formalization checking - needs to know what's left to check)
```

**Metrics.** Field-by-field, no solving/retry/policy/executor/verifier —
Variable Extraction Accuracy (model-name F1), Numeric Extraction Accuracy,
Field Association Accuracy (a correct value on the wrong entity, isolated
from outright fabrication), Unit Normalization Accuracy, Constraint
Extraction Accuracy, Overall Schema Accuracy.
**Kill threshold.** overall_schema_accuracy ≥ 90% AND
unit_normalization_accuracy ≥ 90% before H1/H3 measurements are trusted.
**Status.** Measured 2026-07-02, n=60 (`research/H0_formalization/RESULTS.md`):
overall 74.0%, unit normalization 28.3% — below threshold.
**Decision: PIVOT** to deterministic parser-first extraction (Stage B) —
not a change of direction, confirmation that the already-planned next
step targets the actual measured problem. Dominant failure modes:
fabrication (11.0%) and missing models (5.3%) outweigh field-association
errors (2.9%) roughly 6:1 — the error is concentrated in mechanical
transcription of explicit structured/digit-bearing text, not in semantic
misunderstanding of which number belongs to which entity.

---

## H1 — Feedback beats blind retry (THE BET)

**Hypothesis.** Structured verifier feedback (which constraint failed, where) placed
in context for the next attempt yields a higher verified-correct rate than blind
resampling at temperature, under an identical compute budget (same model, same max
tokens, same wall-clock cap).

**Experiment.** Same model, same problems, same executor/verifier — the
kernel's `policy` argument is the only variable (`kernel/loop.py`).
Control (B2) = `policy=None` (blind retry, `next_action` is always
`"attempt"`, no failure signal changes behavior). Treatment (B3) =
`policy=DeterministicPolicy()` (`kernel/policy.py` — a naive, explicit
kind-to-action rule table; see H2 for whether the mapping itself is right).
**Metrics.** Verified-correct rate; attempts-to-success distribution.
**Kill threshold.** Feedback must beat resampling with McNemar p < 0.05 and a
delta ≥ 7 points on dev. Otherwise VGS is dead and the project pivots.
**Status.** Kernel wiring complete and oracle-validated (Policy invoked,
`reformalize` loops back to the Formalizer, repeated failures escalate —
28/28 selftest). Blocked on Phase 1 real Formalizer/Attempter/Executor.

**Generalization condition (frozen with the vertical slice, 2026-07-02):**
the real pipeline is built first against `edge_ai_deployment` only
(Phase 1C, WIN.md). H1's own measurement does not run until Phase 1E,
after Phase 1D generalizes the executor/verifier to >=2 categories. An
Edge-AI-only measurement, if time runs out before 1D-1E complete, must be
reported and labeled exactly that — "Edge AI Optimizer only, not yet
generalized" — never promoted to a blanket H1 CONFIRMED/DENIED verdict.
A single-category result generalized to a global claim would be Law 1's
violation applied to our own research process.

## H2 — Patch beats rewrite

**Hypothesis.** Given verifier feedback, regenerating only the failed region beats
full regeneration. (Literature warning: self-repair gains shrink with model size;
the boring answer "resample wins at 1.5B" is expected and acceptable.)
**Metrics.** Repair success rate on instrumented traces; tokens per solve.
**Kill threshold.** Paired, p < 0.05, else delete the patch path.
**Status.** Registered. Blocked on H1. Note: `kernel/policy.py`'s
`DeterministicPolicy` already encodes a first, explicit kind→action mapping
(e.g. `constraint_violation` → patch, `answer_shape` → reformalize,
repeated failure → escalate). H2 is the test of whether that mapping beats
simpler alternatives (always-patch, always-rewrite) — not a claim that the
current table is already right.

## H3 — Formalization checking reduces verified-wrong answers

**Hypothesis.** Back-translation (formalization → English → compare) and/or redundant
formalization (formalize twice, compare) reduces the rate of answers that are
machine-verified against a *wrong* formalization.
**Metrics.** Verified-wrong rate (graded false but labelled Verified) on messy
variants; clean-vs-messy robustness delta.
**Kill threshold.** Must reduce verified-wrong rate without cutting overall
verified-correct rate; else delete.
**Status.** Registered. **Blocked on H0** (not "Phase 1 formalizer" generically
— H0's 2026-07-02 measurement shows the dominant errors are mechanical
(fabrication, missing models, unit conversion), which Stage B's
deterministic extraction targets directly, not H3's checking mechanism.
H3's actual remaining scope, once Stage B lands, is the smaller residual:
field-association errors (2.9% measured) that survive mechanical
extraction — semantic misattribution, not transcription failure. Sequencing:
H0 reduces deterministic formalization errors → H3 reduces the semantic
formalization errors left over).

## H4 — Typed IR beats raw Python

**Hypothesis.** Model emits a typed intermediate representation compiled to solver
calls, vs. model writes SymPy/Z3 Python directly.
**Metrics.** Verified-correct rate, peak RAM, tokens, wall-clock. Paired.
**Kill threshold.** IR must beat raw Python on verified-correct rate OR enable
verification raw Python structurally cannot. Better → keep. Worse → delete.
Equal → delete.
**Status.** Registered. Blocked on Phase 1.

## H5 — African language capability is worth its cost (rubric: +15% multiplicative)

**Hypothesis.** The 1.5B model can formalize math word problems stated in at
least one African language (candidates: Swahili, Hausa, Yoruba) well enough
that the verified-correct rate on translated problems stays within 15 points
of the English rate — making the +15% bonus net-positive.

**Experiment.** Translate a 30-problem dev subset (procedurally — the
generators' surface templates are translatable); run the standard loop; pair
against the English originals.
**Metrics.** Verified-correct rate delta (translated vs English), RAM/latency
impact of any added components.
**Kill threshold.** 48-hour scoping first (does the model produce anything
usable at all?). If the capability requires a second model or breaks the RAM
budget, delete — the bonus cannot cost the disqualification.
**Status.** Registered 2026-07-02 from the official rubric. Scoping allowed
during Phase 1; full experiment blocked on the loop.
