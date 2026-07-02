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
**Status.** Registered. Blocked on Phase 1 formalizer.

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
