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

| Model | Size (Q4) | L0 acc | L1 acc | Tokens/sec | Verdict |
|---|---|---|---|---|---|
| qwen2.5:1.5b | ~1.0 GB | 6.7% | 3.3% | ? | incumbent (L1 ≈ L0, CoT hallucinates arithmetic) |
| qwen2.5-math-1.5b (GGUF/llama.cpp) | ~1.0 GB | ? | ? | ? | competition candidate |
| deepseek-r1-distill 1.5b | ~1.1 GB | ? | ? | ? | reasoning-tuned |
| gemma3:1b | ~0.8 GB | ? | ? | ? | smallest |
| llama3.2:1b | ~0.8 GB | ? | ? | ? | ? |

Tokens/sec column exists because S_perf is 30% of the final score.
