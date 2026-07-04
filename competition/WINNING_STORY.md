# The winning story (Horizon 1 — the only document that matters until Aug 25)

**Rule #1 (Guardrail Zero, CLAUDE.md — frozen since day one):** every
recommendation must increase the probability of winning ADTC 2026,
justified against the published judging criteria. Anything excellent for
the company but weak for the competition is marked Post-ADTC and lives
in `future/`, not here.

## The three questions that decide it

**1. Why does EulerMind beat another offline LLM?**
Not the model — everyone has the same open weights. Trust, measured:
it distinguishes what it **proved** (Verified — dual independent
checkers, 0% false certification across 192 certificates), what it
**checked** (Derived — the model's answer survived deterministic
substitution/numeric verification), what it can only **suggest**
(Heuristic — labeled), and what it **doesn't know** (Open — said
plainly). No offline chatbot in the field can put up those labels with
machinery behind them.

**2. What does a judge see in 90 seconds that nobody else demonstrates?**
Wi-Fi visibly off → paste a WAEC-style quadratic → steps stream from a
local 1.5B math model → *"✓ machine-checked: roots substitute
correctly"* → then a question past the verified edge → *"I cannot
verify this — treat it as guidance."* The honest refusal is staged on
purpose; it is the ten seconds that separate this from every chatbot.

**3. The sentence a judge should repeat afterward?**
*"On an ordinary 8 GB laptop with no internet, it knew exactly which of
its answers it had proved."*

## What still moves the score (nothing else does)

| # | Item | Owner | Why it scores |
|---|---|---|---|
| 1 | Finish Σ1: simultaneous-extraction hardening + classroom benchmark (~50 syllabus-authored SS1–SS3 questions, African contexts) run against the real Qwen2.5-Math GGUF via llama-server, **headline metric = confidently-wrong rate** | Assistant (needs BEGIN IMPLEMENTATION) | Turns the trust story into a number no rival can match; feeds REPORT + demo + use-case bonus |
| 2 | Admin blockers: organizer email (4 Qs), ADTF team_id, Devpost prompt/story paste | **User** | Unblocks the only unfillable required field; submission legality |
| 3 | Screenshots + 2-minute video (scripts ready), dual go-public, submit | **User** | The judged artifacts themselves |

Optional, strictly after #1 lands clean: the learner passport
(portable on-device evidence file — described honestly, no "encrypted"
claim without key management). Post-ADTC by constitution: everything in
`future/FOUNDER_CONSTITUTION.md`.

## The locked 50-day plan (decided 2026-07-04 — "no building yet" lock)

**Product name (locked): EulerMind — Offline Mathematics Companion.**
The verification engine is the technology; the companion is the product.

**The promise (locked copy rule):** the demo *accepts* any
secondary-school maths question and always says whether it could check
itself. It never claims to *solve* WAEC — coverage claims are
falsifiable by one judge question; the honesty claim is not. A stumped
EulerMind labeling itself honestly is the product working.

**Status correction on the record:** the "middle path" architecture
(free question box → certified lane → tutor lane → checker → honest
labels) shipped at commit 0d29f8e and is live. What remains is breadth,
hardening, measurement, and presentation — not a new direction.

| Wk | Work | Owner |
|---|---|---|
| 1 (now) | **User: organizer email + ADTF team_id + Devpost prompt/story paste (external latency — cannot wait).** Assistant: Σ1 hardening (simultaneous extraction, real-GGUF wiring via llama-server) | Both |
| 2–3 | Author 50 syllabus-aligned questions across ~10 topics (African contexts, no copyrighted papers) → measure vs real Qwen2.5-Math GGUF on CI x86 → expand to 100 with weak topics oversampled. Headline: **confidently-wrong rate**; per-topic table becomes the REPORT capability map | Assistant |
| 4 | Evidence-driven improvement ONLY where the benchmark points: routing, checking, extraction, prompting, explanations. **No fine-tuning. No new certified verticals unless the benchmark names one as cheap + high-yield** | Assistant |
| 5 | Polish + re-vendor to submission repo + REPORT/Devpost/video-script updated with measured numbers. Stretch (only if clean): learner passport, honestly described | Assistant |
| 6 | Screenshots, 2-minute video (staged honest-refusal beat mandatory), final audit re-run, dual go-public | User (scripts ready) |
| 7+ | **Buffer (~10 days). Submit well before Aug 25 07:45 GMT+1** | User |

**Locked non-goals until submission:** fine-tuning · new certified
verticals (absent benchmark evidence) · evolution engine · platform/OS
work · reopening strategy (constitution is parked) · any copy that
promises coverage instead of honesty.
