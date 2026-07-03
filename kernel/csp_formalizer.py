"""Gamma Task 1 — CSP Formalizer for constraint_csp.

Parser-first, deterministic wherever the source is explicit; LLM performs
semantic association only, and only when deterministic extraction cannot
apply, per the frozen contract. The four constraint kinds are rendered by
benchmark/generator/csp.py from FIXED deterministic templates (not
paraphrased prose, unlike edge_ai_deployment) - so a template-matching
parser, not a value-semantic one, is the right tool here: the templates
are the "explicit structure" this domain presents.

Output spec shape (identical to what the solver consumes):
{engineers: [...], projects: [...], project_tags: {proj: tag},
 constraints: [{"kind": ..., ...fields}]}

Independent of benchmark/ - the four render templates are duplicated here
by necessity (parsing is the inverse of benchmark/generator/csp.py's
_render(), not an import of it).
"""

from __future__ import annotations

import json
import re
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"

FORBIDDEN_RE = re.compile(r'^-?\s*(\w+) cannot be assigned (Project \w+)\.$')
EXACT_TAG_RE = re.compile(r'^-?\s*Exactly (\d+) engineers? must be assigned (\w+) projects\.$')
NOT_BOTH_TAG_RE = re.compile(r'^-?\s*(\w+) and (\w+) cannot both be assigned (\w+) projects\.$')
IMPLIES_RE = re.compile(
    r'^-?\s*If (\w+) is assigned (Project \w+), then (\w+) must be assigned (Project \w+)\.$')

PROJECT_LINE_RE = re.compile(r'^-\s*(Project \w+)\s*\((\w+)\)\s*$')
INTRO_RE = re.compile(
    r'([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)*(?:\s+and\s+[A-Z][a-z]+)?)'
    r'[—\-]must each be assigned exactly one project', re.IGNORECASE)
# The intro sentence uses an em-dash on both sides: "Five engineers—A, B and C—must..."
INTRO_NAMES_RE = re.compile(r'engineers[—\-]([^—\-]+)[—\-]must each be assigned')


def parse_engineers(text: str) -> list[str] | None:
    m = INTRO_NAMES_RE.search(text)
    if not m:
        return None
    raw = m.group(1)
    raw = raw.replace(" and ", ", ")
    names = [n.strip() for n in raw.split(",") if n.strip()]
    return names or None


def parse_projects(text: str) -> dict | None:
    tags = {}
    for line in text.splitlines():
        m = PROJECT_LINE_RE.match(line.strip())
        if m:
            tags[m.group(1)] = m.group(2)
    return tags or None


def parse_constraints(text: str) -> tuple[list[dict], list[str]]:
    """Returns (parsed_constraints, unparsed_lines). Unparsed lines are the
    explicit fallback signal - each becomes a candidate for the LLM."""
    parsed, unparsed = [], []
    in_section = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("Constraints:"):
            in_section = True
            continue
        if not in_section or not line.startswith("-"):
            continue
        body = line[1:].strip()
        m = FORBIDDEN_RE.match("- " + body)
        if m:
            parsed.append({"kind": "forbidden", "engineer": m.group(1), "project": m.group(2)})
            continue
        m = EXACT_TAG_RE.match("- " + body)
        if m:
            parsed.append({"kind": "exact_tag", "count": int(m.group(1)), "tag": m.group(2)})
            continue
        m = NOT_BOTH_TAG_RE.match("- " + body)
        if m:
            parsed.append({"kind": "not_both_tag", "e1": m.group(1), "e2": m.group(2),
                           "tag": m.group(3)})
            continue
        m = IMPLIES_RE.match("- " + body)
        if m:
            parsed.append({"kind": "implies", "e1": m.group(1), "p1": m.group(2),
                           "e2": m.group(3), "p2": m.group(4)})
            continue
        unparsed.append(body)
    return parsed, unparsed


_LLM_CONSTRAINT_PROMPT = (
    'Classify this single constraint sentence into exactly one JSON object. '
    'The engineer/project names are proper nouns (e.g. "Alice", "Project X") - '
    'copy them exactly as written, never invent or alter them.\n'
    'Shapes (pick the one that matches):\n'
    '{"kind":"forbidden","engineer":"<name>","project":"<name>"}\n'
    '{"kind":"exact_tag","count":<int>,"tag":"<tag>"}\n'
    '{"kind":"not_both_tag","e1":"<name>","e2":"<name>","tag":"<tag>"}\n'
    '{"kind":"implies","e1":"<name>","p1":"<name>","e2":"<name>","p2":"<name>"}\n\n'
    'Sentence: {line}\nRespond with ONLY the JSON object.'
)


def _llm_parse_constraint(line: str, model: str = "llama3.2:1b") -> dict | None:
    """Minimal LLM fallback: semantic classification of ONE constraint
    sentence into a known shape. Never invents entity names (the model is
    told to copy them, not compute anything) - this is association, not
    deterministic reasoning, per the frozen contract."""
    try:
        payload = json.dumps({
            "model": model, "prompt": _LLM_CONSTRAINT_PROMPT.format(line=line),
            "stream": False, "format": "json",
            "options": {"temperature": 0.0, "num_predict": 150},
        }).encode()
        req = urllib.request.Request(OLLAMA_URL, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            out = json.loads(resp.read())
        parsed = json.loads(out.get("response", "") or "{}")
        if isinstance(parsed, dict) and parsed.get("kind") in (
                "forbidden", "exact_tag", "not_both_tag", "implies"):
            return parsed
    except Exception:
        pass
    return None


class CSPFormalizer:
    """Formalizer protocol. Parser-first; explicit LLM fallback ONLY for
    individual constraint lines the deterministic templates don't match -
    never for engineers/projects, which are pure entity listing with no
    "association" role for the LLM to play. Engineers is a fixed 5-name
    list and projects always render as `- Project X (tag)`; if those are
    missing it is a genuine formalization failure to report, not a
    semantic-interpretation task to hand to the LLM."""

    def __init__(self, model: str = "llama3.2:1b"):
        self.model = model

    def formalize(self, state) -> dict:
        text = state.problem_text
        engineers = parse_engineers(text)
        tags = parse_projects(text)
        constraints, unparsed = parse_constraints(text)

        llm_calls = 0
        recovered = []
        if unparsed and engineers and tags:
            for line in unparsed:
                c = _llm_parse_constraint(line, model=self.model)
                llm_calls += 1
                if c is not None:
                    recovered.append(c)
        constraints = constraints + recovered
        still_unparsed = len(unparsed) - len(recovered)

        complete = bool(engineers) and bool(tags) and bool(constraints) and still_unparsed == 0
        source = "parser" if not unparsed else ("llm_fallback" if not still_unparsed else "unparsed")
        if complete:
            return {"kind": "csp",
                    "spec": {"engineers": engineers, "projects": list(tags),
                             "project_tags": tags, "constraints": constraints},
                    "formalizer_tokens": llm_calls * 30, "source": source,
                    "unparsed_constraint_lines": 0}

        return {"kind": "csp", "spec": None, "formalizer_tokens": llm_calls * 30,
                "source": "unparsed", "unparsed_constraint_lines": still_unparsed,
                "missing_engineers": engineers is None, "missing_projects": tags is None}
