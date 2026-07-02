"""B0 — naive direct-answer baseline. The floor.

The model reads the problem and emits a JSON answer. No tools, no loop, no
verification. Trust label is always Heuristic (Law 1: unverified LLM output
never claims more). Every subsequent system (tool loop, blind resample,
verifier feedback) must beat this number to justify its existence.

Inference via local Ollama (stdlib urllib only — the experiment must not
add dependencies to measure a model that talks HTTP).
"""

from __future__ import annotations

import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"

FORMAT_HINTS = {
    "lp": ('{"x": <units of the first product, number>, '
           '"y": <units of the second product, number>, '
           '"profit": <maximum total profit, number>}'),
    "calculus": ('{"critical_points": [{"x": <number>, '
                 '"type": "local_max" or "local_min"}, ...]}'),
    "csp": ('{"satisfiable": true or false, '
            '"assignment": {"<engineer name>": "<Project letter>", ...}} '
            '(omit "assignment" if not satisfiable)'),
}


class OllamaDirectSolver:
    def __init__(self, model: str = "qwen2.5:1.5b", timeout_s: int = 180,
                 num_predict: int = 800, temperature: float = 0.0, seed: int = 0):
        self.model = model
        self.timeout_s = timeout_s
        self.options = {"temperature": temperature, "num_predict": num_predict,
                        "seed": seed}
        self.name = f"b0-direct-{model.replace(':', '-')}"

    def _generate(self, prompt: str) -> dict:
        payload = json.dumps({
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": self.options,
        }).encode()
        req = urllib.request.Request(OLLAMA_URL, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            return json.loads(resp.read())

    def solve(self, problem: dict) -> dict:
        hint = FORMAT_HINTS[problem["answer_spec"]["type"]]
        prompt = (
            "Solve this mathematics problem. Respond with ONLY a JSON object "
            "in exactly this format, no other text:\n"
            f"{hint}\n\n"
            f"Problem:\n{problem['text']}\n"
        )
        try:
            out = self._generate(prompt)
            answer = json.loads(out.get("response", "") or "{}")
            tokens = out.get("eval_count", 0)
        except Exception:
            answer, tokens = None, 0
        return {"answer": answer if isinstance(answer, dict) else None,
                "trust_label": "Heuristic",  # unverified — never more (Law 1)
                "attempts": 1,
                "tokens": tokens}
