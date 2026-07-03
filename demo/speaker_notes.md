# Speaker notes — EulerMind

Public framing only. Internal names (`edge_ai_deployment`,
`optimization_lp`, `FailureSignal`, `DeterministicPolicy`) stay out of
judge-facing language — see `research/edge_ai_family_decision.md` for why
scene 1's instance was chosen.

**Correction (2026-07-03):** this file previously described the
attempt→fail→retry LLM narrative and called "verification-guided beats
blind retry" the project's actual thesis. Both are stale. The
LLM-attempter pipeline was superseded by the deterministic solver
pipeline in Validation Phase 1 (`demo/actual_output.md`'s history), and
the retry-beats-blind-retry hypothesis (H1) was **rejected by the
registered decision rule** in Phase Gamma (`whitepaper/HYPOTHESES.md`,
`docs/SCIENTIFIC_STATE.md`) — measured directly, not assumed. Do not use
the old framing live: a judge who has read the repo can ask "how does
your data support that?" and the honest answer is now "it doesn't; that's
not what we're claiming." The corrected pitch below states what the
evidence actually supports, which is a stronger and more defensible claim
than the one it replaces.

## The actual thesis (say this, not the old one)

"EulerMind takes a natural-language math problem, converts it into a
formal specification, solves it with a real deterministic solver, and
then certifies the answer with a **second, independently-written checker**
that shares no logic with the first — across multiple mathematically
different kinds of problems. The claim isn't 'the model reasons better.'
The claim is 'you don't have to trust the model at all — you can check
its work two different ways and both have to agree.'"

## Scene 1 — Edge AI Optimizer (`edge_ai_deployment`)

1. **Frame the problem before showing the tool.** "You have five ML
   models and a laptop with limited RAM. Which do you deploy, and how
   many of each?" — a real edge-AI decision, not a textbook word problem.
2. **Feed it the messy prompt live**, distractor sentences and all
   (light fixtures, parking lot, RAM given in MB against a GB catalog).
   Say nothing about them — let the formalization step visibly ignore
   the irrelevant facts and convert the units, unprompted.
3. **Land on the trust label.** Say "Verified" and mean it: the answer
   came from a real exhaustive-search solver, then was independently
   rechecked by a second implementation that shares no search code with
   the first (`research/G3_cert_independence/RESULTS.md` — 60/60
   agreement, 0 false certifications).
4. **Call out the near-miss on purpose:** XGBoost has the single highest
   accuracy of any model (0.96) but is *not* in the optimal deployment —
   individually the best model, budget-inefficient at these numbers. The
   system optimized; it didn't pattern-match to "pick the best accuracy."
5. **Close on the constraint:** "This ran offline, on a laptop, inside a
   4GB budget, on a 1-2B parameter model — no cloud, no GPU."

## Scene 2 — Optimization Advisor (`optimization_lp`)

Full script: `demo/lp_scene.md`. The point of this scene is **not**
"another benchmark passed" — it's that the independent checker uses a
**different theorem** (LP Duality) than the solver (Fundamental Theorem
of LP), not just different code. Land on: "two unrelated pieces of math,
80 years apart, agreeing independently."

## Scene 3 — the credibility close (if time allows, or for Q&A)

"This isn't just tested on this machine. Every commit re-runs the entire
certification pipeline on a completely separate machine — different OS,
different CPU architecture — and checks that every certificate, every
independent-checker verdict, and every false-certification count comes
back byte-for-byte identical. It did, again, this morning."
(`research/D3_independent_reproduction/RESULTS.md` — link the GitHub
Actions run if asked for proof: judeszn/EulerMind, run 28673053751.)

If asked "what happens when it's wrong": show the CSP scene's unsat
mechanism (`research/G1_csp_validation/`) — given a genuinely unsolvable
assignment problem, EulerMind returns "no valid assignment exists" plus
the exact minimal set of constraints causing it, never a fabricated
answer. Refusal-to-fabricate is Law 1's strongest single-sentence proof.

## What NOT to do live

- Don't show a clean/textbook variant of scene 1's problem — the messy
  one is the point.
- Don't claim retry-and-recover is the thesis — see the correction above.
  If a first attempt visibly fails in Scene 2's LP unbounded/infeasible
  edge case (not part of the pinned instance, but available if explored
  live), narrate it as "the system correctly refuses to certify an answer
  here" — a refusal, not a recovery.
- Don't explain `FailureSignal`/`Policy`/`DeterministicPolicy` by
  internal name in front of judges — these are retry-mechanism internals
  from a hypothesis that was tested and rejected; they're not part of the
  current pitch at all.
