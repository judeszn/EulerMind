# Intervention 2 — B2 (Blind Retry) vs B3 (Guided Retry): RESULTS

**Date:** 2026-07-02 · `llama3.2:1b`, full 60-problem `edge_ai_deployment`
dev set (30 bases, clean+messy), `StructuredFormalizer` (Intervention 1B,
the completed artifact) for both arms, `DeterministicExecutor` +
`KnapsackVerifier` unmodified. **Policy is the loop-decision variable**
(`policy=None` vs `policy=DeterministicPolicy()`); Attempter
temperature/feedback-visibility differ by the pre-registered experiment
design (stated explicitly before this run, not decided after seeing
results).

## Comparison table

| Metric | B2 (blind) | B3 (guided) | Δ (B3−B2) |
|---|---|---|---|
| **Verified-Correct Rate** | 0.0% | 0.0% | **0.0** |
| False Verification Rate | 5.0% | 5.0% | 0.0 |
| Mean Attempts | 2.90 | 2.95 | +0.05 |
| Mean Latency (per problem, full run) | 4.278s | 4.244s | -0.034s |
| Trust label: Verified | 3/60 | 3/60 | — |
| Trust label: Open | 57/60 | 57/60 | — |
| Trust label: Derived / Heuristic | 0 / 0 | 0 / 0 | — |
| **McNemar p-value** | — | — | **1.0** |
| **Verdict** | — | — | **indistinguishable** |

Δ=0.0, p=1.0 is as close to a null result as a paired comparison can
produce — not a small effect, a complete absence of any measurable
difference.

## Failure breakdown

Pooled across all attempts (174 in B2, 177 in B3):

| Failure kind | B2 | B3 |
|---|---|---|
| `constraint_violation` | 486 signals | 484 signals |
| `answer_shape` / `formalization_shape` | 0 | 0 |
| Verified (any) | 3 | 3 |

**Zero formalization or shape failures in either arm** — Intervention 1B
is holding on the original benchmark data exactly as measured. The
entire failure surface is `constraint_violation`: the Attempter's
proposed integer counts don't fit the RAM/FLOPS/latency budget or miss
the high-accuracy requirement, in both arms, at nearly the same rate
(97–99% of attempts either way).

## The critical finding: every "Verified" label in this run was false

Both arms produced exactly 3 Verified labels; `verified_correct_rate` is
0.0% in both because **all 6 were false verifications** — feasible
answers that were not the true optimum. Confirmed directly on one case
(`edge-00002-clean`, B2, attempt 1): the Verifier returned `ok: true` with
zero signals (every budget check and the profit-consistency check
passed), but `benchmark.metrics.grade()` — which requires an exact match
to the true optimal score — correctly marked it wrong.

**Root cause, precisely: `KnapsackVerifier` checks feasibility and
internal consistency, not optimality.** The benchmark's grading standard
requires the proposed plan to equal the true maximum score; the kernel's
"Verified" label currently only certifies "this plan satisfies every
constraint and its claimed score matches its own arithmetic" — a strictly
weaker property. This is not a formalization bug and not an arithmetic
bug (0 profit-consistency failures among the false verifications — the
model's self-reported score matched its own counts correctly; the counts
themselves just weren't optimal). It is a gap in what the Verifier's
contract certifies versus what "correct" means for this benchmark
category.

## Additional pattern (informational — same data, no new experiment)

The 3 B2 successes all landed on attempt 1; the 3 B3 successes all landed
on attempt 2. The two sets of successful problem IDs have **zero
overlap** (`{edge-00017-messy, edge-00002-clean, edge-00031-clean}` vs
`{edge-00034-messy, edge-00023-messy, edge-00034-clean}`). Consistent
with noise (a ~5% hit rate on largely-unrelated instances) rather than
either arm exhibiting a systematic advantage.

## Decision

**DEFER.**

The registered kill threshold (Δ ≥ 7pts, p < 0.05) is not met — taken at
face value, Δ=0.0 and p=1.0 would normally read as DELETE, per H1's own
pre-registered text ("otherwise VGS is dead and the project pivots").
I'm not recording that verdict, because the failure breakdown shows this
run did not cleanly test H1's causal claim: **97–99% of all attempts in
both arms fail identically on `constraint_violation`**, meaning there is
almost no room for verifier feedback to produce a measurable difference
— both arms are dominated by the same bottleneck (the Attempter's
inability to reliably find a feasible, let alone optimal, integer
combination via free-form reasoning) before policy ever gets a chance to
matter. Layered on top, the **Verified-Correct success bar itself is
confounded** by the feasibility-vs-optimality gap above — even a
genuinely useful repair (guided retry successfully turning an infeasible
attempt into a feasible one) would not register as Verified-Correct
unless it happened to land exactly on the global optimum.

A clean test of H1 requires these two confounds resolved first, not a
retry of the same measurement. Not proposing what that resolution should
be — reporting only what was measured.

Per the stop condition: not beginning another intervention, not
suggesting future work. Waiting for further instruction.
