# ADTC 2026 submission checklist (Sprint Δ2)

Submission repository: **github.com/judeszn/eulermind-adtc-submission**
(private until the deliberate go-public step below). Statuses honest;
an item is ✅ only with an artifact behind it.

## Repository artifacts

| Item | Status | Notes |
|---|---|---|
| Template-conformant structure (metadata.json, download_model.sh, REPORT.md, model/, .gitignore) | ✅ | Matches the official template's required file structure exactly |
| metadata.json valid JSON, all fields truthful | ✅ except one | **`team_id` = REPLACE-WITH-ADTF-TEAM-ID — blocked on user registering at the ADTF portal. The template requires zero placeholders at submission time** |
| 2 test prompts, math domain, African-SME framed, certified-vertical shaped | ✅ | LP production mix (Lagos), CSP assignment (Nairobi); both hand-verified solvable with unique/valid answers; no simulated-tool prompting per PROMPT_STRATEGY.md |
| african_alpha_claim = true with load-bearing pairing | ✅ | operations_research; description ties the pipeline to SME planning as the product's purpose |
| download_model.sh idempotent, public URL, path matches _runtime | ✅ | Qwen2.5-Math-1.5B Q4_K_M via bartowski (URL already proven in 2 CI runs) |
| *.gguf and model/ gitignored | ✅ | |
| REPORT.md — every claim traceable | ✅ | Every number verified against committed evidence before writing (192/192 certs, 0% false-cert, 15.02 TPS, 1700MB, 68% GSM8K, run IDs cited) |
| Official profiler passes on the repo | 🔶 | CI run 28691529653 in progress at time of writing — baseline submission.json committed once green |
| submission.json baseline archived | 🔶 | From the CI workflow (clean x86 runner), not a dev machine |

## Human-only items (nobody else can do these)

| Item | Owner | Notes |
|---|---|---|
| Register on ADTF portal → real team_id into metadata.json | **User** | Blocks final submission, nothing else |
| Join Discord; attend knowledge session | **User** | Also: locate the official math validation set |
| Send organizer email (competition/ORGANIZER_EMAIL_DRAFT.md) | **User** | A-02/A-05 answers can reopen the model choice and reshape prompt strategy |
| Screenshots of the build in action | **User** (script/staging: assistant) | Devpost requirement |
| 2-minute video | **User** (script: assistant, Δ4) | Devpost requirement |
| Flip submission repo to **public** | **User** | This IS the submission act — deliberate, last |
| Submit repo URL on Devpost | **User** | Before Aug 25, 2026 07:45 GMT+1 |

## Deliberately deferred (with reopening triggers)

- `packaging: binary_bundle` → switch to `docker_build_from_repo` only
  if A-02/A-08 resolve to "application is judged" (World B) — that's
  also the trigger to wire the EulerMind pipeline into the submission
  as the answering application.
- Model choice reopens automatically if A-05 = "max observed across
  teams" (deepseek is the ranked alternate; see MODEL_CANDIDATES.md).
