# Prompt strategy — locked (Sprint Δ1, 2026-07-03)

## Locked principles

1. **Prompts are registered experiments** — baseline → intervention →
   measured comparison → keep/reject. Same methodology as Gamma, new
   variable. No "this feels better."
2. **Every prompt strategy is benchmarked across all finalists**, never
   tuned to one model. The prompt×model matrix decides which model
   naturally aligns with the pipeline — measured, not guessed.
3. **Grading is deterministic and already built**: prompt outputs are
   scored by `benchmark.metrics.grade()` against existing ground-truth
   instances (4 categories, exact graders). No LLM-judge, no rubric
   invention. The harness runs a candidate GGUF (llama-server) on
   existing benchmark problems under each prompt strategy and grades
   mechanically — plus token count, latency, and fabrication checks
   (claimed numbers not present in the source text).
4. **Scope honesty**: our prompts never enter the automated score
   (lm_eval uses its own templates; llama-bench uses synthetic tokens).
   Prompt work optimizes exactly three surfaces: the 2 `test_prompts`
   in metadata.json, the demo, and REPORT evidence. Effort is sized to
   that — a focused harness, not a research program.

## Locked prohibition: no simulated-tool prompts

Prompts that instruct a bare model to role-play machinery it does not
have ("You have 2 tools: Regex_Parser, ILP_Solver... STEP 3 [Solver]:
Verify C1-C4") are **banned** from this project's submissions, demos,
and test prompts. A bare GGUF will *pretend* to parse, *pretend* to
verify, and emit "Verified" — a fabricated trust label wearing
EulerMind's vocabulary with none of its machinery. That is Law 1's
target failure mode, built into a prompt on purpose. One probing judge
question ("show me the parser's actual output") exposes it as theater.

The honest division, decided by Assumption A-02's answer:
- **World B (application judged):** the real pipeline parses/solves/
  verifies — the prompt needs no tool fiction, and trust labels are
  earned by running code.
- **World A (bare model judged):** prompts ask for clean structured
  reasoning and honest uncertainty ("state what you cannot verify"),
  and never claim verification that didn't happen.
The trust-taxonomy vocabulary (Verified/Derived/Heuristic/Open) appears
in a prompt ONLY where the machinery that backs it actually runs.

Also noted for the record: the draft prompts circulating with framing
like "attacks Units 28%" cite pre-Intervention-1A/1B/D1 failure rates.
Those failure modes were repaired and re-measured months ago (parser at
100% on native + paraphrase splits, `research/D1_parser_repair/`). We
do not rebuild solved problems.

## Sequencing (locked)

Prompt harness work starts **after** Phase 2 model selection completes
(its stop condition is active), and its design is finalized after the
A-02 answer arrives (World A vs B changes what the 2 test_prompts
should ask for). Candidate prompt-strategy axes registered now, to be
measured then: baseline direct-question · structured-extraction-first ·
show-your-constraint-checking · African-SME framing (doubles as the
use-case bonus surface). Each measured on existing LP/CSP/edge_ai
instances across all finalists.
