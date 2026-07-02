# Speaker notes — "EulerMind Edge AI Optimizer"

Public framing only. Internal names (`edge_ai_deployment`, `FailureSignal`,
`DeterministicPolicy`) stay out of judge-facing language — see
`research/edge_ai_family_decision.md` for why this instance was chosen.

## The pitch, in order

1. **Frame the problem before showing the tool.** "You have five ML
   models and a laptop with limited RAM. Which do you deploy, and how
   many of each?" — this is a real edge-AI decision, not a textbook word
   problem. Note the irony on purpose: EulerMind is itself solving this
   exact category of problem about itself (an offline reasoning model
   deciding what fits in constrained memory).
2. **Feed it the messy prompt live**, distractor sentences and all
   (light fixtures, parking lot, RAM given in MB against a GB catalog).
   Say nothing about them — let the formalization step visibly ignore
   the irrelevant facts and convert the units, unprompted.
3. **Show the attempt → verify → retry loop happening, not just the
   final answer.** If the first attempt fails a budget or the
   high-accuracy constraint, show the exact FailureSignal (which
   constraint, by how much) and narrate: "the system caught its own
   mistake here — a smaller model wouldn't have known it was wrong."
4. **Land on the trust label.** Say the word "Verified" and mean it:
   every number in the final answer was checked by a real solver, not
   asserted by the model.
5. **Call out the near-miss on purpose:** XGBoost has the single highest
   accuracy of any model (0.96) but is *not* in the optimal deployment —
   it's individually the best model and budget-inefficient at these
   numbers. This is the line that shows judges the system is actually
   optimizing, not pattern-matching to "pick the best accuracy."
6. **Close on the constraint, not around it:** "This ran offline, on a
   laptop, inside a 4GB budget, on a 1-2B parameter model — no cloud, no
   GPU." State the measured RAM and latency numbers once Phase 1C
   produces them (see `demo/expected_output.md`).

## What NOT to do live

- Don't show a clean/textbook variant of this problem — the messy one is
  the point.
- Don't explain FailureSignal/Policy by name — narrate what happened
  ("it noticed X was over budget and adjusted"), not the internal
  contract.
- Don't skip a failed attempt if one happens naturally during rehearsal —
  a real recovery is more convincing than a first-try success. If the
  live run happens to succeed on attempt 1, have a rehearsed backup clip
  of a recovered run ready, since the retry-and-recover moment is the
  actual thesis of the project (verification-guided beats blind retry).

## Reserved for later (Phase 1D, not this demo)

CSP's unsat + minimal-conflict-set mechanism ("no valid assignment
exists, and here is exactly why") is a stronger single-sentence proof of
Law 1 than anything in the knapsack demo — it shows outright refusal to
fabricate, not just constraint-checking. Worth a second demo scene once
the pipeline generalizes past Edge AI Deployment; not required for the
first flagship recording.
