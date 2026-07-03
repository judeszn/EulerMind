# EulerMind Evidence Protocol v1.0 (FROZEN)

**Frozen governance — timeless.** Any "Precedent:" reference to a specific
result below is a frozen historical anchor illustrating a rule, not a live
status; it does not change when that result's verdict changes. Current
scientific state lives only in `docs/SCIENTIFIC_STATE.md`.

Frozen once. Do not revisit unless experience proves it insufficient (and
if it does, that itself is a logged, evidenced change — not a rewrite).

## Every experimental claim must include

1. **Positive control** — a known-valid case is accepted.
2. **Negative control** — corrupted / wrong cases are rejected.
3. **Independent re-check** — a separate implementation agrees.
4. **Frozen benchmark** — dataset immutable and versioned.
5. **Frozen success metric** — registered before the run.
6. **Reproducible execution record** — artifacts written to disk.

## Every claim must state its evidence level explicitly

Overclaiming is prevented by naming the level, not by the result looking
strong. The two middle levels are distinct and must not be conflated:

| Level | Meaning | Bar |
|---|---|---|
| Architecture only | Design is internally coherent | a coherent diagram is not evidence |
| Implementation | Code exists and ran | in one environment |
| **Internal reproducibility** | Same code + **same** environment reproduces | re-run locally |
| **Independent reproducibility** | Same code + **different** environment reproduces | someone clones and runs it elsewhere |
| **Replicability** | An **independent implementation** reaches the same conclusion | someone writes their own checker and agrees |
| External validation | Community reproduces and extends | publication stage |

Reproducibility (re-run *my* code) and replicability (someone writes
*their own* and agrees) are different scientific standards. For EulerMind
the thesis is "trust from independent certification," so **replication is
closer to the actual claim than reproduction** — a second, independently
written optimality checker agreeing is stronger evidence than re-running
the same enumeration. The current `recheck_certificate` sharing the
solver's search is a *replicability* gap, not a reproducibility one.

## Current status of the one validated vertical

Bounded optimization (edge_ai_deployment), Validation Phase 1:
- Architecture: locked.
- Implementation: executed.
- Internal reproducibility: **reported (this environment only — the ceiling).**
- Independent reproducibility: not established.
- Replicability: not established.
- External validation: not supported.

## Standing rule for negative-result wording (added 2026-07-03)

A negative result on a mechanism question must be recorded as
**answered-negative-at-the-registered-configuration**, never as
"COMPLETE" or a global negative. State it against the exact registered
intervention and inference configuration, not the axes that happen to
vary it (model choice, encoding, temperature, etc. are levers on the
mechanism, not the mechanism itself — naming levers invites a false sense
of completeness the moment someone finds a lever not on the list; naming
the registered configuration bounds the claim by construction instead).
Precedent: H1a in `whitepaper/HYPOTHESES.md` — "under the registered
intervention (prompt-appended textual verifier feedback) and registered
inference configuration (llama3.2:1b, temperature 0), no observable
behavioural variation was detected across retries." Also keep every such
claim strictly behavioural (what was observed), never cognitive (what the
model "did internally") — the latter is unobservable by construction.

When a mechanism check invalidates an outcome experiment (e.g. feedback
never functionally exercised, so a policy-comparison result can't answer
the policy question), **decompose the hypothesis rather than reporting
"untested."** The mechanism sub-question may have a real, earned answer;
collapsing it into "untested" discards evidence. Precedent: H1 → H1a
(mechanism, answered-negative-at-configuration) + H1b (causal claim,
still untested because H1a's negative removed the premise).

## Standing rule for stochastic vs. deterministic reproducibility (added 2026-07-03)

**Deterministic result** (output does not vary across identical reruns —
a solver, a certificate recheck, an attempter at temperature 0):
internal reproducibility means *bit-identical rerun*. **Stochastic
result** (output varies across identical reruns): internal
reproducibility can only mean *the qualitative conclusion is stable
across independent reruns* — expecting the exact Δ or p-value to repeat
is the wrong bar.

The deciding criterion is **observed behaviour across identical reruns**,
never a proxy inferred from configuration. (See Pending Clarification
below — do not promote a clarification into this frozen rule until a
second independent implementation reproduces the issue.)

### Pending Clarifications (recorded, NOT yet promoted into the frozen protocol)

Recorded here so a single implementation's finding does not silently
rewrite frozen governance — the project's standing allergy to evidence
escalation applies to its own protocol as much as to its hypotheses. A
clarification is promoted into the rule above only when a **second,
independent implementation** demonstrates the same issue.

- **PC-2026-07-03 (one implementation so far):** the informal heuristic
  "temperature > 0 implies stochastic execution" is not a reliable
  classifier. For llama3.2:1b on Ollama 0.30.10, a fixed seed rendered a
  temperature-0.6 experiment fully deterministic (bit-identical across
  reruns, two independent tests — `research/G2_csp_h1b/REPRODUCTION.md`).
  Narrow claim only: *this implementation, this seed control*. Not
  asserted universally — other engines/models may differ (e.g. batching
  nondeterminism can break fixed-seed reproducibility elsewhere).
  Practical guidance in the meantime: **classify by observed rerun
  behaviour, not by temperature**; where a fixed seed pins output the
  result is deterministic and robustness to sampling variation becomes a
  separate, seed-varied experiment. Promote to the frozen rule only on a
  second independent confirmation.

**A stochastic result may not be recorded as confirmed on a single
execution, no matter how clean the run looked.** Before treating a
stochastic result as internally reproduced: **pre-register a fixed N of
independent reruns, chosen before any of them are observed, and report
all N regardless of outcome.** The result is "stable" only if all N
reruns agree on which side of the pre-registered kill threshold the
outcome falls. Do **not** use an open-ended "repeat until it looks
stable" criterion — without a stopping rule fixed in advance, that is
statistically indistinguishable from optional stopping (sampling until a
preferred result appears), regardless of intent.

**N itself must be pre-registered *per experiment*, not inherited as a
blanket constant, and its value must come from a documented, principled
method — not bare discretion.** A fixed protocol-wide default (e.g.
always N=3) reintroduces the same hazard one level up: choosing N based
on which value flatters the expected outcome is pre-registration in name
only. Two legitimate ways to size N, and every experiment must state
which regime it's in:
- **Confirmatory batch** — the observed (or expected) result is far from
  the decision boundary; N is small, just enough to rule out "this one
  run was a fluke" (this is what N=3 means for H1b-Gamma-1, whose
  observed p=0.79 is nowhere near the 0.05 boundary — a diagnostic
  check, not a power-seeking campaign).
- **Power-driven batch** — the result is genuinely borderline (e.g. a
  p-value or Δ close to the pre-registered threshold); N should be set
  via an actual power calculation relative to that threshold and the
  known per-run sample size, since a small confirmatory N would be too
  underpowered to trust either way.

This project's own repeated-measures caveat applies regardless of which
regime: N reruns of the same problem set are not N independent samples
of fresh problems, so naive pooling into one larger test overstates
power — report each rerun's own result and require unanimous agreement,
don't pool blindly.

**Precedent (2026-07-03 confirmation review):** H1b-Gamma-1
(`research/G2_csp_h1b/`) was found, on review, to rest on exactly one
execution of a temperature=0.6 experiment — reclassified from
implied-confirmed to explicitly PROVISIONAL pending N=3 (confirmatory
batch, justified above, not a protocol-wide default) pre-registered
reruns. Caught by checking committed execution artifacts (timestamped
report files) against the narrative claim, not by re-reading the
narrative alone.

## Standing rule for certificate correctness vs. certificate independence (added 2026-07-03)

These are different properties and must be reported separately, not
merged into one "verifier soundness" line:

- **Certificate correctness** — when the certificate says "accepted,"
  is the certified property actually true? Supported by negative
  controls (rejects corrupted certificates) *and*, more importantly, by
  cross-validation against a genuinely separate source of truth (e.g. the
  benchmark's independently-implemented ground truth), not by the
  recheck alone.
- **Certificate independence** — is the recheck procedure implemented
  separately from the thing producing the candidate, with no shared code
  path? **Currently partial for both validated verticals**:
  `edge_ai_solver.py`'s `recheck_certificate` reuses the solver's own
  optimum-search; `csp_solver.py`'s `recheck_certificate` calls the same
  `_check()` / `_enumerate_solutions()` functions `solve()` depends on. A
  systematic bug in that shared logic would fool the certifier and the
  candidate-producer identically, and no negative control run so far
  would catch it — negative controls test "rejects a wrong answer," not
  "the shared logic itself is correct." Closing this requires a second,
  genuinely independently-written checker, not merely a second function.

## Standing rule for architecture discussion

Every architecture discussion must end with **either** a measurable
experiment whose outcome would change the decision, **or** a falsifiable
contract clause a future experiment will test. A debate that can produce
neither is philosophy, not engineering, and should stop.

Definitional/contract work is exempt from "name an experiment now" — its
job is to make later experiments valid (e.g. the Verified≠Correct contract
had no immediate experiment yet made the eventual one meaningful) — but it
must still be falsifiable, or it is philosophy wearing a contract's name.
