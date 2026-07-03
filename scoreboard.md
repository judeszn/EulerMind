# Scoreboard — the heartbeat

**This is the Evidence ledger** — permanent, accumulating per-experiment
measurements, never deleted. For the current *conclusions* drawn from
this evidence (the Knowledge layer — what the science currently says),
see `docs/SCIENTIFIC_STATE.md`. This file records what was measured; that
file records what it currently means.

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

## Phase Gamma — constraint_csp H1 attempt (2026-07-02, n=52)

Verification-asymmetric domain (checking O(constraints), finding a
solution over 2520 permutations is not) — chosen because knapsack's
exact-solvability made H1 untestable there.

| Metric | B2 (blind) | B3 (guided) |
|---|---|---|
| Verified-Correct Rate | 19.23% | 19.23% |
| False Certification Rate | 0.0% | 0.0% |
| SAT solved (of 42) | 6 | **0** |
| UNSAT solved (of 10) | 4 | **10** |

Δ=0.0, McNemar p=1.0 (perfect 6-vs-6 discordant split). Verifier soundness
and capability confounds from the knapsack run are both resolved here.

**H1 decomposed, not left as "untested"** (frozen wording, 2026-07-03):
**H1a** (does feedback produce observable behavioural variation?) —
*under the registered intervention (prompt-appended textual verifier
feedback) and registered inference configuration (llama3.2:1b,
temperature 0), no observable behavioural variation was detected across
retries* — checked on 42/42 multi-attempt cases, not a sample.
Configuration-scoped, not global; behavioural, not cognitive.
Full report: [research/G1_csp_validation/RESULTS.md](research/G1_csp_validation/RESULTS.md).

## Phase Gamma — H1b, temperature-matched (2026-07-03, n=52)

Fixed the confound above: both arms temp=0.6, `seed=attempt`. Sanity gate
(unmodified `GuidedCSPAttempter()` default) reproduced H1a's 42/42
exactly before trusting anything else. Mechanism gate (≥50% threshold):
B2 79%, **B3 100%** — passed, feedback confirmed functionally live.

| Metric | B2 (blind) | B3 (guided) | Δ |
|---|---|---|---|
| Verified-Correct Rate | 19.23% | 23.08% | +3.85pts |
| False Certification | 0.0% | 0.0% | 0.0 |
| McNemar p | — | — | **0.79** |

**Status: PROVISIONAL, rejected by the registered decision rule at n=1
execution** (corrected 2026-07-03, confirmation review) — first H1b
measurement to pass every validity gate (verifier sound, mechanism live,
sanity-checked single-variable design); does not clear the pre-registered
kill threshold (Δ≥7, p<0.05). "Falsified" softened to "rejected by the
registered decision rule" — this tested one bundled configuration
(model+policy+encoding+retry mechanism), not verifier-guided reasoning in
the abstract; the practical consequence (don't pursue this exact
configuration further without new evidence) is unchanged. **Stochastic
result, confirmed by review to have exactly one execution on record —
not yet internally reproduced.** Awaiting N=3 pre-registered reruns
(not yet authorized/executed) before this can be called confirmed rather
than provisional. Not a claim that feedback can't help under any
model/encoding/policy — untested elsewhere. Full report:
[research/G2_csp_h1b/RESULTS.md](research/G2_csp_h1b/RESULTS.md).

**Update (2026-07-03, Resolution A):** the registered N=3 stochastic
reruns were found structurally impossible — a fixed seed at temperature
0.6 is bit-deterministic on this stack (PC-2026-07-03), so three
identical-config reruns are trivially identical and cannot measure
anything. Per the Conflict Resolution rule the run stopped and Resolution
A was applied: the result is re-classified **deterministic**, whose
reproduction bar is a bit-identical rerun — met (a full rerun reproduced
the committed numbers to every decimal: Δ=+3.85pts, p=0.790527). Status
now: **rejected by the registered decision rule, internally reproduced
(deterministic).** Sampling robustness became a separate registered
experiment (H1b-Gamma-2, next section). See
[research/G2_csp_h1b/REPRODUCTION.md](research/G2_csp_h1b/REPRODUCTION.md).

## Phase Gamma — H1b-Gamma-2, sampling robustness (2026-07-03, N=5 seed batches, n=52 each)

Seed as the sole independent variable (`seed_offset ∈
{0,1000,2000,3000,4000}`, attempt seed = offset + attempt), N=5
pre-registered confirmatory batches. Positive control: offset 0
reproduced Gamma-1 bit-for-bit before anything else was trusted.

| Seed offset | Δ (pts) | McNemar p | Variation B2/B3 | Gate | False-cert |
|---|---|---|---|---|---|
| 0 (=Gamma-1) | +3.85 | 0.79 | 0.79 / 1.00 | **PASS** | 0 |
| 1000 | 0.0 | 1.00 | 0.00 / 0.00 | FAIL | 0 |
| 2000 | 0.0 | 1.00 | 0.00 / 0.00 | FAIL | 0 |
| 3000 | −3.85 | 0.50 | 0.05 / 0.00 | FAIL | 0 |
| 4000 | −3.85 | 0.50 | 0.05 / 0.00 | FAIL | 0 |

**Verdict: robustness Supported** — no seed produces a guided advantage
near the kill threshold (Δ≥7, p<0.05). Two qualifications, both recorded:
only batch 0 satisfies the Behaviour Variation Gate, so it is the only
valid H1b measurement (the other four show the mechanism was not
exercised); and the gate itself is seed-fragile (1 pass / 4 fail —
PC-2026-07-03b). 0 false certifications across all 10 arm-runs — the most
robust property measured. Full report:
[research/G2b_sampling_robustness/RESULTS.md](research/G2b_sampling_robustness/RESULTS.md).

## Gamma+1 — Certificate Independence, edge_ai (2026-07-03, n=60)

An independently-written checker (brute-force enumeration, no pruning,
imports nothing from the solver's search) rechecked every dev certificate
the production pipeline produces.

| Comparison | Result |
|---|---|
| Primary (pruned DFS) vs independent (brute force) | **60/60 agree** |
| Independent optimum vs benchmark ground truth | **60/60 match** |
| False certifications under independent check | **0** |
| Positive control (true optimum) | accept |
| Negative controls (inflated / infeasible / suboptimal) | all reject |

**Certificate Independence (edge_ai): Partial → Supported** —
implementation- and oracle-independent, not paradigm-independent; native
format, dev split. Full report:
[research/G3_cert_independence/RESULTS.md](research/G3_cert_independence/RESULTS.md).

## Gamma+2 — Certificate Independence, constraint_csp (2026-07-03, n=52)

CSP analogue: independent checker differing on two axes (backtracking DFS
with incremental pruning vs generate-then-filter; separately-written
evaluator), covering both certificate types (42 SAT, 10 UNSAT).

| Comparison | Result |
|---|---|
| Primary (shared logic) vs independent (backtracking) | **52/52 agree** |
| Independent full-enumeration count vs ground-truth `solution_count` | **52/52 match** |
| False certifications under independent check | **0** |
| Positive controls (true SAT assignment, true UNSAT conflict) | both accept |
| Negative controls (violating assignment / false conflict / non-minimal) | all reject |

**Certificate Independence (constraint_csp): Partial → Supported** — both
validated verticals now carry Supported correctness AND Supported
independence. Full report:
[research/G3_cert_independence/RESULTS_CSP.md](research/G3_cert_independence/RESULTS_CSP.md).

## Scientific state snapshot (2026-07-03 — SUPERSEDED; live state is `docs/SCIENTIFIC_STATE.md`)

| | Status |
|---|---|
| Architecture | Locked |
| Certificate Correctness | ✓ (negative controls + cross-validated against benchmark's independent ground truth) |
| Certificate Independence | Partial (recheck shares `_check()`/`_enumerate_solutions()`/search logic with the solver in both verticals — a second, independently-written checker would close this) |
| H1a | Negative, configuration-specific, internally reproduced |
| H1b-Gamma-1 | Provisional — rejected by registered decision rule, 0/3 pre-registered reruns completed |
| Internal Reproduction | Deterministic: ✓ · Stochastic: 0/3 (not yet established) |
| Independent Reproduction / Replication / External Validation | Not established |

## Validation Phase 1 — first contract-valid result (2026-07-02, n=60)

Deterministic solver + optimality-certifying verifier (contract v1.0),
native `edge_ai_deployment` dev set, fully offline, peak RSS 27.6 MB.

| System | Coverage (Verified) | False Certification | Verified-Correct |
|---|---|---|---|
| Intervention 2 (LLM attempter) | 5% (all wrong) | 5% | **0%** |
| **Validation Phase 1 (solver + cert)** | **100%** | **0%** | **100%** |

First Verified-Correct > 0 under the locked contract — saturating, at zero
false certification. Every Verified answer carries a re-checkable
optimality certificate; the checker provably rejects feasible-but-
suboptimal answers (the exact H1-invalidating bug). Scope: structured
inputs where 1B formalization is 100%; degrades on unstructured phrasing.
**Decision: KEEP.** Full report: [research/V1_validation/RESULTS.md](research/V1_validation/RESULTS.md).

## H0 — formalization accuracy (measured 2026-07-02, n=60, llama3.2:1b)

| Metric | Value | vs threshold (≥90%) |
|---|---|---|
| Overall Schema Accuracy | 74.0% | below |
| Unit Normalization Accuracy | **28.3%** | well below — worst metric |
| Variable Extraction Accuracy | 83.2% | below |
| Numeric Extraction Accuracy | 72.3% | below |
| Field Association Accuracy | 93.1% | at/near |
| Constraint Extraction Accuracy | 66.7% | below |

Decision: **PIVOT** to deterministic parser-first extraction (Stage B).
Full report: [research/H0_formalization/RESULTS.md](research/H0_formalization/RESULTS.md).
H1 and H3 both blocked on this clearing threshold — see `whitepaper/HYPOTHESES.md`.

## Intervention 1 — parser-first extraction (measured 2026-07-02)

| Metric | Baseline | Intervention 1 | Δ |
|---|---|---|---|
| Overall Schema Accuracy | 74.0% | **100%** | +26.0pts |
| Unit Normalization Accuracy | 28.3% | **100%** | +71.7pts |
| Fabricated / Missing / Swapped (counts) | 112 / 54 / 29 | 0 / 0 / 0 | -195 total |
| LLM fallback engaged | — | 0/60 | untested path |

~~Decision: KEEP~~ — **superseded, see validation below.**
Full report: [research/I1_parser_first/RESULTS.md](research/I1_parser_first/RESULTS.md).

## Intervention 1 validation under paraphrase (measured 2026-07-02)

| Metric | Own format | L1 (format) | L2 (prose) | L3 (mixed) |
|---|---|---|---|---|
| Overall Schema Accuracy | 100% | 86.0% | 93.7% | **52.8%** |
| Parser Success Rate | 100% | **0%** | **0%** | **0%** |
| LLM Fallback Rate | 0% | 100% | 100% | 100% |

**Decision: DEFER.** Parser Success Rate is 0% on all 3 paraphrase
levels, including formatting-only changes — the regex is literal, not
semantic. Fallback engaged correctly every time (no crashes) but its
accuracy is presentation-dependent, dropping to 52.8% when catalog
entries appear as prose asides rather than lists/tables (0/30 extracted
in a targeted check vs 13/20 for the same data in table form). H0/H1/H3
dependency: **still blocked** — the 100% result holds only for the
benchmark's exact phrasing. Full report: [research/I1_validation/RESULTS.md](research/I1_validation/RESULTS.md).

## Intervention 1B — structure detection + extractors (measured 2026-07-02)

| Level | 1A validation | **1B** | Parser Success (1A→1B) |
|---|---|---|---|
| L1 (formatting) | 86.0% | **100%** | 0% → **100%** |
| L2 (prose) | 93.7% | **100%** | 0% → **100%** |
| L3 (mixed) | 52.8% | **88.9%** | 0% → **100%** |

**Decision: KEEP — Intervention 1 complete.** Deterministic path now
handles all 3 paraphrase levels with 0% LLM fallback and 0 fabrication.
L3's residual 11% is one diagnosed segmentation edge case (prose asides
sharing an unsplit region with a table → extractor correctly refuses to
guess), deliberately not chased to avoid template-overfitting. Gains on
template-generated paraphrases are a lower bound on real-phrasing
robustness, not proof. Full report: [research/I1b_structure/RESULTS.md](research/I1b_structure/RESULTS.md).

## Intervention 2 — H1 measured (2026-07-02, n=60, StructuredFormalizer)

| Arm | Verified-Correct | False Verification | Mean Attempts | Mean Latency |
|---|---|---|---|---|
| B2 (blind) | 0.0% | 5.0% | 2.90 | 4.28s |
| B3 (guided) | 0.0% | 5.0% | 2.95 | 4.24s |

Δ=0.0, McNemar p=1.0 — perfectly indistinguishable. **Decision: DEFER**
(not DELETE — see full reasoning in [research/H1_edge_ai/RESULTS.md](research/H1_edge_ai/RESULTS.md)).
97-99% of all attempts in both arms fail identically on
`constraint_violation`; every Verified label in the run was a false
verification (Verifier checks feasibility, not optimality — a scope gap,
not a formalization or arithmetic bug). Both confounds swamp any room
for the policy mechanism to show a difference.

## H1 — the bet, as one number (not two rows to mentally subtract)

`policy=None` (B2) vs `policy=DeterministicPolicy()` (B3), same kernel,
same executor, same verifier — see `kernel/loop.py`. Metric is
**verified-correct rate** (Verified label AND `benchmark.metrics.grade()`
agrees), not bare solve rate, so a policy can't win by guessing more
without any of it being properly verified. Decision by
`compare_paired` (McNemar), never raw subtraction.

| Arm | Verified-Correct Rate | n | McNemar p | Δ (B3−B2) | Verdict |
|---|---|---|---|---|---|
| B2 (blind retry) | ? | ? | — | — | — |
| B3 (guided retry) | ? | ? | ? | ? | ? |

Kill threshold (`whitepaper/HYPOTHESES.md` H1): Δ ≥ 7pts, p < 0.05.
Verdict labeled "Edge AI Optimizer only" until measured on ≥2 categories.
