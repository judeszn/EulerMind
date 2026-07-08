# competition/ — ADTC 2026 submission tracking

Everything here optimizes against the **actual** ADTC 2026 evaluation
pipeline — verified by cloning and reading the official
[submission template](https://github.com/Africa-Deep-Tech-Foundation/adtc-2026-submission-template)
and [profiler source](https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler),
not by interpreting the marketing page.

**The core verified fact this directory is built on:** the automated
score components (S_perf via `llama-bench`, S_eff via RAM sampling, the
automated share of S_acc via `lm_eval`) all run against the **bare GGUF
through llama.cpp**. EulerMind's certification kernel is not in that
path. Model selection decides the automated score; the kernel and the
evidence base decide the qualitative score. They are optimized
separately, on purpose.

Current status: `FINAL_SUBMISSION_AUDIT.md` — submission repo is
template-compliant; both repos are public (confirmed 2026-07-08);
remaining blockers are external/human (organizer answer, team ID, video,
screenshots). `WINNING_STORY.md` tracks optional further score-raising
work, not a submission blocker
(see the scope note at the top of each).

| File | What it is |
|---|---|
| `SUBMISSION_CHECKLIST.md` | The living submission dashboard — status of every template/Devpost requirement, by criticality |
| `FINAL_SUBMISSION_AUDIT.md` | Final per-area PASS/FAIL verdict on the submission repository |
| `ASSUMPTION_REGISTER.md` | Registry of unresolved scoring-rubric assumptions (A-01…A-13) |
| `ORGANIZER_EMAIL_DRAFT.md` | Ready-to-send questions to ADTF, tied to the assumption register |
| `RED_TEAM_REVIEW.md` | Self-adversarial review of the submission |
| `MODEL_CANDIDATES.md` | Model leaderboard — frontier scan + accuracy measurements, pre-registered selection rule |
| `MODEL_DECISION.md` | Full ratification memo for the selected model (qwen2.5-math-1.5b) |
| `PRODUCTION_SETUP.md` | Rebuild guide for the offline demo stack |
| `PROMPT_STRATEGY.md` | Locked prompt-design principles |
| `SIGMA2_TUTOR_EXPERIENCE_LOCK.md` | Locked tutor UI spec |
| `TARGETS.md` | Score targets, every number labeled [exact]/[measured]/[assumption] |
| `score_model.py` | S_total predictor. Self-testing: `python3 -m competition.score_model` |
| `select_model.py` | Model selection rule implementation |
| `DEVPOST_STORY.md`, `JUDGE_WALKTHROUGH.md`, `VIDEO_SCRIPT.md` | Devpost copy and live-demo scripts (overlap with `demo/speaker_notes.md` by design — same pitch, different formats) |
| `EVAL_GUARDRAIL_HARNESS_PRD.md` | PROPOSED, not built — the Σ1 tutor-eval harness referenced by `WINNING_STORY.md` |
| `reality_check_transcript.md`, `holdout_waec_realworld_dev_transcript.md` | Raw Q&A transcripts, evidence for `scoreboard.md`'s Sigma section |
| `smoke_submission/` | Template-conformant harness (SmolLM2-135M, the template's own default) for validating the official profiler end-to-end on CI. **Not the competition submission** — marked as such in its metadata |
| `archive/` | Superseded tracking docs, kept for history — see each file's header for what replaced it |

Measurement policy: all TPS/RAM numbers come from the GitHub Actions
x86 runner (4 vCPU, ~7 GB — closest available match to the ADTC Standard
Laptop and the audit VM), via `.github/workflows/adtc-profile.yml`
running the **official, unmodified** profiler. The arm64 dev machine's
numbers are never reported — the audit comparator's ±25%/±15% drift
tolerance makes cross-architecture self-reporting a flag risk.
