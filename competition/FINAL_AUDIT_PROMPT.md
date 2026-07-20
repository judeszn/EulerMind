# Final-submission audit prompt (run in a FRESH session before submitting)

Copy everything below into a new Claude Code session (or hand it to any
competent engineer). It assumes zero context on purpose.

---

```text
FINAL SUBMISSION AUDIT — EulerMind, Africa Deep Tech Challenge 2026

You are a hostile pre-submission auditor. Your job is to find the reasons
this submission would LOSE, before a judge does.

HARD RULES
- AUDIT ONLY. Do not edit, fix, commit, or push anything. If you find a
  CRITICAL issue, report it with a proposed fix and STOP for approval.
- Evidence only: every verdict must come from a command you actually ran
  in this session, never from reading documentation and believing it.
- Anything you cannot verify from this machine gets verdict BLOCKED (with
  the reason), never PASS.
- Work in a scratch directory. Clone fresh — audit the PUSHED state, not
  a local working copy that may be ahead of origin.

CONTEXT (verify, don't trust)
- Submission repo (what judges clone):
  github.com/judeszn/eulermind-adtc-submission
- Research/evidence repo: github.com/judeszn/EulerMind
- Product: two INDEPENDENT lanes. Certified lane = pure-stdlib exact
  solver + certificate + second independently-written checker; works with
  NO model. Tutor lane = optional local GGUF (Qwen2.5-Math-1.5B) via
  llama-server; a deterministic answer checker labels the result.
- Trust ladder (locked): Verified / Derived / Heuristic / Open internally;
  displayed as PROVED / CHECKED / AI EXPLANATION / COULDN'T ANSWER, plus a
  VERIFICATION FAILED state. False-verification count must be 0 everywhere.

SECTION A — COLD-CLONE RUNNABILITY (the judge's first 10 minutes)
1. git clone the submission repo into a temp dir.
2. Required files: README.md, REPORT.md, KNOWN_LIMITATIONS.md, LICENSE,
   metadata.json, download_model.sh, run_demo.sh, app/ (~17 files).
3. `python3 -m app.local_demo` (no model, no installs) must serve
   localhost:7860. POST the Lagos workshop test prompt to /solve →
   label "Verified", answer 30 chairs + 30 tables, profit 345000.
4. `PATH=/usr/bin:/bin ./run_demo.sh check` must FAIL CLEANLY with
   per-OS install guidance (macOS/Linux/Windows) — not a bash error, not
   a dead link, not a reference to a file that doesn't exist in THIS repo.
5. If llama-server + the GGUF are available on this machine: run the full
   stack, ask one checkable WAEC question (e.g. "Solve 2x^2 + 7x + 3 = 0")
   → CHECKED/Derived with a plain-English rationale; then POST /check with
   a deliberately wrong answer ("FINAL ANSWER: x = 5" for that question)
   → must FAIL LOUDLY, never Derived. If not available: BLOCKED, say so.
6. With no model server running, the tutor lane must show the graceful
   message ("AI explanations are optional...") — not a red error.

SECTION B — HONESTY / OVERCLAIM SCAN (tracked files only)
1. grep tracked files for banned claims: "never wrong", "always correct",
   "100% accurate", "all maths", "guarantees", "saturated". Any hit on a
   judge-facing file is CRITICAL.
2. Tutor-lane text must never claim "independent" verification — that word
   belongs to the certified lane only (two separately-written checkers).
3. Every number in README/REPORT must trace to a checked-in artifact or CI
   run: 192/192 certificates, 0% false certification, 12/20 on the real
   WAEC set, 0 false verifications, ~1.7 GB peak RAM, TPS figure. Open the
   cited files; confirm the numbers match. A cited file that doesn't exist
   is CRITICAL.
4. The 20-question WAEC set is BURNED (checkers were improved against it).
   Confirm no doc calls it an untouched holdout. If a fresh unseen set was
   since run, its transcript must exist and match any claim made about it.
5. KNOWN_LIMITATIONS.md must exist and not contradict the README.

SECTION C — TRUST INTEGRITY (the product's one non-negotiable)
1. Labels come only from deterministic code: grep app/ to confirm no
   prompt asks the model to declare its answer verified/correct, and no
   code path lets model text set a label.
2. Negative controls via app/answer_checker.py: wrong quadratic root,
   wrong simultaneous pair, wrong percentage → all must fail loudly
   (Heuristic + passed=False), zero false Derived.
3. In the research repo: `python3 -m benchmark.selftest` → all checks pass.
4. Truncated generations are never verified (finish_reason plumbing
   present in tutor.py and local_demo.py).

SECTION D — LEAK AND HYGIENE SCAN
1. `git grep` tracked files for: "/Users/", "sk-", "ghp_", "password",
   "token". Any hit is CRITICAL.
2. Confirm .claude/, __pycache__/, model weights (*.gguf) are untracked.
3. `git log --format=%B` — no AI/Co-Authored-By attribution trailers, no
   embarrassing messages.

SECTION E — DEMO-DAY TRAPS (report, don't fix)
1. Ollama fallback: app/tutor.py probes 127.0.0.1:8080 THEN :11434. If
   Ollama is running on the demo machine, a llama-server failure silently
   swaps models mid-demo. Check whether anything is listening on 11434
   right now; the pre-demo checklist must say "quit Ollama".
2. Ports 7860/8080 free; stale server processes from old checkouts killed
   (this project was bitten by exactly this once — check `lsof -i :7860`
   and confirm the serving process's cwd is the repo you think it is).
3. Offline claim: with the stack up, every listening socket for llama/
   python must bind 127.0.0.1 only.

SECTION F — PROFILER CONFORMANCE
1. metadata.json parses; _runtime.model_path matches download_model.sh's
   output path exactly.
2. The checked-in baseline submission JSON exists and its RAM/TPS numbers
   are the ones the README cites.
3. .github/workflows/profile.yml exists; if `gh` is available, confirm the
   latest run on main is green. Otherwise BLOCKED.

OUTPUT FORMAT
- One table per section: check | verdict (PASS / FAIL / CRITICAL /
  BLOCKED) | evidence (the command + one-line output).
- Then a final verdict: SUBMIT AS-IS, or FIX FIRST with a ranked list.
- End with the explicit list of things this audit could NOT verify from
  this machine (e.g. native Windows, a second physical machine) so a
  human can close those by hand. Never silently promote BLOCKED to PASS.
```
