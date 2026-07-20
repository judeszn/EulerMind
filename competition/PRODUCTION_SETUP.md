# Production Environment — 15-minute rebuild guide

Target: the exact offline stack used for the ADTC demo. **No Ollama, no
cloud, no internet at runtime.** GGUF → llama.cpp → EulerMind.

Tested on macOS (M1) and Linux x86 (the same environment the official
ADTC profiler audits on). Works on any 4 GB+ machine — peak RAM of the
whole stack is ~1.7 GB, measured on audit-like x86 CI, run 28683815170.

## 1. Install llama.cpp (2 min)

**macOS**
```sh
brew install llama.cpp
```

**Linux** — either Homebrew (identical command, Homebrew works on Linux
too), or build from source (universal, no package-manager assumptions):
```sh
brew install llama.cpp
# --- or, build from source ---
sudo apt install -y build-essential cmake git   # Debian/Ubuntu; use your
                                                # distro's equivalent packages
git clone https://github.com/ggml-org/llama.cpp
cmake -B llama.cpp/build -S llama.cpp -DCMAKE_BUILD_TYPE=Release
cmake --build llama.cpp/build --config Release -j
export PATH="$PWD/llama.cpp/build/bin:$PATH"    # add to your shell profile
                                                # to persist across sessions
```

**Windows** — install WSL2, then follow the Linux steps above (this also
matches the x86 Linux environment the ADTC profiler audits on — running
under WSL2 is the closest local match to how the submission gets scored).
Alternatively, download a prebuilt `llama-*-bin-win-*.zip` from
[github.com/ggml-org/llama.cpp/releases](https://github.com/ggml-org/llama.cpp/releases)
and add its folder to `PATH`.

```sh
llama-server --version          # sanity, all platforms
```

## 2. Download the competition model (5 min, one-time, ~1.0 GB)

The ratified model (competition/MODEL_DECISION.md): **Qwen2.5-Math-1.5B-Instruct,
Q4_K_M GGUF.**

```sh
mkdir -p model
curl -L -o model/Qwen2.5-Math-1.5B-Instruct-Q4_K_M.gguf \
  'https://huggingface.co/bartowski/Qwen2.5-Math-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-Math-1.5B-Instruct-Q4_K_M.gguf'
```

(Same URL and path the submission repo's `download_model.sh` uses and
CI has verified end-to-end — see
[github.com/judeszn/eulermind-adtc-submission](https://github.com/judeszn/eulermind-adtc-submission).
If the exact filename 404s — Hugging Face occasionally renames — list the
repo's files at huggingface.co/bartowski/Qwen2.5-Math-1.5B-Instruct-GGUF
and take the `Q4_K_M` one. This is the ONLY internet-requiring step;
after it, the machine can go offline permanently.)

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

Hard verification: `lsof -i -P | grep -E 'llama|python3'` (macOS and most
Linux) — every line must show `127.0.0.1` (loopback), nothing external.
If `lsof` isn't installed (common on minimal Linux images), use
`ss -tlnp | grep -E ':8080|:7860'` instead — same check, different tool.

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
llama-bench -m model/Qwen2.5-Math-1.5B-Instruct-Q4_K_M.gguf     # tokens/sec

# peak RAM: run a reality check while watching. The `time` FLAG differs by
# OS — macOS/BSD uses -l, Linux (GNU time) uses -v. The shell's own `time`
# builtin supports neither flag, so call the standalone binary explicitly.
/usr/bin/time -l python3 -m app.reality_check 2>&1 | grep "maximum resident"   # macOS
/usr/bin/time -v python3 -m app.reality_check 2>&1 | grep "Maximum resident"   # Linux
#   ^ if /usr/bin/time is missing on Linux: sudo apt install time
```

Submission numbers must come from audit-like x86 CI (drift tolerance
±25% TPS / ±15% RAM — docs/SCORING.md), not the M1; local numbers are
for rehearsal and regression only.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `llama-server not found` | macOS/Linux: `brew install llama.cpp`, reopen terminal. No Homebrew? See §1's build-from-source steps. Windows: use WSL2 |
| model 404 on download | list the HF repo files, take the `q4_k_m` GGUF |
| server slow to start | first load reads ~1 GB from disk; script waits up to 120 s |
| UI says "tutor lane offline" | check `/tmp/eulermind-llama.log`; is the port 8080 taken? |
| answers stream but no labels | that's the checker being honest (Heuristic); paste a solvable equation to see Derived |
| anything phones home | it must not — file a bug; all sockets are 127.0.0.1 |

## What this deliberately does NOT include

No pip installs (stdlib only), no Docker, no GPU flags, no env vars. Every
step above has a macOS command, a Linux command that doesn't assume any
particular package manager, and a Windows path (WSL2, or a prebuilt
binary). If a step here only works on one OS, it's a bug in this guide.
