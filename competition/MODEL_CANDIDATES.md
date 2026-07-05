# Model candidate leaderboard (Sprint Δ0)

Domain: `math_scientific_reasoning`. Runtime: llama.cpp, GGUF only
(competition rule — no other runtime accepted). Selection is by
measurement through the official profiler on CI (x86, audit-like),
never by reputation.

**Facts** (param count, quant, approximate file size — from public model
cards, to be re-verified at download) vs **measurements** (empty until
the CI profiling run fills them). No cell gets a number without a run.

## Frontier scan results (Δ1 Phase 1 — measured, CI run 28683815170, 2026-07-03)

All 8 candidates through the official profiler (`--skip-accuracy`),
audit-like x86 runner, all URLs public, all architectures compatible:

| Model | TPS | 1st token (ms) | Peak RAM (MB) | S_eff [exact] | S_perf @ tps_max=15 |
|---|---|---|---|---|---|
| qwen2.5-0.5b-instruct | **29.45** | 7,798 | **621** | 91.3 | 100 (cap) |
| tinyllama-1.1b-chat | 23.04 | 12,647 | 1,197 | 83.3 | 100 (cap) |
| gemma-3-1b-it | 19.71 | 8,100 | 986 | 86.2 | 100 (cap) |
| llama-3.2-1b-instruct | 18.86 | 12,301 | 1,383 | 80.7 | 100 (cap) |
| deepseek-r1-distill-qwen-1.5b | 17.34 | 17,395 | 1,817 | 74.7 | 100 (cap) |
| qwen2.5-1.5b-instruct | 15.85 | 16,600 | 1,825 | 74.5 | 100 (cap) |
| qwen2.5-math-1.5b-instruct | 15.02 | 16,789 | 1,700 | 76.3 | 100 (cap) |
| phi-3.5-mini-instruct | 6.06 | 57,847 | 3,836 | 46.5 | 40.4 |

**Phase 1 verdicts (per the pre-registered rule):**
- **Eliminated — phi-3.5-mini**: strictly dominated (worst TPS, worst
  RAM, worst first-token by 3×; the only candidate below the 15-TPS
  reference line). Its accuracy ceiling cannot buy back ~30 S_perf +
  ~30 S_eff points at their weights.
- **Key structural finding [measured]:** under the tps_max=15 reference
  reading, *every remaining candidate caps S_perf at 100* — so the
  decision reduces to `0.5·S_acc + 0.2·S_eff`, and the S_eff spread
  (74.5–91.3) is worth at most ~3.4 total points. **Accuracy dominates
  the choice.** Only if A-05 resolves to "max observed across teams"
  does the fast-small end regain leverage.
- **Finalists for Phase 2 accuracy benchmarking:**
  1. **qwen2.5-math-1.5b** — the domain specialist; highest expected
     math accuracy per parameter.
  2. **deepseek-r1-distill-qwen-1.5b** — reasoning-distilled; the live
     question is whether it beats the math specialist on the proxy
     (with a known risk: long chain-of-thought outputs are token-hungry
     and may parse poorly under strict exact-match).
  3. **qwen2.5-1.5b** — same-family general control; isolates the value
     of math specialization.
- **Reserve — qwen2.5-0.5b**: kept warm, not benchmarked yet. It only
  becomes competitive if A-05 resolves adversarially (its 29.5 TPS and
  91.3 S_eff would then matter); its expected math accuracy is far
  below the 1.5B tier otherwise.

Raw reports: CI artifacts `scan-<model>` on run 28683815170.

## Phase 2 accuracy results (measured, CI run 28684426883, seed 42, limit 50, identical settings)

| Finalist | gsm8k flexible [primary] | gsm8k strict | Predicted S_total @ tps_max 15 / 25 / 50 |
|---|---|---|---|
| **qwen2.5-math-1.5b** | **68%** | 68% | **79.26** / 67.28 / 58.27 |
| deepseek-r1-distill-1.5b | 66% | 66% | 77.93 / **68.74** / **58.33** |
| qwen2.5-1.5b (control) | 52% | 52% | 70.91 / 59.93 / 50.42 |

(arc_easy sanity check unavailable: lm_eval's gguf loglikelihood path
fails against llama-server — `ValueError: zip() argument 2 is longer
than argument 1` — generative tasks only through this backend. The
DeepSeek strict-format risk did NOT materialize: strict = flexible for
all three.)

**Statistical honesty:** 68% vs 66% is one question out of fifty
(stderr ±6.7pts each) — indistinguishable by this project's own
statistics discipline. The specialization gap vs the control
(+16/+14pts, 7–8 questions) is the real, directional finding.

**Rule outcome (select_model.py, pre-registered at commit be22acf):
ESCALATED, not silently picked** — the ranking inverts across tps_max
scenarios: math-1.5b wins at the published reference (15), deepseek at
25 and 50 (by ≤1.5 and 0.06 pts). Exactly the case the escalation
clause was written for; decision depends on Unknown **A-05**.

**RATIFIED — qwen2.5-math-1.5b** (2026-07-04, escalation resolved by the
full-range tps_max sweep — see `competition/MODEL_DECISION.md`). Summary below.
(a) wins at the only *published* anchor (TPS_REFERENCE=15);
(b) never trails on the 50%-weighted accuracy component;
(c) deepseek's scenario wins require A-05 to resolve adversarially AND
are worth ≤1.5 pts there;
(d) all qualitative surfaces favor it — concise math-tuned output for
the demo, the 2 test_prompts, and formalizer integration, vs R1-style
verbose chain-of-thought (slower wall-clock answers, harder to
constrain to JSON);
(e) coherent narrative: math-specialized model on the math track.
**Hedge preserved:** deepseek is the ranked alternate; if the organizer
answer to A-05 is "max observed across teams," this decision is
re-opened by that trigger. Evidence: `accuracy_results_ci_28684426883.json`.

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
