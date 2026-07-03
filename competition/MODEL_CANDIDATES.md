# Model candidate leaderboard (Sprint Δ0)

Domain: `math_scientific_reasoning`. Runtime: llama.cpp, GGUF only
(competition rule — no other runtime accepted). Selection is by
measurement through the official profiler on CI (x86, audit-like),
never by reputation.

**Facts** (param count, quant, approximate file size — from public model
cards, to be re-verified at download) vs **measurements** (empty until
the CI profiling run fills them). No cell gets a number without a run.

| Model | Params | GGUF Q4_K_M size (approx) | TPS (CI) | Peak RAM (CI) | lm_eval proxy | Notes |
|---|---|---|---|---|---|---|
| SmolLM2-135M-Instruct | 135M | ~0.1 GB | **91.77** [measured, CI run 28683560689] | **0.19 GB** [measured] | ? (skipped) | Template default, smoke only. **Measured finding: a 135M model hits ~92 TPS and S_eff≈97 on audit-like hardware** — concretely confirms the tps_max adversarial exposure (any team shipping a tiny model can push TPS_max to ~90+), and confirms tiny models max the automated S_perf/S_eff while (presumably) dying on the 50%-weighted S_acc. Full report: `smoke_submission_report_ci_28683560689.json` |
| Llama-3.2-1B-Instruct | 1.2B | ~0.8 GB | ? | ? | ? | Already the project's LLM (Ollama-side); known-quantity behavior |
| Qwen2.5-1.5B-Instruct | 1.5B | ~1.0 GB | ? | ? | ? | Prior bake-off incumbent family |
| **Qwen2.5-Math-1.5B-Instruct** | 1.5B | ~1.0 GB | ? | ? | ? | Domain-specialized; scoreboard.md has flagged it "competition candidate, highest priority open item" since the original bake-off — Δ0 finally measures it |
| DeepSeek-R1-Distill-Qwen-1.5B | 1.5B | ~1.1 GB | ? | ? | ? | Reasoning-distilled; prior bake-off flagged it strong-but-slow at L1 (86s latency) — TPS risk |
| SmolLM2-1.7B-Instruct | 1.7B | ~1.1 GB | ? | ? | ? | Strong small-model family |
| Gemma-2-2b-it | 2.6B | ~1.7 GB | ? | ? | ? | Upper size bound worth one measurement; prior 1B sibling was dominated in bake-off |
| Phi-3.5-mini-instruct | 3.8B | ~2.3 GB | ? | ? | ? | Likely accuracy ceiling of the shortlist; S_eff cost ~2.9 pts/GB and TPS cost to quantify — measure before excluding |

## Selection rule (pre-registered, before any measurement exists)

Maximize `score_model.s_total` using: CI-measured TPS and peak RAM
**[measured]**, lm_eval proxy as s_acc stand-in **[assumption, labeled]**,
african_bonus held constant across candidates, reported at
tps_max ∈ {15, 25, 50} — pick the winner under tps_max=15 unless the
ranking inverts across scenarios, in which case bring the tradeoff back
for a decision rather than picking silently.

Proxy suite until the official math validation set is obtained:
`gsm8k` (primary — math word problems, closest to the domain) +
`arc_easy` (the profiler's own default, for comparability). Both
[assumption]: the hidden subset is per-domain and unpublished.
