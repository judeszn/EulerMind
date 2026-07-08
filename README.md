# EulerMind

An offline mathematics tutor that checks its own answers before asking a
student to trust them.

CPU-only, fully offline, 1.7 GB peak RAM measured. Built for the
[Africa Deep Tech Challenge 2026](https://africadeeptech.org/challenge-2026/).

```bash
./run_demo.sh               # llama.cpp + GGUF + UI, one command
python3 -m app.local_demo   # UI only — the certified lane works without a model
```

This is the research and evidence repository. The competition submission
(template-conformant, model weights, `REPORT.md`) lives in
[github.com/judeszn/eulermind-adtc-submission](https://github.com/judeszn/eulermind-adtc-submission),
generated from this repo; internal submission tracking lives in
[competition/](competition/).

## 1. Problem

Offline, low-bandwidth classrooms cannot rely on cloud-hosted AI tutors —
no connection, no server, no service. A model small enough to run on
commodity hardware without internet access is the only option, and small
offline models make more arithmetic and algebra mistakes than the
cloud-scale models people are used to.

## 2. Why existing AI tutors are insufficient

A chatbot that explains a wrong answer as confidently as a right one is not
useful for learning — a student cannot tell which explanation to trust
without already knowing the answer. Most offline tutors either state that
limitation nowhere, or bury it in a generic disclaimer that never changes
per answer. Neither tells a student, question by question, which specific
output was checked and which was not.

## 3. EulerMind approach

Three rules, enforced in code, not in the prompt:

1. **Never fabricate certainty.** Every answer carries one of four trust
   labels (§6), assigned by deterministic code — never by the model
   labeling itself.
2. **Reasoning before generation.** Arithmetic, algebra, and constraint
   checking are executed, never generated. The model proposes; code
   verifies.
3. **Everything measurable.** Every claim in this README traces to a
   dated measurement in [scoreboard.md](scoreboard.md) or a
   `research/*/RESULTS.md` report — see
   [docs/SCIENTIFIC_STATE.md](docs/SCIENTIFIC_STATE.md) for the current,
   evidence-backed state, including the tested hypothesis that did not
   hold up (§9).

Full design rationale and the frozen phase plan: [docs/VISION.md](docs/VISION.md).

## 4. Architecture

```
                 question (text)
                        |
                        v
              +-- Reasoning Kernel --+
              |                      |
              |   Formalize          |     natural language -> variables,
              |       |              |     constraints, objective
              |       v              |
              |   Attempt / Execute  |     arithmetic and search run as
              |       |              |     code, never generated
              |       v              |
              |   Verify             |     independently-written checker,
              |       |              |     no shared code with the solver
              +-------|--------------+
                      v
                Trust label
             (Verified / Derived / Heuristic / Open)
                      |
                      v
              Explanation (rendered from the logged trace)
```

Three domains carry a full Formalizer -> Solver -> Verifier ->
Independent Checker chain today: bounded resource allocation
(`edge_ai_deployment`), constraint satisfaction (`constraint_csp`), and
linear programming (`optimization_lp`). A fourth path (`app/tutor.py` +
`app/answer_checker.py`) routes free-form secondary-school questions to a
deterministic answer checker (substitution, recomputation, or formula
roundtrip, depending on question type) when they fall outside the three
certified domains.

## 5. Trust model

Every answer carries exactly one label. Labels are assigned by
`app/answer_checker.py` or the kernel's certificate logic — never
self-reported by the model.

| Label | Meaning | How it is earned |
|---|---|---|
| **Verified** | The kernel certified the answer against an executable model of the problem, and a second, independently-written checker agrees. | Formalizer + solver + two independent verifiers, all agreeing |
| **Derived** | The model's answer survived a deterministic check (substitution, recomputation, or a formula roundtrip against fixed sample values). | `app/answer_checker.py` |
| **Heuristic** | The answer could not be checked by any available method (open-ended proof, unsupported question shape). Shown as unverified, not as wrong. | No checker matched the question |
| **Open** | The system could not produce or check an answer at all. | Refusal |

A `Verified` label requires both the arithmetic *and* the formalization
of the problem to pass a machine check — a correct calculation on a
misread problem is still wrong, so formalization is gated too
(`docs/VISION.md`, Law 1).

## 6. Offline execution

Inference runs through `llama.cpp` against a local GGUF file
(`llama-server` on `127.0.0.1`); the certified kernel and the answer
checker are pure Python standard library. Nothing in the solve path makes
a network call. This has been checked two ways:

- **Cross-machine, cross-architecture reproduction**: the certification
  pipeline (all three domains) reproduces byte-for-byte on GitHub Actions
  `ubuntu-latest` (macOS/arm64 -> Linux/x86_64), on every push
  (`.github/workflows/reproduce.yml`,
  [research/D3_independent_reproduction/RESULTS.md](research/D3_independent_reproduction/RESULTS.md)).
- **Peak RAM measured at 1.7 GB** with the production model
  (Qwen2.5-Math-1.5B, Q4_K_M) loaded — see
  [competition/MODEL_DECISION.md](competition/MODEL_DECISION.md).

## 7. Screenshots

Not yet committed to this repo. Demo staging (terminal run, a `Verified`
result, and an honest `Open` refusal) is described in
[competition/FINAL_SUBMISSION_AUDIT.md](competition/FINAL_SUBMISSION_AUDIT.md);
images will be added here once captured.

## 8. Benchmarks

All numbers below are measured and dated; the full ledger, including
negative results, is [scoreboard.md](scoreboard.md).

| Metric | Result | Source |
|---|---|---|
| Certificates checked (edge_ai 60 + CSP 52 + LP 80) | **192/192** primary/independent agreement, **0%** false certification | [docs/SCIENTIFIC_STATE.md](docs/SCIENTIFIC_STATE.md) |
| Independent reproduction | Bit-identical across OS + CPU architecture, every push | [research/D3_independent_reproduction/RESULTS.md](research/D3_independent_reproduction/RESULTS.md) |
| Tutor lane, real WAEC past-paper set (n=20, not authored by the checker's authors) | 12/20 `Derived`, 0 false verifications | [competition/holdout_waec_realworld_dev_transcript.md](competition/holdout_waec_realworld_dev_transcript.md) |
| Release-candidate profiler run (Qwen2.5-Math-1.5B, Q4_K_M) | 15.68 TPS, 1,699 MB peak RAM, audit-like x86 CI, fraud-check pass | [competition/FINAL_SUBMISSION_AUDIT.md](competition/FINAL_SUBMISSION_AUDIT.md) |

**What is not yet established:** the pre-registered hypothesis that
verifier feedback improves on blind retry (H1) was tested and rejected at
the configuration measured — reported in full, not hidden, in
[docs/SCIENTIFIC_STATE.md](docs/SCIENTIFIC_STATE.md). The trust-labeling
and dual-checker certification described above do not depend on that
hypothesis being true.

## 9. Run locally

Requires Python 3.10+. The benchmark harness has zero dependencies; the
tutor lane requires `llama.cpp` and a local GGUF file.

```bash
# Certified-domain harness (no model needed)
python3 -m benchmark.selftest                                    # calibrate the ruler: 20/20
python3 -m benchmark.generator.build --per-category 40           # generate a dataset version
python3 -m benchmark.runner --solver oracle --split dev          # run + report

# Full tutor stack (model + UI)
./run_demo.sh                 # starts llama-server + UI, downloads nothing automatically
./run_demo.sh check           # preflight only, no servers started
python3 -m app.local_demo     # UI only, certified lane works without a model
```

Model setup and hardware notes: [competition/PRODUCTION_SETUP.md](competition/PRODUCTION_SETUP.md).

## 10. Repository layout

```
app/         tutor UI, local demo entry point, deterministic answer checker
kernel/      frozen Kernel API: state schema, reasoning loop, formalizers,
             solvers, Oracle Mode (mechanical validation, no LLM)
benchmark/   the measurement instrument — schema, generators, metrics,
             runner, selftest. Stdlib-only; never imports a solver.
research/    one directory per experiment (hypothesis, run, RESULTS.md);
             permanent record, never edited after the fact
docs/        frozen architecture (VISION.md), rubric mapping (SCORING.md),
             trace schema (LOGGING.md), live findings (SCIENTIFIC_STATE.md)
whitepaper/  pre-registered hypotheses and their outcomes
demo/        the pinned, rehearsed demo script and its recorded baseline
competition/ submission tracking, model selection record, judge-facing docs
scoreboard.md   the measurement ledger — every experiment, one row each
```

## 11. License

[MIT](LICENSE).
