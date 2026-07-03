# Delta D3 — Independent Pipeline Reproducibility: RESULTS

**Date:** 2026-07-03 · GitHub Actions run
[`28673053751`](https://github.com/judeszn/EulerMind/actions/runs/28673053751)
on a `ubuntu-latest`-hosted runner · **Outcome: SUCCESS — decision KEEP.**

## 1. Environment (genuinely independent, not simulated)

| | Development machine | CI runner |
|---|---|---|
| OS | macOS 15.7.1 | Linux (Ubuntu, `6.17.0-1018-azure`) |
| Architecture | arm64 | x86_64 |
| Python | 3.11.13 | 3.11.15 |
| Filesystem | working tree (reused) | fresh checkout, no cache |

Crosses OS, CPU architecture, and Python patch version — not a same-machine
fresh-checkout simulation. Third-party dependencies: **none** (verified by
import audit across `kernel/`, `benchmark/`, and every `research/`
experiment module — stdlib only), so "fresh Python environment" required
zero installs, eliminating a whole class of environment-drift risk by
construction. Full manifest and log:
`research/D3_independent_reproduction/reproduction_log_20260703-163812.txt`.

## 2. Execution

`benchmark.selftest`, then the three certification pipelines
(`research.G3_cert_independence.run`, `research.G3_cert_independence.run_csp`,
`research.D2_lp_vertical.run`) — each regenerated from scratch on the
runner and compared field-for-field (summary *and every row*, not only
aggregate counts) against the frozen reference reports already committed
to the repository.

## 3. Verification

| Check | Result |
|---|---|
| `benchmark.selftest` | **PASS** (all sub-checks, including `lp:`/`csp:`/`calculus:` negative-control checks) |
| edge_ai (Gamma+1) report | **bit-identical** — `sha256 cb2e21c5...` on both machines |
| constraint_csp (Gamma+2) report | **bit-identical** — `sha256 682934f8...` on both machines |
| optimization_lp (D2) report | **bit-identical** — `sha256 302bc5ee...` on both machines |
| Certificate decisions (primary/independent, every row) | identical |
| Agreement matrices | identical (60/60, 52/52, 80/80, unchanged) |
| False-certification counts | identical (0, 0, 0) |
| Environment-specific failures | none |

No diff on any of the three experiments (`"diff": null` in all three).

## 4. Evidence classification

| Level | Status |
|---|---|
| Architecture | unchanged |
| Implementation | reproduced |
| Internal Reproducibility | retained |
| **Independent Reproducibility** | **Supported** — different OS, different CPU architecture, different Python patch version, fresh checkout, zero manual intervention |
| Replicability | unchanged (still Partial-at-certificate-level / ✗-at-pipeline-level — a second machine running the *same* code is not a second, independently-written implementation) |
| External Validation | unchanged |

## 5. Scientific conclusion

**Registered Hypothesis HΔ3: Supported.** The complete deterministic
certification pipeline — formalizer, solver, verifier, and independent
checker, across all three verticals — reproduces identically on an
independent execution environment. This raises the evidence ceiling for
every certified result simultaneously (edge_ai, constraint_csp,
optimization_lp) without introducing any new capability, hypothesis, or
architecture change.

### Honest scope

- One independent run, one alternate environment (Linux/x86_64 via
  GitHub Actions). This is Independent Reproducibility, not Replicability
  — the same code ran twice, not two different implementations. The
  workflow (`.github/workflows/reproduce.yml`) now runs on every push to
  `main`, so this becomes a standing, continuously-reconfirmed check, not
  a one-off result — but the *evidence classification* is still "one
  environment class demonstrated," not "N independent environments."
- Certification path only (stdlib, no network, no model calls) — this
  says nothing about reproducibility of the LLM-dependent experiments
  (Gamma's H1a/H1b/H1b-Gamma-2), which require Ollama and are out of
  scope for this task by design.

## Stopping Reason

Stopped immediately after CI execution completed and evidence was
classified, per the registered Stop Condition. Δ4 not begun. H4 not
registered. No governance modified. No additional experiments started.
