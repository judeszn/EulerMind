# Decision: which "Edge AI" benchmark families to build

A pitch proposed reframing the benchmark domain from textbook math to
AI-systems-flavored engineering math, with 5 new procedural generator
families. Evaluated against WIN.md's Guardrail Zero (every addition must
name a rubric line it serves) and No Vertical/Horizontal Optimization.

## Adopted

**Edge AI Deployment** (`benchmark/generator/edge_ai.py`, dataset v1) — an
integer knapsack: deploy-counts per model type, maximize weighted
accuracy/latency score under RAM/FLOPS/latency budgets. Built because:
genuinely new capability coverage (our LP generator was continuous-only;
this is real integer programming), cheap (same construction discipline as
the existing generators, stdlib-only ground truth via enumeration), and
directly serves S_acc's "cross-disciplinary integration" plus the African
Use Case bonus (edge AI deployment under hardware constraints is exactly
the competition's own theme).

## Rejected or already built — not new work

- **"Verifier Challenge"** (inject a wrong solution, system must detect +
  repair + verify): already built. This is `FlakyOracleAttempter`'s
  sabotage logic in `kernel/oracle.py`, running since Phase 0. Needs
  packaging as demo material, not a new generator.
- **"Formalization" (messy English -> extract LP)**: already H3. Every
  generator's clean/messy paired variants already test exactly this.
- **ML Pipeline Scheduling** (dependency graphs, deadlines, throughput):
  a genuinely separate solver problem (graph + scheduling), not a cheap
  reskin. Deferred — would compete with Phase 1C for time.
- **Quantized Model Selection** (Q2-Q8 variants, same knapsack shape):
  legitimate but redundant with Edge AI Deployment's coverage for now.
  Deferred.

## The "prompt template" this was paired with

The proposed 9-step ROLE/STEP prompt structure (extract variables ->
validate -> solve -> verify -> FailureSignal -> retry -> trust label) is,
almost line for line, the kernel loop already built (formalize -> attempt
-> execute -> verify -> Policy -> retry -> trust label). Useful as demo
copy explaining the architecture in domain language. **Not adopted as an
implementation mechanism** — a single prompt asking a model to do all 9
steps in one generation relies on the model checking its own arithmetic,
which is exactly L1's measured failure mode (the model hallucinated
constraints, "verified" them against itself, and returned a confident
wrong answer — see `research/L1_reasoning_prompt/RESULTS.md`).
