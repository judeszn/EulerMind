# Model bake-off — plan

**Hypothesis.** Another compact model (≤ ~1.2 GB Q4) gives a materially
better L1 starting point than qwen2.5:1.5b within the RAM budget.

**Why at L1, not L0.** L0 force-suppresses reasoning (JSON-only output),
which penalizes reasoning-tuned models (deepseek-r1-distill) unequally.
The discriminating rung is L1: best unaided effort.

**Candidates.** qwen2.5:1.5b (incumbent), qwen2.5-math-1.5b (competition
candidate — needs GGUF via llama.cpp, not on Ollama), deepseek-r1-distill
1.5b (reasoning-tuned), gemma3:1b, llama3.2:1b.

**Metrics.** L1 accuracy on the standard 30-problem dev subset; tokens/sec
(S_perf is 30% of the final score); model RAM class.

**Acceptance.** A challenger must beat the incumbent by >10pts on the
30-problem subset (small-n noise floor) to trigger a full-dev-split
confirmation run. Tokens/sec regression of >30% requires the accuracy gain
to be confirmed on the full dev split before switching.

**Kill threshold.** No challenger clears the bar → incumbent stays,
bake-off closes, decision recorded in scoreboard.md.

**Expected score gain.** Unknown → that is exactly why it's an experiment
(48h clock from results landing).
