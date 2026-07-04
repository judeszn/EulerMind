# EulerMind

A verification-guided mathematical reasoning engine optimized for commodity
hardware (CPU-only, fully offline, 1.7 GB peak RAM measured).

**Current state:** three certified reasoning domains (edge-AI deployment,
constraint CSP, linear programming), each with a deterministic
parser-first formalizer, an exact solver, a certifying verifier, and a
**second, independently-written checker** — 192/192 certificates agreed,
0% false certification, reproduced byte-identically across OS and CPU
architecture on every push. Current conclusions:
[docs/SCIENTIFIC_STATE.md](docs/SCIENTIFIC_STATE.md) · measurements:
[scoreboard.md](scoreboard.md) · research record:
[whitepaper/GAMMA_FINAL_REPORT.md](whitepaper/GAMMA_FINAL_REPORT.md).

**ADTC 2026:** this is the research/evidence repo. The competition
submission lives in its own template-conformant repository; competition
boards live in [competition/](competition/).

**Try it (zero dependencies, stdlib only):**

```bash
python3 -m app.local_demo   # → http://localhost:7860, fully offline
```

Paste a production-planning, assignment, or deployment problem and watch
each pipeline stage certify — or refuse honestly when the problem is
outside the certified domains.

The frozen vision, laws, guardrails, and phase plan live in
[docs/VISION.md](docs/VISION.md). Pre-registered research hypotheses with kill
thresholds live in [whitepaper/HYPOTHESES.md](whitepaper/HYPOTHESES.md).

## Phase 0 (historical — the research instrument)

We build the ruler before the system it measures. Phase 0 ships exactly four
things — benchmark harness, procedural dataset generator, metrics, logging —
and is deliberately **stdlib-only** so the instrument never depends on the
solvers (SymPy, Z3, llama.cpp) it will later measure.

### Quickstart

```bash
# 1. Calibrate the ruler (oracle must score 100%, null must score 0%)
python3 -m benchmark.selftest

# 2. Generate the dataset (40 base instances/category -> 240 problems,
#    clean+messy pairs, ~25% held out by deterministic base_id hash)
python3 -m benchmark.generator.build --per-category 40

# 3. Run a reference solver and produce a report
python3 -m benchmark.runner --solver oracle --split dev
python3 -m benchmark.runner --solver null --split dev
```

### Layout

```
benchmark/
  schema.py          problem schema, deterministic dev/holdout split
  generator/         procedural generators (exact ground truth by construction)
    lp.py            2-variable LP word problems (vertex enumeration, Fractions)
    calculus.py      polynomial critical points (built backwards from the answer)
    csp.py           assignment puzzles incl. UNSAT instances + minimal conflict sets
    build.py         dataset builder CLI
  metrics.py         re-verifying graders, McNemar paired comparison
  runner.py          runner, RAM/latency profiling, JSONL traces, reports
  selftest.py        harness calibration (adversarial grader checks)
  datasets/          generated (git-ignore large versions)
  reports/           generated
kernel/
  state.py           frozen Execution State schema (versioned) + failure taxonomy
  api.py             frozen Kernel API v1 (stage protocols + Budget config)
  loop.py            the reasoning loop: verify-in-the-loop, budgeted, fully logged
  oracle.py          Oracle Mode — mechanical EulerMind, no LLM; Phase 1 gate
research/            experiment quarantine, one dir per hypothesis
docs/VISION.md       frozen vision + research question
docs/LOGGING.md      frozen JSONL trace schemas (the execution-trace corpus)
whitepaper/          pre-registered hypotheses (H1-H4)
```

### Design decisions worth knowing

- **Graders re-verify, never string-match.** Any feasible-and-optimal LP plan,
  any valid CSP assignment passes — not just the stored example.
- **Unsat instances are the epistemic test.** ~15% of CSP instances have no
  solution; the correct answer is a refusal. Inventing an assignment is graded
  wrong (Law 1, enforced mechanically).
- **Messy variants share ground truth with clean twins**, so the clean-minus-
  messy paired delta is the formalization-robustness metric.
- **Kill decisions use `metrics.compare_paired`** (McNemar exact), never raw
  rate comparison — at n≈100, differences under ~7 points are noise.
- **Split hygiene:** dev for iteration, holdout run once per phase gate,
  judges' problems assumed unseen.
