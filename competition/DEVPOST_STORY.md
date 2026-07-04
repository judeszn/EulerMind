# Devpost project story — ready to paste (flows FROM the submission repo)

**Tagline (if asked):** Offline mathematical reasoning for the hardware
Africa already has — every answer certified twice.

---

## Inspiration

The bottleneck for AI in Africa isn't models — it's access economics and
trust. A student in Lagos or an SME owner in Dakar can't depend on cloud
APIs, and can't afford to act on a confidently wrong local answer
either. The failure mode that actually hurts people is not "no answer" —
it's a wrong answer delivered with confidence. We built EulerMind around
that exact risk.

## What it does

EulerMind runs a math-specialized 1.5B model (Qwen2.5-Math, GGUF Q4_K_M,
llama.cpp) entirely offline on an 8 GB laptop — and wraps it in a
deterministic verification pipeline. For resource-allocation,
assignment, and linear-programming problems, the language model's job
ends at understanding the text: a parser-first formalizer produces a
formal specification, an exact solver computes the answer, a verifier
issues a re-checkable certificate, and a second, independently-written
checker re-proves it. For LP, the checker doesn't even reuse the
solver's approach — the solver uses the Fundamental Theorem of LP, the
checker uses LP Duality. Two unrelated theorems must agree before
anything is labeled "Verified." Outside those domains, EulerMind answers
with the model and says so honestly — the trust label is earned by
machinery, never asserted.

## How we built it

Research-first, with pre-registered hypotheses and kill thresholds.
Every architectural claim traces to a registered experiment: 192/192
certificates independently agreed across three domains, 0% false
certification, byte-identical reproduction across OS and CPU
architecture on every push (GitHub Actions). Model selection was
measured, not guessed: 8 candidate GGUFs profiled through the official
ADTC profiler on x86 CI, 3 finalists benchmarked on GSM8K under
identical settings, winner chosen by a selection rule committed before
any accuracy data existed.

## Challenges we ran into

Our own hypothesis died: we pre-registered "verifier-guided retry beats
blind retry," measured it rigorously, and the data rejected it. We kept
the negative result and rebuilt the thesis around what the evidence
actually supports — deterministic certification. Separately, a
hypothesis-driven experiment exposed a parser defect our field-level
metrics were structurally blind to; we root-caused it, repaired it, and
proved bit-exact non-regression on every frozen result.

## Accomplishments we're proud of

0% false certification, measured, across every domain. A negative result
published instead of buried. A pipeline that reproduces byte-for-byte on
hardware it's never seen. And a system that refuses to fabricate — when
a problem is outside its certified domains, it labels the answer "Open"
and says exactly why.

## What we learned

Trust is an engineering deliverable. A 1.5B model on a commodity laptop
can be *more* trustworthy than a frontier model in the cloud — if you
stop asking the model to check its own work.

## What's next

Extending certification to calculus (the design exists: Sturm's theorem
for completeness, a different theorem than the solver's — continuing the
two-theorem pattern), and African-language formalization, which is also
the honest path to reopening our formalization-checking research line.

---

*Numbers in this story: peak RAM 1,699 MB and 15.68 tok/s from the
official adtc-profiler on clean x86 CI (run 28691529653); GSM8K 68%
(n=50, seed 42, run 28684426883); certificate evidence in the research
repo. Nothing here is aspirational.*
