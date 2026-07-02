# Model bake-off — RESULTS

**Date:** 2026-07-02 · **Subset:** 30 dev problems (same as L0/L1), L1 prompt

## Instrumentation bug found and fixed

Ollama's self-reported `eval_duration` for gemma3:1b implied 3.1 tok/s,
which is arithmetically impossible given 889.5 mean tokens in a 30.3s mean
latency (~29 tok/s). Verified with an isolated single-call test (41 tok/s,
normal) — the corruption only appears under concurrent multi-model load
during the bake-off run, most likely Ollama's duration counters getting
confused by model swap/eviction between candidates.

**Fix applied:** tokens/sec recomputed from wall-clock latency ÷ token
count for all four models, not from Ollama's internal counters. This is
physically grounded and trustworthy. Not expected to recur in Phase 1,
where timing instrumentation is owned directly against llama.cpp.

## Corrected table

| Model | L1 acc | Messy delta | Latency | Tok/s (corrected) |
|---|---|---|---|---|
| qwen2.5:1.5b (incumbent) | 3.3% | +6.7pts | 9.8s | 39.9 |
| llama3.2:1b | 13.3% | 0 | 20.7s | 34.7 |
| gemma3:1b | 13.3% | 0 | 30.3s | 29.3 |
| deepseek-r1:1.5b | 16.7% | −6.7pts | 86.1s | 33.7 |

## Paired comparison vs incumbent (McNemar exact, n=30)

| Model | p-value | Verdict |
|---|---|---|
| llama3.2:1b | 0.375 | indistinguishable |
| gemma3:1b | 0.375 | indistinguishable |
| deepseek-r1:1.5b | 0.219 | indistinguishable |

At n=30, even a 4x raw accuracy gap (deepseek) is not statistically
distinguishable from the incumbent. All three challengers nominally clear
the plan's >10pt acceptance bar (10.0 / 10.0 / 13.3 pts), which per
PLAN.md triggers a full-dev-split confirmation run.

## Decision

**DEFER full confirmation runs.** Running 172-problem confirmations for
three candidates now (deepseek alone would take ~4 hours at 86s/problem)
is exactly the open-ended model-selection rabbit hole the ladder guardrail
(No Vertical Optimization) exists to prevent before L2 even exists.

Sub-decisions that don't need more data:

- **gemma3:1b is dropped.** llama3.2:1b pareto-dominates it: identical
  accuracy and robustness, but 1.5x faster and fewer tokens. No ambiguity.
- **llama3.2:1b — provisional KEEP** as the default candidate for
  continued rungs (L2 onward): matches deepseek's robustness profile
  without the 8.8x latency tax, ties gemma on accuracy while being faster.
- **deepseek-r1:1.5b — flagged, not adopted.** Best raw accuracy, but
  8.8x slower than the incumbent and its messy-delta went *negative*
  (distractor variants scored better than clean, plausibly noise at
  n=15 pairs — needs a bigger sample before trusting the sign). Revisit
  as an L3 candidate: its verbosity may pair well with verifier feedback,
  where correctness matters more than raw throughput.
- **qwen2.5-math-1.5b — still untested.** The actual competition
  candidate (math-tuned, RAM-optimized for our target). Needs GGUF via
  llama.cpp, not available on Ollama. Highest-priority open item, not
  superseded by this bake-off since it wasn't in the pool.

## What this means for the ladder

Model choice is not blocking L2. The tool-assisted rung is expected to
swamp these L1-level differences anyway (delegating arithmetic to
SymPy/Z3 removes the exact failure mode — hallucinated coefficients —
that separates these models at L1). Build L2 on llama3.2:1b as the
working default; re-run the bake-off properly (full dev split, plus
qwen2.5-math-1.5b) once L2 exists, since that is the reasoning surface
that will actually ship.
