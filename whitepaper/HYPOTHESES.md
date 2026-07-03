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

**Intervention 1 (Stage B) measured 2026-07-02**
(`research/I1_parser_first/RESULTS.md`): 100% on every metric, 0
fabrication, 0 missing, 0 swaps, LLM fallback never engaged (0/60). Gate 2
passed decisively. Caveat: this validates the digit-bearing/structured
half of the design exactly as scoped — the LLM-fallback path for
unstructured phrasing was never exercised by this run and remains
unvalidated. ~~H0's threshold is cleared for this domain's benchmark data; H1 and H3's
dependency on H0 is satisfied~~ — **superseded by validation below.**

**Validation under controlled perturbation, measured 2026-07-02**
(`research/I1_validation/RESULTS.md`): 30 unique instances, paraphrased
3 ways with byte-identical ground truth (rendered fresh from ground truth,
not edited text — guarantees zero numeric drift). **Parser Success Rate:
0% on all 3 levels, including formatting-only changes.** The regex is
literal, not semantic — it doesn't survive bullets→table, bullets→
semicolons, or any lexical variation. LLM fallback engaged 100% of the
time and worked correctly (no crashes, correct splicing), with accuracy
ranging 52.8%–93.7% depending on presentation — worst on mixed-format
text where catalog entries embedded as prose asides were dropped
entirely (0/30 extracted in a targeted check, vs 13/20 for the same
entries presented in a table).

**Decision: DEFER.** Not KEEP — the 100% result was real but overfit to
one exact phrasing, exactly as the prior turn's caveat predicted before
this was tested. Not DELETE — the architecture (detector, parser,
explicit fallback with correct splicing) behaved exactly as designed
within its scope, and still delivers 100% on the benchmark's controlled
phrasing. H0/H1/H3 dependency status: still blocked at that point.

**Intervention 1B (structure detection + matching extractors) measured
2026-07-02** (`research/I1b_structure/RESULTS.md`): Parser Success Rate
0% → **100% on all 3 paraphrase levels**, LLM fallback → 0%, fabrication
0. Overall Schema Accuracy: L1 100%, L2 100%, L3 88.9% (residual is one
diagnosed segmentation edge case, deliberately not chased to avoid
template-overfitting). **Decision: KEEP — Intervention 1 complete.**
**H0's threshold is now cleared for the structure types in scope**, with
the standing caveat that gains on template-generated paraphrases are a
lower bound on real-judge-phrasing robustness, not proof. H1/H3 are
unblocked to the same degree — resume only with that caveat explicit.

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

**Phase Gamma / constraint_csp measured 2026-07-02**
(`research/G1_csp_validation/RESULTS.md`), 52 problems (42 SAT, 10 UNSAT),
a verification-asymmetric domain chosen specifically because knapsack's
exact-solvability made H1 untestable there. Verifier soundness confirmed
(0% false-certification both arms, every certificate independently
rechecked) and real capability (19.23% coverage, not a floor) — the two
confounds that invalidated the knapsack run are resolved. Result:
Δ=0.0, McNemar p=1.0 (perfect 6-vs-6 discordant split). Composition:
B3 (guided) solved 10/10 UNSAT and 0/42 SAT; B2 (blind) solved a mix
(6 SAT + 4 UNSAT) — structurally different behavior summing to the same
total. **Decisive finding: checked across all 52 problems, 42/42
multi-attempt cases in B3 produced the IDENTICAL failure signal on every
retry** — the guided attempter's output does not vary with temperature-0
feedback. **Decision: DEFER**, narrower than the knapsack DEFER: not a
verifier or capability confound this time, but a confirmed-inert feedback
mechanism — this run tested "single-shot vs multi-shot resampling," not
"guided vs blind," because feedback was never functionally exercised.
Applying the kill threshold's literal numbers here would overclaim past
what was measured. **H1 remains untested after two attempts on two
verticals, both failures now precisely characterized.**

**Intervention 2 measured 2026-07-02** (`research/H1_edge_ai/RESULTS.md`),
60 problems, StructuredFormalizer (1B): Δ=0.0, McNemar p=1.0 — no
measurable difference. **Decision: DEFER, not DELETE.** The kill
threshold's literal numbers would read as DELETE, but 97-99% of all
attempts in both arms failed identically on `constraint_violation`
(the Attempter can't reliably find a feasible integer combination,
regardless of feedback), and every "Verified" label in the run (3/60
each arm) was a false verification — `KnapsackVerifier` checks
feasibility/consistency, not optimality, while `benchmark.metrics.grade()`
requires exact match to the true optimum. Both confounds swamp any room
for policy to matter; this run did not cleanly test the causal claim.
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
