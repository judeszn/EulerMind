# FINAL SUBMISSION AUDIT — 2026-07-04

Auditor stance: a judge with 750 submissions and five minutes, who has
never met us. Every verdict below is backed by an artifact, a CI run, or
a direct test — nothing is "should work."

## Verdicts

| Area | Verdict | Evidence |
|---|---|---|
| Repository (structure, docs, license, hygiene) | **PASS** | Template files + LICENSE (MIT) + KNOWN_LIMITATIONS + CHANGELOG + release README; `model/.gitkeep` tracked (gitignore negation fixed); no stray files |
| Template compliance | **PASS** | Required structure exact; metadata valid JSON; prompts = 2; `*.gguf` ignored; download script idempotent/public/path-matched |
| Profiler | **PASS** | Green on the release-candidate commit itself (run 28693918832, clean x86); baseline archived (15.68 TPS, 1,699 MB, fraud-check pass) |
| Offline | **PASS** | Demo is stdlib-only (verified standalone inside the submission repo); inference is llama.cpp-local; zero network at solve time |
| 8 GB | **PASS** | 1,699 MB peak measured — ~24% of the 7 GB scoring budget |
| Demo | **PASS** | One command from repo root; all 3 example buttons Verified *from inside the submission repo* (Lagos 30+30/₦345,000, Nairobi valid assignment, edge-AI KNN×3+SVM×2/3249); out-of-domain → honest Open |
| Metadata | **PASS except one field** | All truthful; `team_id` placeholder is the registered external blocker, loudly marked |
| REPORT | **PASS** | Every number run-ID-cited; dual TPS figures explicitly reconciled; scope-honesty paragraph present |
| README | **PASS** | Cold-read optimized: value + numbers + 60-second quickstart above the fold; trust labels explained; limitations linked; no marketing language |
| Consistency (numbers/links/commands/filenames) | **PASS** | 192/192 recomputed from frozen reports before use; 15.02 vs 15.68 reconciled in-table; all commands re-executed during this audit; repo links resolve |
| Screenshots | **PENDING — user** | Staging ready (demo + example buttons); not a repository defect |
| Video | **PENDING — user** | Script + walkthrough + judge Q&A pivots ready; not a repository defect |
| Devpost consistency | **PENDING — user** | Form still carries old draft prompts + empty score field; correct values ready to paste (metadata.json, DEVPOST_STORY.md); score field blocked on organizer Q4 |
| Submission readiness | **See status** | — |

## Remaining blockers — all external or human, none in the repository

1. ADTF **team_id** → one field, one commit (user registration)
2. **Organizer answer** on the "Self Reported Profiler Score" field (email + Discord, drafted)
3. **Devpost form updates** (prompts + story paste — 10 min)
4. **Screenshots + 2-minute video** (user; all scripts/staging prepared)
5. **Go-public — BOTH repos** (submission + research; red-team Critical finding #1: all evidence links target the research repo, which is also private)
6. **Devpost submit** (before Aug 25, 2026 07:45 GMT+1)

## Release status

# ✅ READY FOR SUBMISSION

Per the registered rule: this status is assigned because **every
remaining blocker is external** (team ID, organizer response, Devpost
form work, recording, public release, submit). No repository issue
remains. The repository a judge will clone runs its own demo in one
command, certifies its own registered test prompts, carries its own
profiler baseline produced by its own CI, and states its own
limitations before anyone has to find them.
