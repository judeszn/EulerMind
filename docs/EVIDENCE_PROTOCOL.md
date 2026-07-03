# EulerMind Evidence Protocol v1.0 (FROZEN)

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

## Standing rule for architecture discussion

Every architecture discussion must end with **either** a measurable
experiment whose outcome would change the decision, **or** a falsifiable
contract clause a future experiment will test. A debate that can produce
neither is philosophy, not engineering, and should stop.

Definitional/contract work is exempt from "name an experiment now" — its
job is to make later experiments valid (e.g. the Verified≠Correct contract
had no immediate experiment yet made the eventual one meaningful) — but it
must still be falsifiable, or it is philosophy wearing a contract's name.
