"""L1 / B1 — Reasoning Prompt baseline. The model's best unaided effort.

Same model as L0, but chain-of-thought is allowed: reason step by step,
then emit the final answer as a JSON object. No tools, no verification —
trust label stays Heuristic (Law 1). L1 minus L0 measures the value of
letting the model think; L2 minus L1 will measure the value of tools.
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
    "csp": ('{"satisfiable": true, "assignment": {"<engineer>": "<Project X>", ...}} '
            'or {"satisfiable": false} if no valid assignment exists'),
}


def extract_last_json(text: str):
    """Return the parseable JSON object whose closing brace is latest in the
    text (outermost wins on ties) — the model's final answer."""
    best = None  # (end, -start, obj): prefer latest end, then outermost start
    starts = [i for i, ch in enumerate(text) if ch == "{"]
    for start in starts:
        depth = 0
        for j in range(start, len(text)):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[start:j + 1])
                    except json.JSONDecodeError:
                        pass
                    else:
                        if isinstance(obj, dict):
                            key = (j, -start)
                            if best is None or key > best[0]:
                                best = (key, obj)
                    break
    return best[1] if best else None


class OllamaReasoningSolver:
    def __init__(self, model: str = "qwen2.5:1.5b", timeout_s: int = 300,
                 num_predict: int = 1500, temperature: float = 0.0, seed: int = 0):
        self.model = model
        self.timeout_s = timeout_s
        self.options = {"temperature": temperature, "num_predict": num_predict,
                        "seed": seed}
        self.name = f"l1-reasoning-{model.replace(':', '-')}"

    def _generate(self, prompt: str) -> dict:
        payload = json.dumps({
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": self.options,
        }).encode()
        req = urllib.request.Request(OLLAMA_URL, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            return json.loads(resp.read())

    def solve(self, problem: dict) -> dict:
        hint = FORMAT_HINTS[problem["answer_spec"]["type"]]
        prompt = (
            "Solve this mathematics problem carefully, step by step. Show "
            "your reasoning. Then, on the final line, output ONLY a JSON "
            "object in exactly this format:\n"
            f"{hint}\n\n"
            f"Problem:\n{problem['text']}\n"
        )
        try:
            out = self._generate(prompt)
            answer = extract_last_json(out.get("response", ""))
            tokens = out.get("eval_count", 0)
        except Exception:
            answer, tokens = None, 0
        return {"answer": answer,
                "trust_label": "Heuristic",  # still unverified (Law 1)
                "attempts": 1,
                "tokens": tokens}
