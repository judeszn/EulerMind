# Eval + Guardrail Harness — PRD (Submission Phase, 2026-07-04)

Status: **PROPOSED — Track B instrument.** Frozen scope below; changes need a
decision-matrix row (docs/SCORING.md) like anything else.

## 1. Why this exists (one paragraph)

50 days out, the kernel's *science* is frozen — not its *product*. These are
different (docs/SCIENTIFIC_STATE.md is a research record, not a spec freeze):
- **Scientifically frozen:** H1 (verifier-guided reasoning) is rejected at the
  tested config; Gamma is closed; the three certified verticals' evidence does
  not reopen. No new *research claims*.
- **Competitively open:** any bounded, measured routing/coverage change that
  raises Verified+Derived coverage *without* raising false-verification is a
  product improvement and should ship. Freezing the science does not freeze the
  product.

The unclaimed qualitative points are in **proving, at scale and honestly, what
EulerMind can and cannot check**, in **shipping bounded coverage gains that
move the North Star (§4.0)**, and in **never letting a demo OOM, overheat, or
falsely certify**. This harness turns "trust me" into a published number a
judge reads in under two minutes. It builds **no *speculative* capability** —
per WIN.md/CLAUDE.md the benchmark is an instrument, never a solver — but it is
also the scoreboard against which *non*-speculative capability earns its place
(§4.0, §6).

Which criterion (CLAUDE.md Q1): qualitative **S_acc** (report + demo + judge
confidence), **African Use Case +10**, and the **disqualification guardrails**
(OOM/thermal) that protect all other points. Simpler implementation (Q2):
extends `benchmark/` + `app/`, no new architecture. Measurable in 48h (Q3):
yes — first run on the 100-item set is a single command. Raises expected score
(Q4): yes — it is the only artifact that converts the existing, already-built
trust surface into judge-visible evidence.

## 2. In scope / out of scope

**In scope**
- A fixed **curriculum-aligned eval set** (target n=100, WAEC/SSCE secondary
  maths), versioned and immutable like all `benchmark/` datasets.
- A **runner** that pushes each question through the Tutor Lane router
  (`app/tutor.py` → `app/answer_checker.py`, plus the kernel `Verified` path)
  and records the trust label + correctness.
- **Trust & coverage metrics** (§4) written to `scoreboard.md` and a single
  publishable `REPORT` artifact.
- **Guardrails** (§5) enforced per-question: RAM ceiling, thermal, latency,
  offline — the rubric-mandated existence checks.
- A **JSONL trace** conforming to docs/LOGGING.md (never break replay).

**Out of scope (frozen non-goals)**
- No **speculative** capability. Bounded coverage gains that pass the
  admission test (§2.1) are *in* scope; anything whose payoff can't be measured
  on the frozen set within 48h is out. No new vertical, no reopening H1, no LLM
  in the labeling path (labels come only from `app/answer_checker.py` / kernel
  certificates — model self-labeling is the banned fabricated-certainty
  pattern, PROMPT_STRATEGY.md).
- No learner memory, evidence engine, evolution pipeline, School OS, teacher
  dashboards, autonomous curriculum (DO_NOT_BUILD.md).
- This harness does **not** implement Track A (model selection / lm_eval /
  llama-bench) — but it **scores** the coupling point (§2.2): the model is
  chosen jointly on the automated proxy *and* downstream TAR here.

## 2.1 Capability-admission test (the handbook rule, operationalized)

> *Every new capability earns its place by increasing Trusted Answer Rate while
> keeping False-Verification Rate at zero.*

A proposed checker / routing change is **admitted** only if it passes all of:
1. **Bounded:** buildable and measurable in ≤ 48h (WIN.md 48-hour rule).
2. **Non-speculative:** targets a question shape the model *already answers*,
   turning existing Heuristic answers into checked Derived/Verified ones —
   not a new solving engine (a geometry verifier that takes three weeks is a
   ❌, not a coverage tweak).
3. **Moves the North Star:** measured TAR delta > 0 on the frozen dev set,
   decided by `benchmark.metrics.compare_paired` (McNemar), never raw rates.
4. **FVR stays 0:** zero new false-verifications on dev *and* on the pinned
   demo instance. A single new false-cert rejects the change outright.
5. **Observable (Guardrail 14):** it changes `benchmark/`, `demo/`, or
   `scoreboard.md`.

Fails any one → `future/`, not main.

## 2.2 The Track A ↔ Track B coupling point (model selection)

The rubric scores the **bare GGUF** for the automated 50% (no router). The
product scores the **model+router** for TAR. They meet at one decision — which
GGUF ships — so that decision is made on a **joint** objective, not
automated-best alone:

```
pick model =  argmax over candidates of
              [ automated score (lm_eval proxy + llama-bench TPS + peak RAM) ]
              AND  [ downstream TAR through the router ]
```

Concretely: a candidate that wins lm_eval but emits answers
`app/answer_checker.py` can't parse (heavy LaTeX, no clean `FINAL ANSWER`
line — see the existing `_delatex` shim) is a **net loss** and is rejected
even if its automated proxy is higher. This harness supplies the TAR half of
that comparison; TARGETS.md supplies the automated half.

## 3. The eval set (the "100 questions")

- **Source discipline:** curriculum-aligned (WAEC/SSCE topics), themed as
  African SME scenarios where natural (load-bearing, not cosmetic — earns the
  +10). Direction-of-inference rule (EXECUTION_CONTRACT): questions are chosen
  because the curriculum requires them, **never** constructed so a label can
  win. No question is authored to be checkable; the checkable fraction is a
  *measurement*, not a design target.
- **Immutable:** new directory + CHANGELOG entry, never regenerated in place
  (CLAUDE.md dataset rule). Proposed path: `benchmark/datasets/tutor_v0/`.
- **Ground truth:** each item carries a gold answer where one exists, so
  correctness is graded independently of the trust label. Explanation-only
  items are marked (label expectation = Heuristic "see explanation").
- **Split discipline:** a **dev** portion is rehearsed freely; a **holdout**
  portion is run once at the phase gate and never iterated (WIN.md). The
  demo's pinned instance lives in the dev portion, never holdout.
- **Coverage map:** every item tagged by expected route — kernel-certifiable
  (LP/CSP/bounded-opt shapes) vs numeric-checkable (solve/derivative/arith)
  vs heuristic-only (proofs, word explanations). This tag is the *coverage
  denominator*, published, not hidden.

## 4.0 North Star (the one number we optimize daily)

**Trusted Answer Rate (TAR)** — the single metric every product decision moves:

```
              count(label ∈ {Verified, Derived}  AND  graded_correct)
TAR   =       --------------------------------------------------------
                        n   (the FROZEN eval set, §3)

subject to    False-Verification Rate  ==  0
```

Every engineering decision reduces to one question:
**"Does this raise TAR without moving FVR off zero?"** Yes → ship. No → don't.
FVR is not a metric to trade against — it is a wall. A change that raises TAR
by any amount while lifting FVR above zero is **rejected**, not weighed.

Two properties that keep TAR honest (both mandatory):
1. **The denominator is frozen and immutable (§3).** TAR must only rise by
   improving the product, never by reshaping "all questions" toward checkable
   shapes — that is benchmark engineering, banned by the direction-of-inference
   rule (EXECUTION_CONTRACT). You do not get to move the denominator.
2. **TAR has a true ceiling below 100%.** Genuinely unprovable items (proofs,
   open explanations) can never enter the numerator. That cap is an honest
   property of the product, not a failure to fix — reporting it *is* the trust
   story.

The six §4 metrics remain, as the decomposition that explains *why* TAR moved.
TAR is the headline; they are the diagnosis.

## 4. Metrics (the decomposition behind the North Star)

Per-item the runner records `{label, checked, passed, graded_correct}`.
Aggregated:

| Metric | Formula | Why it's published |
|---|---|---|
| **Coverage** | `count(label in {Verified,Derived}) / n` | Honest answer to "how much can it prove?" |
| **Verified-Correct Rate** | `count(label==Verified & correct) / n` | Kernel-certified & actually right |
| **Derived-Correct Rate** | `count(label==Derived & correct) / n` | Numeric-checked & actually right |
| **False-Verification Rate** | `count(label∈{Verified,Derived} & !correct) / count(label∈{Verified,Derived})` | **The brand-risk number.** Hard gate. |
| **Honest-Heuristic Rate** | `count(label==Heuristic & correctly-unprovable) / count(unprovable)` | Does it *say* when it can't check? |
| **Loud-Failure Rate** | `count(checked & !passed surfaced to user) / count(check ran & failed)` | "This answer did not survive substitution" — the most valuable thing it can say |

## 5. Guardrails (rubric-mandated; failing one is a stop, not a warning)

Enforced per-question during the run, on x86 CI (never the arm64 dev machine —
audit drift ±25% TPS / ±15% RAM, SCORING.md):

- **RAM ceiling:** hard cap; peak model-process RSS logged; **OOM = fail the
  run** (OOM = disqualification in the real thing). Target ≤ 1.4 GB (TARGETS).
- **Thermal:** temp telemetry; > 85°C flags P_thermal = −10; run aborts.
- **Latency:** per-question wall-clock recorded; a p95 budget so the demo can
  never hang on a judge.
- **Offline:** the run asserts no network egress beyond the local
  llama-server (127.0.0.1) — offline is a primary constraint (WIN.md).

## 6. Acceptance gates (what "done" means)

1. **Runs green in CI** on the x86 profile, offline, under the RAM ceiling,
   no thermal flag. (Existence before excellence.)
2. **False-Verification Rate = 0% on the pinned demo instance** — non-
   negotiable hard release gate (WIN.md, scoreboard.md). Benchmark-wide FVR is
   *tracked and published*, target 0%, but the pinned-instance 0% is the wall.
3. **Trusted Answer Rate (§4.0) reported and tracked over time** — the harness
   emits TAR on every run so the daily question ("did TAR rise, did FVR stay
   0?") is answerable from one number.
4. **scoreboard.md updated** with the measured §4 table (cells stay `?` until
   the run fills them — no faked precision).
5. **One publishable artifact** (`competition/TUTOR_EVAL_REPORT.md` or
   REPORT.md section) a judge reads in < 2 min: TAR, coverage, correctness,
   and — stated plainly — what it refuses to check and why. Honesty is the
   feature.
6. **Ladder mapping recorded:** each item's route tagged L2 (tool-checked /
   Derived) vs L3 (certificate / Verified) so the harness feeds the existing
   rung scoreboard, not a parallel one.

## 6.1 The three workstreams this serves (until submission)

| # | Workstream | Duration | Owns | Gate |
|---|---|---|---|---|
| 1 | **Model** | 2–5 days | Benchmark remaining candidates, freeze the winner on the §2.2 *joint* objective | Frozen GGUF, joint-best |
| 2 | **Product** | ~30 days | Routing, checking, measurable-coverage expansion, UX — each change admitted via §2.1 | TAR ↑, FVR = 0 |
| 3 | **Evidence** (this harness) | parallel | Run the eval, measure TAR/coverage/FVR, publish | Gates §6 |

Workstream 2's charter is **not** "add features" — it is "add only capability
that passes §2.1." Workstream 1 stays alive until the model is genuinely the
joint-best under competition constraints; it does not block 2 or 3.

## 7. Non-goals restated as kill triggers

If any of these appear in a PR against this PRD, reject it:
- A question authored to be checkable, or any reshaping of the frozen
  denominator to inflate TAR (Goodhart / benchmark engineering).
- An LLM asked to assign or influence a trust label.
- A metric that hides the heuristic denominator to inflate coverage.
- A capability that fails the §2.1 admission test — speculative, unbounded
  (a new solving engine), TAR-neutral, or FVR-raising by even one case.
- Iterating on the holdout split.

## 8. Build order (thin slices, WIN.md)

1. `tutor_v0` dev set (~20 items across all coverage tags) + CHANGELOG.
2. Runner over the router, emitting the LOGGING.md JSONL trace.
3. §4 metrics aggregator → scoreboard.md cells.
4. §5 guardrails wired into the runner (fail-closed).
5. Publishable report artifact + pinned-instance 0% FVR gate.
6. Scale dev set to ~80; freeze a ~20 holdout; run holdout once at the gate.

Each slice must change `benchmark/`, `demo/`, or `scoreboard.md` (Guardrail
14) or it didn't happen.
