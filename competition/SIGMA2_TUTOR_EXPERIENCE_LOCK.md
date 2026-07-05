# Σ2 — Tutor Experience Lock (Submission Critical)

**Status: LOCKED.** Purpose: make EulerMind feel like software a student can
learn from, while preserving the project's core principle — **never claim more
certainty than the system has actually earned.**

## Mission

The tutor experience must make a student think *"I understand this now,"* while
making a judge think *"This system is honest about what it knows."* Every UI
decision must improve one of those two outcomes.

## Non-negotiable principle

**The UI is a visualization of what actually happened inside EulerMind — not an
animation, not a fabricated reasoning trace.** If the backend did not perform an
operation, the UI may not imply that it did.

## The two zones (the whole integrity story in one rule)

```
  MODEL ZONE  ───────────────  EULERMIND ZONE
  "the model suggested this"   "EulerMind proved this"
  Understanding / Method /      Machine Check / Trust Label
  Calculation / Answer          (deterministic, compiler-like)
  quiet, dashed, neutral        distinct, solid, colored
```

The reasoning section belongs to the **model**. The checking section belongs to
**EulerMind**. **They must never look identical.** A student must be able to see,
without reading a word, that one was *suggested* and one was *proved*.

## Execution pipeline (the UI exposes these real stages)

```
Student Question → Intent Router
   ├─ Certified Engine (kernel) → deterministic solver
   └─ Tutor Engine (Qwen Math)  → step-by-step reasoning (streamed)
                → Deterministic Checker → Trust Classification → Final Response
```

## Every visible box ↔ a real computation (the enforcement table)

This table is the lock. A box may exist only if this column can be filled.

| UI box | Zone | Backed by (real computation) |
|---|---|---|
| Understanding / Method / Calculation | Model | Qwen stream (`app/tutor.py`), structured by the section-header prompt |
| Answer (large) | Model | the `FINAL ANSWER:` line from the *same* stream — the exact string handed to the checker |
| Machine Check | EulerMind | `app/answer_checker.check_answer()` — deterministic substitution / recomputation / numeric-derivative |
| Trust Label + Why | EulerMind | the `label` from `check_answer` (Derived/Heuristic) or the kernel certificate lane (`Verified`) |
| Certified lane: Formalized / Solved / Verified / Independently checked | EulerMind | `app/local_demo.solve()` — kernel router + exact solver + re-checkable certificate + independent recheck |

## Visual hierarchy

`Answer` (highest) → `Machine Check` → `Trust Label` → `Reasoning` → `Understanding`
(lowest). Reading order follows generation (Understanding streams first); *emphasis*
follows this hierarchy (the Answer and the Check dominate).

## Trust label rules

- Never appears before checking.
- Never appears beside intermediate reasoning.
- Appears once, in the EulerMind zone, after the Machine Check, with a "Why?" line.

## Never allowed

- ❌ "Verified Step 1" / any trust label on an intermediate step
- ❌ Green checkmarks beside model reasoning
- ❌ Fake execution animations / simulated verification
- ❌ Pretending the checker examined intermediate reasoning
- ❌ "Thinking…" when nothing is happening

## The one design principle

**Every visible box on the screen must correspond to a real computation
performed by EulerMind.** Nothing exists purely for aesthetics; nothing implies
work that never happened.

## Integrity reconciliations (read before building — these prevent the trap)

1. **"Understanding" is the *model's* stated understanding, not a deterministic
   classifier.** The original sketch showed "extracted problem type / detected
   topic" as if EulerMind detected it. We do **not** have a deterministic
   topic classifier in the pre-answer path, so Understanding is rendered in the
   **model zone** (the model restating the question), never as an EulerMind
   detection badge. If a real classifier is later wired (the checker's
   shape-dispatch could seed one), it may graduate to the EulerMind zone — not
   before. Until then: model zone, neutral styling.
2. **The big Answer is the checked string.** The large Answer box shows the
   `FINAL ANSWER:` line verbatim — the identical string passed to
   `check_answer`. This guarantees "the answer you see is the answer we
   checked," an integrity property in its own right. (So the model is prompted
   for Understanding/Method/Calculation + a `FINAL ANSWER:` line; the UI does
   not invent a separate answer.)
3. **Graceful, honest fallback.** Small models won't always emit the section
   headers. When headers are absent the UI falls back to generic `Step N`
   segmentation of the same text — structuring presentation, never inventing
   reasoning. No headers ≠ fake headers.

## Success criteria

- A judge understands the interface in < 15 s.
- A secondary-school student understands it in < 30 s.
- A teacher immediately sees the distinction between explanation, computation,
  verification, and confidence.

## Educational layer (LOCKED as spec; built after the core faithful render)

Below the trust label: *Try another example · Show another method · Explain more
simply · Common mistakes.* Each button is a **real** action — a re-query of the
model or an example load — never a canned animation. Implemented after the core
zones ship; specced here so it isn't reinvented ad hoc.
