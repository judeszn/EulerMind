# SYSTEM DIRECTIVE

You are not helping build a research project. You are helping maximize the
probability of winning the Africa Deep Tech Challenge 2026.

Before suggesting any feature, ask:

1. Which official judging criterion does this improve?
   (S_total = 0.50·S_acc + 0.30·S_perf + 0.20·S_eff − P_thermal; see docs/SCORING.md)
2. Is there a simpler implementation?
3. Can it be measured within 48 hours?
4. Does it increase expected final score?

If any answer is "no" or "unknown", recommend deletion or defer it to
`future/`. Consult `DO_NOT_BUILD.md` before proposing anything new.

Do not optimize for elegance, extensibility, or publishability before
submission. The benchmark and the official judging rubric are the source of
truth. Working software with higher expected judge score is always preferred
over more sophisticated architecture.

Arguments must be backed by benchmark results, RAM profiles, latency
measurements, or demo quality. Architecture is frozen (docs/VISION.md v1.1).

# Git rules

- NEVER add "Co-Authored-By" or any Claude/AI attribution trailers to
  commit messages. Clean commit messages only.

# The Ladder

All work climbs L0 (Raw Model) → L1 (Reasoning Prompt) → L2 (Tool-Assisted)
→ L3 (Verification-Guided). Before building anything ask: which rung does
this improve? `scoreboard.md` tracks measured scores per rung — update it
with every new measurement. Thin slices across all rungs before optimizing
any single rung.

# Repo orientation

- `WIN.md` — read first. Mission, constraints, 48-hour rule.
- `docs/SCORING.md` — the official rubric + feature decision matrix.
- `docs/VISION.md` — frozen architecture (Laws, kernel, guardrails, phases).
- `docs/LOGGING.md` — frozen JSONL trace schemas. Never break replay logs.
- `benchmark/` — the instrument (stdlib-only; never import solvers into it).
- `kernel/` — frozen API v1 (api.py), loop (loop.py), Oracle Mode (oracle.py).
- `research/` — experiment quarantine, one dir per hypothesis (whitepaper/HYPOTHESES.md).
- `future/`, `DO_NOT_BUILD.md` — deferred until after submission.

# Commands

- `python3 -m benchmark.selftest` — calibrate the ruler (must pass 20/20).
- `python3 -m benchmark.generator.build --per-category N` — new dataset version
  (datasets are immutable: new directory + CHANGELOG entry, never regenerate in place).
- `python3 -m benchmark.runner --solver <name> --split dev` — run + report.
- Kill decisions use `benchmark.metrics.compare_paired` (McNemar), never raw rates.
- Holdout split is run once per phase gate. Never iterate on it.
