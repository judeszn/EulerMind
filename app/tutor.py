"""Sigma-1 Tutor Lane — local model client (stdlib only).

Speaks the OpenAI-compatible /v1/chat/completions streaming protocol,
which BOTH llama.cpp's llama-server (the ADTC-required runtime) and
Ollama (developer convenience) expose. Probes llama-server first.

The model is prompted for step-by-step tutoring and a machine-parseable
FINAL ANSWER line. It is NEVER asked to assess or label its own
correctness - labels come from app/answer_checker.py exclusively
(competition/PROMPT_STRATEGY.md: model self-verification is the banned
fabricated-certainty pattern).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

CANDIDATE_SERVERS = ("http://127.0.0.1:8080", "http://127.0.0.1:11434")

SYSTEM_PROMPT = (
    "You are a patient mathematics tutor for West African secondary school "
    "students preparing for WAEC/SSCE-level exams. Explain step by step in "
    "clear, simple language. Show the working, not just the result. "
    "If the question asks for a computation, end your reply with exactly "
    "one line in this format:\n"
    "FINAL ANSWER: <the answer only>\n"
    "If the question asks for an explanation rather than a computation, "
    "end with:\nFINAL ANSWER: see explanation\n"
    "If you cannot solve the problem, say so plainly instead of guessing."
)


def discover_server(timeout: float = 0.8) -> tuple[str, str] | None:
    """Returns (base_url, model_id) of the first live server, else None."""
    for base in CANDIDATE_SERVERS:
        try:
            with urllib.request.urlopen(f"{base}/v1/models", timeout=timeout) as r:
                data = json.loads(r.read())
            models = [m.get("id", "") for m in data.get("data", [])]
            if models:
                preferred = next(
                    (m for pref in ("math", "qwen") for m in models
                     if pref in m.lower()), models[0])
                return base, preferred
        except (urllib.error.URLError, OSError, json.JSONDecodeError):
            continue
    return None


def stream_tutor_answer(question: str, base: str, model: str):
    """Yields text chunks from the local model. Raises on connection loss."""
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                     {"role": "user", "content": question}],
        "stream": True,
        "temperature": 0.2,
        "max_tokens": 900,
    }).encode()
    req = urllib.request.Request(
        f"{base}/v1/chat/completions", data=payload,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        for raw in resp:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            body = line[5:].strip()
            if body == "[DONE]":
                return
            try:
                delta = json.loads(body)["choices"][0]["delta"]
            except (json.JSONDecodeError, KeyError, IndexError):
                continue
            chunk = delta.get("content")
            if chunk:
                yield chunk
