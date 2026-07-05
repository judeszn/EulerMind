# Production Environment — 15-minute rebuild guide

Target: the exact offline stack used for the ADTC demo. **No Ollama, no
cloud, no internet at runtime.** GGUF → llama.cpp → EulerMind.

Reference machine: Mac M1, 16 GB RAM (works on any 4 GB+ machine — peak RAM
of the whole stack is ~1.7 GB, measured on audit-like x86 CI, run 28683815170).

## 1. Install llama.cpp (2 min)

```sh
brew install llama.cpp          # macOS
# Linux: https://github.com/ggml-org/llama.cpp/releases (or build from source)
llama-server --version          # sanity
```

## 2. Download the competition model (5 min, one-time, ~1.0 GB)

The ratified model (competition/MODEL_DECISION.md): **Qwen2.5-Math-1.5B-Instruct,
Q4_K_M GGUF.**

```sh
mkdir -p models/qwen2.5-math-1.5b
curl -L -o models/qwen2.5-math-1.5b/model.gguf \
  'https://huggingface.co/Qwen/Qwen2.5-Math-1.5B-Instruct-GGUF/resolve/main/qwen2.5-math-1.5b-instruct-q4_k_m.gguf'
```

(If the exact filename 404s — Hugging Face occasionally renames — list the
repo's files at huggingface.co/Qwen/Qwen2.5-Math-1.5B-Instruct-GGUF and take
the `q4_k_m` one. This is the ONLY internet-requiring step; after it, the
machine can go offline permanently.)

## 3. Run everything (1 command)

```sh
./run_demo.sh          # preflight → llama-server → demo UI at :7860
./run_demo.sh check    # preflight only
```

The script reuses an already-running llama-server, waits for model
readiness, and fails loudly with instructions if anything is missing.
Server log: `/tmp/eulermind-llama.log`.

## 4. Verify offline (the judge moment)

1. Start the stack. 2. **Turn Wi-Fi off.** 3. Paste a question.
Everything must keep working — model, checker, UI all bind 127.0.0.1 only.

Hard verification (macOS): `lsof -i -P | grep -E 'llama|python3'` — every
line must show `127.0.0.1` (loopback), nothing external.

## 5. Reality check on the REAL model (Σ3 Phase 1, ship model)

```sh
python3 -m app.reality_check
# -> competition/reality_check_transcript.md (12 WAEC questions, trust
#    labels, false-verification count — must be 0)
```

`app/tutor.py` probes llama-server (:8080) BEFORE Ollama (:11434), so with
the production stack up, all tooling automatically uses the competition
model. Then do the Phase 2 explanation audit on that transcript.

## 6. Benchmark numbers (record in scoreboard.md)

```sh
llama-bench -m models/qwen2.5-math-1.5b/model.gguf     # tokens/sec
# peak RAM: run a reality check while watching:
/usr/bin/time -l python3 -m app.reality_check 2>&1 | grep "maximum resident"  # macOS
```

Submission numbers must come from audit-like x86 CI (drift tolerance
±25% TPS / ±15% RAM — docs/SCORING.md), not the M1; local numbers are
for rehearsal and regression only.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `llama-server not found` | `brew install llama.cpp`, reopen terminal |
| model 404 on download | list the HF repo files, take the `q4_k_m` GGUF |
| server slow to start | first load reads ~1 GB from disk; script waits up to 120 s |
| UI says "tutor lane offline" | check `/tmp/eulermind-llama.log`; is the port 8080 taken? |
| answers stream but no labels | that's the checker being honest (Heuristic); paste a solvable equation to see Derived |
| anything phones home | it must not — file a bug; all sockets are 127.0.0.1 |

## What this deliberately does NOT include

No pip installs (stdlib only), no Docker, no GPU flags, no env vars. If a
step here can't be done from a fresh checkout + brew + one curl, it's a bug
in this guide.
