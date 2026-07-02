# Expected demo output — STATUS: NOT YET MEASURED

Update discipline (mirrors `benchmark/datasets/CHANGELOG.md`): **never
overwrite silently.** Once Phase 1C produces a real, reviewed run, this
file becomes the frozen baseline for `actual_output.md` to diff against —
but if the pipeline later legitimately improves (Phase 1D generalization
touching the Edge AI path, a better formalizer prompt, etc.), the baseline
may be deliberately updated, with a one-line dated reason appended below.
A hard "never update, ever" would make this file stale the first time we
make the system better.

## Baseline history

- (none yet — filled in on the first real Phase 1C run)

---

This file is a placeholder until Phase 1C's real pipeline (Formalizer +
Executor + Verifier + Policy against `llama3.2:1b`) actually runs
`demo/prompt.md` end to end. It is intentionally empty of claims until
then — writing a fabricated "expected" trace here before the real pipeline
exists would be exactly the kind of certainty-fabrication Law 1 forbids
the system from doing, applied to our own demo materials.

What this file will contain once Phase 1C produces a real run:
- The formalization the LLM extracted (variables/budgets/constraint)
- Each attempt's answer, verifier verdict, and FailureSignal (if any)
- The policy's next_action decision at each failure
- The final trust label and the reproducible trace log path
- Peak RAM and wall-clock time for the run

Do not hand-author this file from Oracle Mode's output — Oracle Mode
reads ground truth directly (it exists to validate the kernel loop, not
to stand in for a real result) and using its trace here would misrepresent
a mechanical validation as a measured demo result.
