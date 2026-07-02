# L1 / B1 — Reasoning Prompt: RESULTS

**Date:** 2026-07-02 · **Model:** qwen2.5:1.5b (Ollama, temp 0, CoT + JSON tail)
**Subset:** same 30 dev problems as L0 (paired by construction)

## Numbers

| Metric | L0 | L1 |
|---|---|---|
| Correct rate | 6.7% | **3.3%** |
| Verified-correct | 0% | 0% |
| Clean / messy | 13.3% / 0% | 6.7% / 0% |
| Mean latency | 1.1 s | **10.9 s** (p95 34.5 s) |

**Paired McNemar:** 2-vs-1 discordant, p = 1.0 → **indistinguishable**.

## Diagnosis (from raw output inspection)

- JSON extraction from CoT works — not a tooling failure.
- The model **hallucinates the mathematics**: on lp-00007 it invented
  different constraint coefficients than the problem states, then wrote
  "Verify the solution", checked its own invented numbers, **passed
  itself**, and returned a confidently wrong answer. On calculus it
  "reasoned" for 53 tokens and guessed.
- Self-verification at 1.5B is fabricated certainty. This is Law 1's
  justification, measured in our own baseline — and demo material.

## Decision (48-hour rule)

**DEFER.** Do not optimize L1 (No Vertical Optimization — and the data says
prompt-polish can't fix arithmetic hallucination anyway). Proceed directly
to L2 (Tool-Assisted): the failure mode is exactly the one SymPy/Z3
delegation is designed to remove. The bake-off re-tests L1 per model —
reasoning-tuned candidates (deepseek-r1-distill, qwen2.5-math) may behave
differently and are downloading now.

## Cost note

CoT costs 10× latency for zero measured gain at this scale. Under S_perf
(30% of final score), unaided chain-of-thought is negative expected value.
