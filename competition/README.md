# competition/ — Sprint Δ0: the ADTC Winning Evaluation Framework

Everything here optimizes against the **actual** ADTC 2026 evaluation
pipeline — verified by cloning and reading the official
[submission template](https://github.com/Africa-Deep-Tech-Foundation/adtc-2026-submission-template)
and [profiler source](https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler)
(2026-07-03), not by interpreting the marketing page.

**The core verified fact this directory is built on:** the automated
score components (S_perf via `llama-bench`, S_eff via RAM sampling, the
automated share of S_acc via `lm_eval`) all run against the **bare GGUF
through llama.cpp**. EulerMind's certification kernel is not in that
path. Model selection decides the automated score; the kernel and the
evidence base decide the qualitative score. They are optimized
separately, on purpose.

| File | What it is |
|---|---|
| `score_model.py` | S_total predictor — exact where the formula is published (S_eff, P_thermal), explicitly parameterized where it is not (tps_max, s_acc). Self-testing: `python3 -m competition.score_model` |
| `TARGETS.md` | Score targets, every number labeled [exact]/[measured]/[assumption]; tps_max sensitivity scenarios |
| `MODEL_CANDIDATES.md` | The model leaderboard — facts filled, measurement cells empty until the CI profiler run fills them; pre-registered selection rule |
| `GAP_ANALYSIS.md` | The execution board — submission requirements with honest statuses, and the open questions for organizers that change strategy |
| `smoke_submission/` | Template-conformant harness (SmolLM2-135M, the template's own default) for validating the official profiler end-to-end on CI. **Not the competition submission** — marked as such in its metadata |

Measurement policy: all TPS/RAM numbers come from the GitHub Actions
x86 runner (4 vCPU, ~7 GB — closest available match to the ADTC Standard
Laptop and the audit VM), via `.github/workflows/adtc-profile.yml`
running the **official, unmodified** profiler. The arm64 dev machine's
numbers are never reported — the audit comparator's ±25%/±15% drift
tolerance makes cross-architecture self-reporting a flag risk.
