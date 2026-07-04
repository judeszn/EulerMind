# Red-team review — trying to reject EulerMind (2026-07-04)

Stance: ADTC judge, 750 submissions, 5–10 minutes, actively looking for
reasons to score this lower. Every attack was executed, not imagined.

## Findings

| # | Severity | Finding | Evidence | Resolution |
|---|---|---|---|---|
| 1 | **Critical** | **The research repo — target of every evidence link in REPORT/README/Devpost story — is PRIVATE.** A judge today hits 404 on the entire evidence base: experiment history, 192/192 reports, CI runs. The checklist tracked go-public for the submission repo only; nobody registered the research repo's flip | `gh repo view judeszn/EulerMind` → PRIVATE (checked, not assumed) | **Registered**: go-public step now covers BOTH repos, as one deliberate pre-submission action (user-owned; not flipped unilaterally — publishing is the user's act). Checklist + audit updated |
| 2 | Major → cleared | Fresh-clone demo appeared to fail during testing | zsh multibyte quoting error in the *test harness*; re-tested with a clean Python HTTP client against a fresh clone: Lagos → Verified, and control-character/unicode garbage input → graceful Open, no crash, empty error log | Product cleared; harness was at fault. The retest added a robustness data point (hostile input handled) |
| 3 | Minor → fixed | CI run IDs cited as bare numbers — a judge can't reach the evidence without manually searching Actions | REPORT.md benchmarks table | Fixed: all four run IDs are now hyperlinks (commit c0cea2f) |
| 4 | Minor | Model URL is third-party (bartowski on HF) — could theoretically move before judging | HEAD request today: 206, alive; proven across 4 CI downloads | Accepted risk; mitigation if paranoid: mirror weights to a GitHub Release asset (template-sanctioned option). Not done — adds a 1 GB artifact to maintain for a low-probability event |
| 5 | Minor | `language_scope: ["en"]` alongside `african_alpha_claim: true` — a rushed judge might conflate use-case bonus with language capability | metadata.json | Defensible as-is (the bonus is *use case*, and REPORT's African paragraph makes the pairing load-bearing); wording already precise. No change |
| 6 | Minor | Vendored `app/` has no automated sync-check against the research kernel | By construction | Mitigated by the code freeze + provenance headers pinning the source commit; a cross-repo diff in CI would add complexity for a risk the freeze already controls. Documented, not built |
| 7 | Minor | Demo answers show bare numbers ("maximum profit 345000") while prompts use currency ("N4,500") | UI output | Cosmetic; readable either way. Not worth breaking the code freeze |
| 8 | Non-issue (checked) | Could the CSP demo hang trying its LLM fallback offline? | Vendored formalizer attempts localhost Ollama only on benchmark-family texts with unparsed constraint lines; connection-refused fails fast inside try/except → honest Open | Verified acceptable; no hang path |

No other issues found after attacking: README commands (re-executed from
fresh clone), number consistency (192/192 recomputed from frozen
reports; dual TPS figures reconciled in-table), template compliance
(structure re-diffed), metadata JSON validity, .gitignore behavior
(`model/.gitkeep` tracks), REPORT length (~2.5 pp, within the 1–3 ideal).

## Top 10 reasons a judge would rank this highly

1. Clone → one command → working certified demo, zero dependencies (verified on a fresh clone).
2. 0% false certification, 192/192 dual-checker agreement — one click from claim to artifact.
3. The two-theorem independence story (duality vs. vertex enumeration) — memorable and technically unusual.
4. It refuses honestly: out-of-domain → Open, on screen, as a feature.
5. Model chosen by a selection rule committed *before* the accuracy data existed — visible anti-cherry-picking.
6. The official profiler runs in the submission repo's own CI; the baseline judges compare against was made on audit-like hardware.
7. Byte-identical cross-OS/arch reproduction, re-confirmed on every push.
8. The African use case is load-bearing: the registered prompts *are* the certified domains.
9. 1.7 GB peak — ~24% of the RAM budget — with headroom the S_eff formula pays for directly.
10. A pre-registered hypothesis died and the repo says so — rare integrity signal.

## Top 10 reasons a judge might score it lower

1. The automated accuracy share rides on a 1.5B model (68% GSM8K) — larger-model submissions may outscore it there.
2. S_perf exposure: ~15.7 TPS is hostage to TPS_max if a rival ships a tiny fast model (A-05 unknown).
3. Certification breadth: three problem families; most arbitrary questions get a non-Verified label.
4. Closed phrasing families — paraphrases outside the two families formalize to Open, which a judge could read as brittleness rather than honesty.
5. The verification layer is invisible to the automated benchmarks (World A) — its value is entirely qualitative unless A-02 says otherwise.
6. n=50 accuracy sampling is selection-grade, not leaderboard-grade (disclosed, but still thin).
7. English-only language scope in an African-language-themed competition environment.
8. No physical-laptop thermal measurement (cloud CI only; disclosed).
9. The demo UI is deliberately minimal — polishless next to flashier rivals.
10. Single-person team — breadth of report/video/demo polish competes for one person's hours.

## Risk assessment

**Compliance risk: LOW** — everything the template requires exists,
validates, and runs; the only compliance gap (team_id) is a known
external. **Competitive risk: MEDIUM** — the automated score is capped
by model size and TPS_max dynamics we don't control; the submission's
differentiation is concentrated in the qualitative half, which is
exactly where its evidence density and honesty are strongest.

## Confidence

**Ready for judging: YES — high confidence (with the two conditions
registered).** The rejection attempt failed on substance: the one
Critical finding (private evidence repo) is procedural and now
checklisted; the one apparent functional failure was the tester's
harness, and disproving it added evidence of robustness. Conditional on
the user completing the external items — including the now-registered
**dual** go-public — this repository survives a hostile five-minute read.
