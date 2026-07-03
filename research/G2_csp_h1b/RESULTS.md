# Phase Gamma — Temperature-Matched H1b: RESULTS

**Date:** 2026-07-03 · `llama3.2:1b` · 52-problem `constraint_csp` dev set
(42 SAT, 10 UNSAT) · fully offline. Executed under
`docs/EXECUTION_CONTRACT.md` v2.0, first task to exercise it.

## 1. Assumptions

- Seed is inert at temperature=0 for this model/server (greedy decoding
  ignores it) — **verified empirically before the code change**, not
  assumed: three seeds (0, 1, 42) at temp=0 produced byte-identical
  output on a test prompt.
- Given (1), adding unconditional `seed=state.attempt` to
  `GuidedCSPAttempter` does not alter its temperature=0 default behavior,
  so the class's original constructor call (`GuidedCSPAttempter()`)
  still reproduces the exact registered H1a configuration.
- Formalizer, Solver, Executor, Verifier, and Certificate code from
  `research/G1_csp_validation/` require zero changes — only the
  Attempter's sampling parameters are the object of this experiment.

## 2. Design Decisions

The prior CSP run (`research/G1_csp_validation/`) confounded two
variables: temperature (0 for guided, 0.6 for blind) and feedback
presence. This design holds temperature and seed-strategy **identical**
across both arms (0.6, `seed=state.attempt`) so feedback-presence is the
only deliberately varied factor. A **mechanism check** (pre-registered
threshold: ≥50% of multi-attempt problems show non-identical output
across attempts) gates whether the resulting Δ/p is trusted as evidence
about H1b at all — this is the exact check that found the prior run's
confound (100% identical), now run *before* interpreting results rather
than after.

## 3. Experimental Protocol

Step 1 (gate): `GuidedCSPAttempter()` at its unmodified default
(temperature=0) run against all 52 problems; must reproduce 42/42
identical signals or the run stops. Step 2: `BlindCSPAttempter()` (temp
0.6, no feedback) vs `GuidedCSPAttempter(temperature=0.6)` (temp 0.6,
with feedback) on the same 52 problems, 3-attempt budget, `policy=None`
vs `policy=DeterministicPolicy()`. Step 3: mechanism variation rate
computed for both arms before Δ/McNemar is reported as interpretable.

## 4. Positive Control

Inherited unchanged from `research/G1_csp_validation/RESULTS.md` §3 —
Formalizer, Solver, Verifier, and Certificate code were not modified in
this task. True satisfying assignment: ACCEPT. True minimal conflict:
ACCEPT. (Not rebuilt; re-verification would test unchanged code.)

## 5. Negative Control

Inherited unchanged, same source: duplicate project, wrong engineer set,
unknown project, forced constraint violation, satisfiable-set-as-conflict,
non-minimal-conflict — all REJECT.

## 6. Independent Re-check

`recheck_certificate()` (unchanged) ran on every Verified answer in both
arms this run: **10/10 (B2) and 12/12 (B3) accepted.**

## 7. Results

**Step 1 — sanity gate:**

| | Multi-attempt | Identical | Varied | Result |
|---|---|---|---|---|
| `GuidedCSPAttempter()` (temp=0, default) | 42 | **42** | **0** | **PASSED** — exact reproduction of the frozen H1a finding |

**Step 3 — mechanism gate:**

| Arm | Multi-attempt | Varied | Variation rate | vs. 0.50 threshold |
|---|---|---|---|---|
| B2 (blind, temp 0.6) | 48 | 38 | **0.79** | PASS |
| B3 (guided, temp 0.6) | 48 | 48 | **1.00** | PASS |

**Both arms pass. This is the first CSP run where the guided attempter's
retries are confirmed to be functionally live, not inert.**

**H1b comparison:**

| Metric | B2 (blind) | B3 (guided) | Δ (B3−B2) |
|---|---|---|---|
| Verified-Correct Rate | 19.23% | **23.08%** | **+3.85pts** |
| False Certification Rate | 0.0% | 0.0% | 0.0 |
| Mean Attempts | 2.73 | 2.69 | −0.04 |
| Every Verified cert rechecked | true (10/10) | true (12/12) | — |
| **McNemar p** | — | — | **0.7905** |

## 8. Limitations

- One model (llama3.2:1b), one domain (constraint_csp), one feedback
  encoding (prompt-appended failure signal text), one policy
  (`DeterministicPolicy`'s naive rule table), one temperature (0.6). Any
  axis changed reopens the question at a new configuration.
- n=52 is modest; the ±7pt noise floor registered elsewhere in this
  project applies here too — a small positive point estimate at this n
  is not strong evidence of *any* true effect size, small or zero.
- Guided's higher variation rate (1.00 vs B2's 0.79) is itself worth a
  note: feedback content changing every retry trivially guarantees output
  variation (the prompt itself differs each time), so B3's 100% is not
  surprising or, on its own, evidence of anything beyond "the mechanism
  is live" — which is exactly and only what the gate was checking for.

## 9. Scientific Conclusion

**This is the first methodologically valid test of H1b's causal claim.**
Both invalidating conditions from prior attempts are absent: verifier
soundness holds (0% false-certification, matching the knapsack and G1
CSP runs), and the mechanism gate confirms feedback was functionally
exercised in the guided arm (unlike G1's CSP run, where it was
confirmed inert). The sanity check proves the comparison is genuinely
single-variable — the same code, unmodified, still reproduces the
original temperature=0 finding exactly.

The result: a small positive point estimate (+3.85pts) favoring guided
retry, far from statistical significance (p=0.79) and far below the
pre-registered kill threshold (Δ≥7, p<0.05). Per the Evidence Escalation
Rule, this is reported as what it is — a valid, non-significant negative
result at this specific registered configuration — not overstated as
"guided doesn't help at all" (a different, broader claim this n cannot
support) and not understated as "still untested" (which would discard
real evidence, the mistake the H1a/H1b split exists to prevent).

## 10. Decision

**DELETE — scoped precisely to this registered configuration.**

Applying the pre-registered kill threshold to a measurement that, for the
first time, satisfies every precondition for validity: verifier-guided
retry with this feedback encoding does not beat blind retry with
statistical or practical significance, for `llama3.2:1b` on
`constraint_csp` at temperature 0.6 with `DeterministicPolicy`'s current
rule table.

**Scope of this DELETE, stated per the Evidence Escalation Rule:** this
does not establish that verifier-guided feedback cannot help in any
configuration — a different model, a richer feedback encoding (e.g.
structured repair hints instead of raw signal text), or a learned policy
(H2's registered question) remain untested. It establishes that *this*
specific, now-validly-tested mechanism does not clear the bar this
project pre-registered before looking at results.

**H1 status, final for this phase:** H1a — negative, configuration-specific
(unchanged). H1b — **tested and negative**, configuration-specific, for
the first time backed by a measurement that passes every validity gate
this project's Evidence Protocol requires.
