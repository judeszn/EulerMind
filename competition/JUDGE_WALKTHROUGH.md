# Judge walkthrough — minute-by-minute (live demo / video spine)

Preflight (before any judge is watching): `python3 -m app.local_demo`
running; browser tab on `localhost:7860`; Wi-Fi ON (you'll kill it on
camera); terminal with the GitHub Actions page pre-loaded in a second
tab (for the reproduction beat). Nothing else open.

| Time | Action | Say |
|---|---|---|
| 00:00 | Face the problem, not the tool | "SMEs and students across Africa have real quantitative decisions — and no way to check an AI's arithmetic." |
| 00:15 | **Turn Wi-Fi off, visibly** | "Internet off. Everything from here is local — an ordinary 8 GB laptop." |
| 00:20 | Show the browser at `localhost:7860` | "This is EulerMind. Not a chatbot — a certified reasoning pipeline." |
| 00:35 | Click **"Lagos workshop (test prompt 1)"** → Solve | "A Lagos furniture workshop's production plan — this is literally one of our registered competition prompts." |
| 00:50 | Point at the four stages as they show green | "Formalized by a deterministic parser — zero hallucination surface. Solved exactly. Certified. And then re-proved by a second, independently-written checker using a *different theorem*. Two pieces of math must agree." |
| 01:10 | Point at **Verified** + the answer (30 chairs, 30 tables, ₦345,000) | "Thirty and thirty, three-forty-five thousand — and that label was earned by machinery, not asserted by a model." |
| 01:20 | Paste any out-of-domain question → Solve | "And when it can't prove something?" |
| 01:35 | Point at **Open** | "It says so. No fabricated confidence — the label is Open and it tells you why. That refusal is the most important feature on this screen." |
| 01:50 | (If time / Q&A) second tab: green CI run | "Every claim you just saw re-verifies on independent hardware on every change — byte-for-byte." |
| 02:00 | End | "Answers you can check, on the machines Africa already owns." |

## Q&A pivots (only if asked)

- **"How do I know the checker isn't wrong the same way the solver is?"**
  → It can't be: for LP the solver uses the Fundamental Theorem of LP
  (vertex enumeration); the checker uses LP Duality and performs zero
  search. No shared code, no shared theorem.
- **"What if the problem is out of scope?"** → You saw it — Open label,
  honest refusal. The model still answers general questions; it just
  never wears a Verified badge it didn't earn.
- **"What's the model?"** → Qwen2.5-Math-1.5B, Q4_K_M, llama.cpp —
  selected by measured benchmark, 1.7 GB peak RAM, chosen by a selection
  rule committed before the accuracy data existed.
- **"Did anything fail during development?"** → Yes, and it's in the
  repo: our original hypothesis (verifier-guided retry) was rejected by
  our own pre-registered decision rule. We kept the negative result and
  built on what the evidence supported.

## Never do live

- Don't paste a benchmark-template problem and call it a customer
  problem — use the shipped test prompts; they're real SME phrasing and
  they certify.
- Don't say "the model verifies its answer" — the *pipeline* verifies
  the answer; the model only reads the problem.
- Don't skip the Open/refusal beat to save time. It is the thesis.
