# ADTC 2026 Submission Dashboard (Submission Manager Mode)

**The living document.** Flow is one-directional: research repo →
submission repo → profiler → Devpost. Nothing is 🟩 without evidence.
Statuses: ⬜ Not Started · 🟨 In Progress · 🟩 Complete · 🟥 Blocked · ⏸ Deferred.
Ordered by criticality.

## Critical path (blockers first)

| Requirement | Official source | Status | Evidence | Owner | Blocking dependency | Next action |
|---|---|---|---|---|---|---|
| Self Reported Profiler Score (Devpost, required) | Devpost form ("Enter the score from the profiler") | 🟥 | Profiler schema has NO overall score field (top-level: schema_version/profiler_version/submission/environment/throughput/memory/accuracy/cpu_thermal/reproducibility); only `accuracy[].score` exists; template REPORT.md: "Official scores are measured by the ADTC profiler on the standard evaluation machine"; released accuracy path fails as shipped (A-12) | Organizers ← User | Organizer answer to email Q4 | **User sends email + posts Q4 in Discord. Leave the field empty until answered. Do not infer.** |
| ADTF team_id → metadata.json | Template field reference ("Your unique team ID as registered on the ADTF portal") | 🟥 | `metadata.json` carries loud placeholder | User | ADTF portal registration (~10 min) | Register, then replace placeholder in submission repo (one commit) |
| Devpost Test Prompts 1 & 2 mirror metadata.json | One-directional flow rule; template rule 7 (prompts are scored) | 🟨 | Screenshot 2026-07-04 shows OLD draft prompts ("factory products A and B" / "five engineers Alice, Ben…") — not the shipped Lagos LP / Nairobi CSP prompts | User (~5 min) | none | Copy both prompts verbatim from submission repo `metadata.json` → Devpost form |
| 2-minute demo video | Devpost "What to Submit" | ⬜ | — | User (script: assistant) | Model + prompts final (done); script not yet written | Assistant drafts script from REPORT.md + demo scenes; user records (~half day) |
| Screenshots of build in action | Devpost "What to Submit" | ⬜ | — | User (staging: assistant) | none | Assistant stages terminal/pipeline captures; user screenshots (~1 h) |
| Devpost project overview + story | Devpost form | ⬜ | Domain dropdown already correct (screenshot) | User (draft: assistant) | none | Assistant drafts from REPORT.md; user pastes (~1 h) |
| Repo public at evaluation | Template rule 1 | 🟩 | Both `EulerMind` and `eulermind-adtc-submission` confirmed public (`gh repo view`, 2026-07-08) | — | — | — |
| Devpost final submit (repo URL) | Devpost | ⬜ | — | User | All above | Before Aug 25, 2026 07:45 GMT+1 |

## Submission repository (github.com/judeszn/eulermind-adtc-submission)

| Requirement | Official source | Status | Evidence | Owner | Blocking dependency | Next action |
|---|---|---|---|---|---|---|
| Template file structure | Template README "Required File Structure" | 🟩 | Repo matches exactly (metadata.json, download_model.sh, REPORT.md, model/, .gitignore) | — | — | — |
| metadata.json truthful, valid | Template field reference | 🟨 | Valid JSON, all fields real except team_id | User | team_id (above) | — |
| Exactly 2 test prompts, domain-appropriate | Template rule 7 | 🟩 | Lagos LP (hand-verified: unique optimum 30+30, ₦345,000) + Nairobi CSP (hand-verified solvable); PROMPT_STRATEGY compliant | — | — | — |
| download_model.sh idempotent, public, path-matched | Template rules | 🟩 | Green in CI run 28691529653 (and 2 prior runs of same URL) | — | — | — |
| *.gguf / model/ gitignored | Template rule 2 | 🟩 | .gitignore in repo | — | — | — |
| REPORT.md (problem/design/constraints/benchmarks) | Template README | 🟩 | Written; every number verified against committed evidence (192/192 recomputed, run IDs cited) | — | — | Revisit only if organizer answers change claims |
| Official profiler passes (Gate 1) | Template "Local Testing" | 🟩 | CI run 28691529653 green: 15.68 TPS, 1,699 MB, fraud-check pass, no throttle | — | — | — |
| submission.json baseline archived | Audit comparator (±25%/±15%) | 🟩 | `baseline_submission_ci_28691529653.json` in submission repo, produced on clean x86 CI | — | — | — |
| accuracy[] populated in submission.json | Unclear — schema requires the key (empty array is schema-valid; `--skip-accuracy` path is the template's own smoke instruction) | 🟥 | Baseline has `accuracy: []`; released accuracy path broken as shipped (A-12/A-13) | Organizers ← User | Q4 answer | If organizers expect a populated accuracy row, use our working llama-server invocation (proven in run 28684426883) |
| packaging value (binary_bundle vs docker_build_from_repo) | metadata schema | ⏸ | binary_bundle shipped | — | A-02/A-08 answer | Switch + wire pipeline as answering app only if World B confirmed |

## Competition requirements

| Requirement | Official source | Status | Evidence | Owner | Blocking dependency | Next action |
|---|---|---|---|---|---|---|
| Offline execution (zero network at inference) | Template rule 3 | 🟩 | Pipeline stdlib+llama.cpp; D3 cross-OS reproduction | — | — | — |
| 8 GB compliance (OOM = DQ) | Template rule 5 | 🟩 | Peak 1,699 MB measured (24% of 7 GB budget) | — | — | — |
| llama.cpp only, GGUF | Template rule 4 | 🟩 | Q4_K_M through llama-bench; fraud-check params_match=true | — | — | — |
| African use case (bonus) | Devpost judging criteria | 🟩 (claim staged) | african_alpha_claim=true; load-bearing OR pairing; SME test prompts | Judges decide | — | Video/demo must show it |
| Open source | Devpost "What to Submit" | 🟩 | Both repos public (confirmed 2026-07-08) | — | — | — |

## Standing rules (this mode)

- No new architecture, verticals, or research hypotheses. Ship-first.
- Every Devpost edit flows FROM the submission repo, never the reverse.
- Unknown values are marked 🟥 with an acquisition path — never invented.
- Reopening triggers stand: A-05 → model choice; A-02/A-08 → packaging.

## Reconciliation audit (2026-07-04, merged from archive/SUBMISSION_BURNDOWN.md)

Every artifact pair checked for mismatch:

| Mismatch | Where | Resolution |
|---|---|---|
| Devpost Test Prompts ≠ metadata.json | Devpost form has old drafts ("factory A/B", "five engineers") | 🟥 User pastes the Lagos/Nairobi prompts from submission-repo metadata.json (5 min) |
| Devpost "Self Reported Profiler Score" has no source | Profiler emits no overall score (schema verified; template REPORT.md confirms audit-side scoring) | 🟨 Q4 in organizer email; leave empty |
| ~~Shipped test prompts don't parse in our own certified pipeline~~ | metadata.json prompts vs formalizers | 🟩 **FIXED** (2026-07-04): formalizers extended with a second closed phrasing family (natural SME prose). Both prompts now certify end-to-end (Lagos: Verified, 30+30, ₦345,000 exact match to hand-solve; Nairobi: Verified assignment, both checkers accept). Full regression green: selftest ✓, D1 9/9 ✓, LP 80/80 exact ✓, D3 reproduction bit-identical ✓, D5 tests 4/4 ✓. |
| Research README said "Phase 0 (this repo, now)" | Judge-visible via REPORT.md link | 🟩 **Fixed** — current-state summary + demo quickstart added |
| smoke_submission carries SMOKE labels | competition/smoke_submission (research repo) | Intentional and correctly labeled — harness, not submission. No action |
| REPORT.md numbers vs evidence | — | 🟩 Verified before writing (192/192 recomputed; run IDs cited). No mismatch found |
| metadata.json vs download_model.sh vs submission.json | model name/path/quant consistent; baseline from CI | 🟩 Consistent (profiler fraud-check params_match=true) |

**Summary as of 2026-07-04:** 14 of 19 tracked items done with evidence
(~74%); all remaining items are human-action or organizer-answer.
Critical blockers (4): team_id · profiler-score definition · video
recording · go-public+submit. Next three actions (all user, ~30 min
total): send the organizer email + Discord post, register on the ADTF
portal, fix the two Devpost prompt fields.

**This board predates Sprint 4/5 product work (2026-07-05 onward — tutor
lane checker families, README rewrite, real-WAEC holdout run).** It
reflects submission-repo status as of 2026-07-04, not the current state
of this research repo; see [scoreboard.md](../scoreboard.md) for what has
moved since.
