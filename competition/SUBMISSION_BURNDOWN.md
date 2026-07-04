# Submission burndown (SUBMISSION EXECUTION MODE)

_Last updated: 2026-07-04. Statuses: 🟩 can complete/completed now ·
🟨 waiting on organizer · 🟥 waiting on user._

## Reconciliation audit (every artifact pair checked)

| Mismatch | Where | Resolution |
|---|---|---|
| Devpost Test Prompts ≠ metadata.json | Devpost form has old drafts ("factory A/B", "five engineers") | 🟥 User pastes the Lagos/Nairobi prompts from submission-repo metadata.json (5 min) |
| Devpost "Self Reported Profiler Score" has no source | Profiler emits no overall score (schema verified; template REPORT.md confirms audit-side scoring) | 🟨 Q4 in organizer email; leave empty |
| ~~Shipped test prompts don't parse in our own certified pipeline~~ | metadata.json prompts vs formalizers | 🟩 **FIXED** (authorized final engineering sprint, 2026-07-04): formalizers extended with a second closed phrasing family (natural SME prose) rather than dumbing the prompts down. Both prompts now certify end-to-end (Lagos: Verified, 30+30, ₦345,000 exact match to hand-solve; Nairobi: Verified assignment, both checkers accept). Full regression green: selftest ✓, D1 9/9 ✓, LP 80/80 exact ✓, D3 reproduction bit-identical ✓, new D5 tests 4/4 ✓. Prompts added as demo example buttons. **Code frozen from here.** |
| Research README said "Phase 0 (this repo, now)" | Judge-visible via REPORT.md link | 🟩 **Fixed** — current-state summary + demo quickstart added |
| smoke_submission carries SMOKE labels | competition/smoke_submission (research repo) | Intentional and correctly labeled — harness, not submission. No action |
| REPORT.md numbers vs evidence | — | 🟩 Verified before writing (192/192 recomputed; run IDs cited). No mismatch found |
| metadata.json vs download_model.sh vs submission.json | model name/path/quant consistent; baseline from CI | 🟩 Consistent (profiler fraud-check params_match=true) |

## Burndown board (by blocking priority)

| Task | Status | Owner | ETA | Blocks submission? | Evidence |
|---|---|---|---|---|---|
| ADTF portal registration → team_id into metadata.json | 🟥 | User | ~10 min + 1 commit | **YES** (template: zero placeholders) | placeholder in metadata.json |
| Send organizer email (4 Qs) + Discord post | 🟥 | User | 15 min | YES via profiler-score field | ORGANIZER_EMAIL_DRAFT.md |
| "Self Reported Profiler Score" value | 🟨 | Organizers | unknown | **YES** (required form field) | Investigation in SUBMISSION_CHECKLIST.md |
| Fix Devpost test prompts (mirror metadata.json) | 🟥 | User | 5 min | YES (prompts are scored) | Screenshot vs metadata.json |
| Record 2-min video | 🟥 | User | ~half day | **YES** (required) | 🟩 Script ready: VIDEO_SCRIPT.md |
| Screenshots | 🟥 | User | ~30 min | YES (required) | 🟩 Staging ready: `python3 -m app.local_demo`, use example buttons; shots: pipeline-verified, Open-refusal, CI-green |
| Devpost story/overview | 🟥 (paste) | User | 10 min | YES (form fields) | 🟩 Draft ready: DEVPOST_STORY.md |
| Local demo entry point | 🟩 **DONE** | — | — | no (but feeds video/screenshots) | app/local_demo.py — stdlib-only, tested: 3 domains Verified (0.3–5.2 ms), refusal path Open, HTTP smoke green |
| Research-repo README refresh | 🟩 **DONE** | — | — | no (judge-visible) | README.md updated |
| Submission repo core (structure/scripts/REPORT/profiler/baseline) | 🟩 **DONE** | — | — | — | CI run 28691529653 green; baseline archived |
| Flip submission repo public | 🟥 | User | 1 min | **YES** — the submission act | deliberate, last |
| Devpost final submit | 🟥 | User | 5 min | **YES** | after all above |

## Summary

- **Completion: 14 of 19 tracked items done with evidence (~74%);
  all remaining items are human-action or organizer-answer.**
- **Critical blockers (4):** team_id · profiler-score definition ·
  video recording · go-public+submit. (Under the 5-blocker limit.)
- **Next three actions (all user, ~30 min total):** ① send the email +
  Discord post ② register on the ADTF portal ③ fix the two Devpost
  prompt fields.
- **Estimated remaining effort:** user ~1 day (dominated by video);
  assistant ~2–4 h contingency (organizer-answer follow-ups, screenshot
  staging help, prompt/formalizer reconciliation if World B).
- **Risk level: LOW-MEDIUM.** Single unhedged risk: the profiler-score
  field's meaning (organizer-controlled). Everything else has evidence
  or a trivial path.
- **Could we submit today if organizers replied immediately? YES** —
  with team_id + score answer in hand, remaining work is: one commit,
  two form pastes, screenshots, one video, two clicks.
