# Organizer email — ready to send (Sprint Δ1, step 1)

**To:** challenge@africadeeptech.org
**Subject:** ADTC 2026 — three scoring-mechanics questions (math_scientific_reasoning team)

---

Hello ADTF team,

We're building a submission for the math_scientific_reasoning track and
have three questions about evaluation mechanics that the Devpost page,
submission template, and profiler source don't fully resolve. Answers
will directly shape our architecture choices.

**1. How are `test_prompts` responses generated for judging?**
Are the four prompts (our two + your two hidden) answered by the bare
GGUF through llama.cpp, or by the submission's application code (for
example when `model.packaging` is `docker_build_from_repo`)? Our system
wraps the model in a deterministic verification pipeline, and this
determines whether judges see its certified outputs directly.

**2. Is S_perf's denominator the maximum TPS observed across all
submissions, or the published TPS_REFERENCE of 15.0?**
The leaderboard table shows `TPS_act ÷ TPS_max` while the notes give
TPS_REFERENCE = 15.0 (provisional). Small models can exceed 90 TPS on
reference-class hardware, so the two readings produce very different
scores.

**3. Where do we obtain the official math_scientific_reasoning
validation set?**
The challenge page says validation sets are provided per domain; we
haven't located the math set on the portal or Discord and want to test
against it rather than a proxy.

Thank you — and thanks for publishing the profiler source; being able
to read the actual measurement code is unusual for a competition and
very much appreciated.

Boluwatife Faturoti
(GitHub: judeszn)

---

**Send checklist:** also post Q1/Q3 in the Discord (parallel channel,
often faster); log any answer verbatim into ASSUMPTION_REGISTER.md the
day it arrives (A-02, A-05, A-03/A-08 respectively).
