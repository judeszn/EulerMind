# 2-minute video script (Devpost requirement)

Target: 1:55. One continuous screen recording + voiceover. Every claim
in the script is measured and citable — nothing aspirational.

| Time | Screen | Voiceover |
|---|---|---|
| 0:00–0:15 | Title card: "EulerMind — offline mathematical reasoning, certified twice." Then: Wi-Fi menu, **turn Wi-Fi off on camera** | "This is EulerMind, running on an ordinary 8-gigabyte laptop. First thing I'll do is turn off the internet — everything you're about to see is fully local." |
| 0:15–0:35 | Browser: `localhost:7860`. Click "Lagos workshop (test prompt 1)" — the ACTUAL registered competition prompt. Press Solve | "A furniture workshop needs a production plan — this is one of our registered competition prompts, verbatim. EulerMind doesn't just ask a language model — it converts the problem into a formal specification with a deterministic parser. Zero hallucination surface." |
| 0:35–1:00 | The four pipeline stages tick green; Verified badge; answer visible | "Then an exact solver finds the optimum, a verifier issues a certificate — and here's the part nobody else does: a *second, independently-written checker* re-proves the answer using a completely different theorem. Two pieces of math, one answer. If either disagreed, you'd see it refuse." |
| 1:00–1:20 | Paste the CSP volunteer-assignment example → Verified. Then paste an out-of-domain question → **Open** label appears | "Same engine, different domain — staff assignment, certified the same way. And when a problem is outside what it can prove? It says so. This label means 'not verified' — EulerMind never fabricates certainty." |
| 1:20–1:40 | Split shot / cut: GitHub Actions green run + REPORT.md benchmark table | "Under the hood: a math-specialized 1.5-billion-parameter model, 1.7 gigabytes of RAM at peak — a quarter of the budget — measured by the official competition profiler. And the entire pipeline reproduces byte-for-byte on independent hardware, automatically, on every change." |
| 1:40–1:55 | Back to the app; the ✓ Offline badge; end card with repo URL | "Built for the student in Lagos, the SME in Dakar, the extension officer in Arusha — the machines Africa already owns, with answers you can actually trust. EulerMind." |

## Recording checklist
- [ ] Wi-Fi visibly toggled off in-frame (the trust beat — do not cut it)
- [ ] Use the built-in example buttons — the two SHIPPED test prompts certify end-to-end (regression-tested, research/D5_prompt_compat/)
- [ ] Show the Open/refusal case — honesty is the differentiator, not a blooper
- [ ] 1080p, cursor visible, no dead air over 2s
- [ ] No claims beyond the script — every number here traces to a CI run
