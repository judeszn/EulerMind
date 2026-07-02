# Scoreboard — the heartbeat

Dev subset: 30 problems (5 bases × 3 categories × clean+messy), dataset v0.
Cells stay `?` until a measurement fills them. RAM = model-process peak
(measured properly from Phase 1 llama.cpp integration; Ollama-phase values
are model-size approximations, marked ~).

## The Ladder (model: qwen2.5:1.5b unless noted)

| Level | Name | Accuracy | Verified | Messy delta | Mean latency | RAM | Experiment |
|---|---|---|---|---|---|---|---|
| L0 | Raw Model | **6.7%** | 0% | −13.3pts | 1.1s | ~1.0 GB | [B0](research/B0_direct_answer/RESULTS.md) |
| L1 | Reasoning Prompt | **3.3%** (≈L0, p=1.0) | 0% | −6.7pts | 10.9s | ~1.0 GB | [B1](research/L1_reasoning_prompt/RESULTS.md) |
| L2 | Tool-Assisted Reasoning | ? | ? | ? | ? | ? | B2 (H1 control) |
| L3 | Verification-Guided Reasoning | ? | ? | ? | ? | ? | B3 (H1 treatment) |

## Model bake-off (at L1 — L0 suppresses reasoning and biases the comparison)

Full results + instrumentation note: [research/bakeoff/RESULTS.md](research/bakeoff/RESULTS.md).
All deltas vs incumbent are statistically indistinguishable at n=30
(McNemar) — directional signal only, confirmation deferred (No Vertical
Optimization).

| Model | Size (Q4) | L1 acc | Messy delta | Latency | Tok/s | Verdict |
|---|---|---|---|---|---|---|
| qwen2.5:1.5b | ~1.0 GB | 3.3% | +6.7pts | 9.8s | 39.9 | incumbent |
| **llama3.2:1b** | ~0.8 GB | 13.3% | 0 | 20.7s | 34.7 | **provisional default** (dominates gemma3) |
| gemma3:1b | ~0.8 GB | 13.3% | 0 | 30.3s | 29.3 | dropped — dominated by llama3.2 |
| deepseek-r1-distill 1.5b | ~1.1 GB | 16.7% | −6.7pts | 86.1s | 33.7 | flagged for L3, too slow as default |
| qwen2.5-math-1.5b (GGUF/llama.cpp) | ~1.0 GB | untested | — | — | — | competition candidate, highest priority open item |

Tokens/sec column exists because S_perf is 30% of the final score.

## Verification integrity (added 2026-07-02)

Operationalizes Law 1's own caveat ("verification is relative to the
formalization") into a number. `grade()` is the benchmark's independent
ground-truth check; `trust_label` is the kernel's own self-assessment —
these can disagree once formalization comes from a real LLM instead of
Oracle Mode's ground-truth cheat.

| Metric | Formula | Scope | Gate |
|---|---|---|---|
| Verified Rate | `count(label=="Verified") / n` | benchmark-wide | tracked |
| Verified Accuracy | `count(label=="Verified" & grade==True) / count(label=="Verified")` | benchmark-wide | tracked (target: rises via H3) |
| False Verification Rate | `count(label=="Verified" & grade==False) / count(label=="Verified")` | benchmark-wide | tracked, **not yet an absolute gate** — H3 is still open |
| False Verification Rate | same formula | **pinned demo instance only** (`demo/prompt.md`) | **hard release gate: 0%** — rehearsed, so achievable |

(Verified Accuracy + False Verification Rate = 100% by construction — two
views of the same count, tracked separately because one communicates the
good case and one communicates the brand risk.)

| Level | Verified Rate | Verified Accuracy | False Verification Rate |
|---|---|---|---|
| L0-L1 | 0% | n/a | n/a |
| L2 | ? | ? | ? |
| L3 | ? | ? | ? |
