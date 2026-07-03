# Submission gap analysis — the execution board (Sprint Δ0)

Statuses are honest: ✅ done · 🔶 in progress · ❌ not started · ❓ unknown/blocked-on-answer.
No percentage bars — a status either has an artifact behind it or it doesn't.

## Submission requirements (from the official template, verified 2026-07-03)

| Requirement | Status | Evidence / next action |
|---|---|---|
| Public GitHub repo | ✅ | github.com/judeszn/EulerMind (verify visibility setting before submitting) |
| Fork/derive from official template structure | 🔶 | `competition/smoke_submission/` created for CI smoke; the REAL submission repo layout decision (this repo restructured vs separate repo) is open |
| `metadata.json` fully filled, no placeholders | ❌ | team_id requires ADTF portal registration — user action |
| Exactly 2 test prompts (math domain) | 🔶 | Smoke pair drafted; final pair should be African-SME-themed math problems (African bonus is load-bearing here) |
| `download_model.sh` → public GGUF URL | 🔶 | Smoke version uses template's SmolLM2 default; final version awaits model selection |
| Model choice (GGUF) | ❌ | Blocked on CI leaderboard measurements — see MODEL_CANDIDATES.md |
| `REPORT.md` (problem, design, constraints, benchmarks) | ❌ | The one place the entire Gamma/Delta evidence base earns S_acc credit — biggest writing task remaining |
| 2-minute video | ❌ | User records; script derivable from demo/speaker_notes.md after model selection |
| Profiler passes locally (Gate 1) | ✅ | Full official pipeline green end-to-end on CI x86 (run 28683560689): download → llama-bench → memory/thermal sampling → schema-valid submission.json. Evidence: `smoke_submission_report_ci_28683560689.json` |
| `submission.json` with measured numbers | 🔶 | Smoke model measured (SmolLM2-135M: 91.77 TPS, 0.19 GB peak). Final numbers await model selection. **Bonus finding: the audit runs on a cloud VM (`measured_on: audit_cloud_vm` in the profiler), so CI-VM numbers are likely *closer* to audit numbers than a physical laptop's would be — the drift-tolerance mitigation is stronger than designed** |
| Audit-drift safety (±25% TPS / ±15% RAM) | 🔶 | Mitigation designed: measure on CI x86 4vCPU (audit-like), not arm64 dev machine |
| OOM-proof under 8 GB | ❓ | Candidate models are 0.1–2.3 GB — low risk, but confirmed only by measurement |
| Registered on ADTF portal (team_id) | ❓ | User action — needed before metadata.json can be finalized |
| Discord joined / knowledge session | ❓ | User action |
| Official math validation set obtained | ❌ | Devpost says "validation sets are provided for each [domain]" — locate via portal/Discord; re-anchors the accuracy proxy |

## Open questions that change strategy (ask organizers — email/Discord)

1. **How are `test_prompts` responses generated for judging — bare GGUF
   through llama.cpp, or the submission's application code?** The
   profiler never generates prompt responses; the mechanism is outside
   it. If bare model: EulerMind's kernel earns credit only via
   REPORT/video/demo. If application: the kernel can answer the prompts
   with certified answers — a decisive differentiator. This single
   answer reshapes where polish effort goes.
2. **Is S_perf's denominator truly max-observed TPS, or the
   TPS_REFERENCE=15 anchor?** Determines whether S_perf is adversarially
   exposed (see TARGETS.md scenarios).
3. `model.packaging: docker_build_from_repo` exists in the metadata
   schema — what runs inside it at audit time, and may it wrap inference?

## What is deliberately NOT on this board

- D4 (calculus vertical), H4, H5, website, desktop app — paused per Δ0's
  premise: no research/feature work until it passes the decision matrix
  in docs/SCORING.md against these measured gaps.
- The research evidence base itself — complete, frozen, and feeding
  REPORT.md; it needs no new work to be citable.
