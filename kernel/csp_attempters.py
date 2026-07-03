"""Gamma Task 6 — LLM Attempters for the CSP H1 experiment.

The candidate generator under test. Deliberately NOT the solver (see the
contract-tension note in the implementation summary): H1 tests whether
verifier feedback helps an uncertain LLM proposer, which requires the
proposer to genuinely be uncertain. BlindCSPAttempter mirrors
kernel/edge_ai.py's BlindAttempter (nonzero temperature, ignores feedback
- true blind resampling). GuidedCSPAttempter mirrors GuidedAttempter
(temperature 0, reads the previous FailureSignal into the prompt).
"""

from __future__ import annotations

import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"


def _ollama_json(model, prompt, temperature, seed=0, num_predict=250, timeout_s=60):
    try:
        payload = json.dumps({
            "model": model, "prompt": prompt, "stream": False, "format": "json",
            "options": {"temperature": temperature, "num_predict": num_predict, "seed": seed},
        }).encode()
        req = urllib.request.Request(OLLAMA_URL, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            out = json.loads(resp.read())
        parsed = json.loads(out.get("response", "") or "{}")
        return parsed if isinstance(parsed, dict) else None, out.get("eval_count", 0)
    except Exception:
        return None, 0


def _prompt(spec: dict) -> str:
    proj_lines = "\n".join(f"- {p} ({spec['project_tags'][p]})" for p in spec["projects"])
    con_lines = "\n".join(f"- {c}" for c in spec["constraints"])
    return (
        "Assign each engineer to exactly one distinct project satisfying every "
        "constraint, or determine no valid assignment exists.\n\n"
        f"Engineers: {', '.join(spec['engineers'])}\n"
        f"Projects:\n{proj_lines}\n\nConstraints (as data, kind + fields):\n{con_lines}\n\n"
        'Respond with ONLY: {"satisfiable": true, "assignment": {"<engineer>": "<project>", ...}} '
        'or {"satisfiable": false} if you believe no valid assignment exists.'
    )


class BlindCSPAttempter:
    """B2 / H1 control: ignores prior FailureSignals, resamples at
    nonzero temperature - "blind resampling at temperature"."""

    def __init__(self, model: str = "llama3.2:1b"):
        self.model = model

    def attempt(self, state) -> dict:
        spec = state.formalization.get("spec")
        if spec is None:
            return {"solution": None, "tokens": 0}
        parsed, tokens = _ollama_json(self.model, _prompt(spec), temperature=0.6,
                                      seed=state.attempt)
        return {"solution": _to_solution(parsed), "tokens": tokens}


class GuidedCSPAttempter:
    """B3 / H1 treatment: reads the previous FailureSignals into the
    prompt. Default temperature=0 preserves the EXACT registered H1a
    configuration (whitepaper/HYPOTHESES.md) unchanged - GuidedCSPAttempter()
    with no args reproduces that finding bit-for-bit. temperature is a
    constructor parameter (not a new interface - Attempter is still the
    frozen protocol) so a temperature-matched H1b run can hold sampling
    strategy constant across arms, isolating feedback-presence as the
    only deliberately varied factor.

    seed=state.attempt is now passed unconditionally (previously only
    BlindCSPAttempter varied seed). Verified empirically before this
    change: seed is INERT at temperature=0 for this model/server (three
    seeds, byte-identical output) - greedy decoding ignores it - so this
    does not alter the temperature=0 default's behavior or its already-
    registered, already-cited result."""

    def __init__(self, model: str = "llama3.2:1b", temperature: float = 0.0):
        self.model = model
        self.temperature = temperature

    def attempt(self, state) -> dict:
        spec = state.formalization.get("spec")
        if spec is None:
            return {"solution": None, "tokens": 0}
        prompt = _prompt(spec)
        prior = state.verifier_result
        if prior and not prior.get("ok") and prior.get("signals"):
            prompt += "\n\nYour previous attempt failed:\n"
            for s in prior["signals"]:
                prompt += f"- {s['kind']} at {s['location']}: {s['evidence']}\n"
            prompt += "Propose a different assignment that fixes this specific problem."
        parsed, tokens = _ollama_json(self.model, prompt, temperature=self.temperature,
                                      seed=state.attempt)
        return {"solution": _to_solution(parsed), "tokens": tokens}


def _to_solution(parsed: dict | None) -> dict | None:
    if parsed is None:
        return None
    if parsed.get("satisfiable") is False:
        return {"satisfiable": False, "assignment": None}
    assignment = parsed.get("assignment")
    if isinstance(assignment, dict) and assignment:
        return {"satisfiable": True, "assignment": assignment}
    return None
