"""Sigma-1 Tutor Lane — lightweight answer verification.

The thesis, pointed at students: VERIFICATION IS CHEAPER THAN GENERATION.
We cannot deterministically solve "differentiate x^2 sin x", but we can
numerically check the model's claimed derivative at sample points in a
millisecond. Every checker here validates a MODEL-PRODUCED answer against
the QUESTION itself - substitution, numeric comparison, recomputation.

Closed question-shape families, fail-closed: anything that doesn't match
a known shape, or any parse/eval failure, returns checked=False and the
answer stays HEURISTIC. A check that runs and FAILS is reported loudly -
for a student, "this answer did not survive substitution" is the single
most valuable thing software can say.

Labels are assigned by THIS code, never by the model (see
competition/PROMPT_STRATEGY.md - the model self-reporting "Verified" is
the banned fabricated-certainty pattern).

Stdlib only. No sympy, no eval() - a whitelisted AST evaluator.
"""

from __future__ import annotations

import ast
import math
import re

TOL = 1e-4


class CheckError(Exception):
    pass


# ---------------------------------------------------------------- safe eval

_FUNCS = {"sin": math.sin, "cos": math.cos, "tan": math.tan,
          "sqrt": math.sqrt, "log": math.log10, "ln": math.log,
          "exp": math.exp, "abs": abs}
_CONSTS = {"pi": math.pi, "e": math.e}

_NORMALIZE = [("\\", ""), ("×", "*"), ("·", "*"), ("−", "-"), ("²", "^2"),
              ("³", "^3"), ("^", "**"), ("√", "sqrt")]

_TOKEN = re.compile(r'\d+\.?\d*|[A-Za-z]+|\*\*|[+\-*/(),]')


def _tokenize(expr: str) -> list[str]:
    out, pos = [], 0
    for m in _TOKEN.finditer(expr):
        if expr[pos:m.start()].strip():
            raise CheckError(f"unrecognized text {expr[pos:m.start()]!r}")
        out.append(m.group())
        pos = m.end()
    if expr[pos:].strip():
        raise CheckError(f"unrecognized trailing text {expr[pos:]!r}")
    return out


def _split_var_products(toks: list[str], variables: tuple[str, ...]) -> list[str]:
    """'ax' -> 'a*x', but ONLY when every letter is a known variable —
    anything else stays a single unknown symbol and fails closed."""
    out: list[str] = []
    for t in toks:
        if (t.isalpha() and len(t) > 1 and t not in _FUNCS and t not in _CONSTS
                and t not in variables and all(c in variables for c in t)):
            for j, c in enumerate(t):
                if j:
                    out.append("*")
                out.append(c)
        else:
            out.append(t)
    return out


def _to_python(expr: str, variables: tuple[str, ...]) -> str:
    """Normalize and insert implicit multiplication: 2x -> 2*x,
    x sin(x) -> x*sin(x), (x+1)(x-1) -> (x+1)*(x-1), sin x -> sin(x)."""
    for a, b in _NORMALIZE:
        expr = expr.replace(a, b)
    toks = _split_var_products(_tokenize(expr), variables)
    out: list[str] = []
    for i, t in enumerate(toks):
        if out:
            prev = out[-1]
            prev_atom = (re.fullmatch(r'\d+\.?\d*', prev) or prev == ")"
                         or prev in variables or prev in _CONSTS)
            cur_atom = (re.fullmatch(r'\d+\.?\d*', t) or t == "("
                        or t in variables or t in _CONSTS or t in _FUNCS)
            if prev_atom and cur_atom:
                out.append("*")
        if t in _FUNCS and i + 1 < len(toks) and toks[i + 1] != "(":
            # bare-argument function: sin x -> sin(x); argument = next atom
            out.append(t)
            continue
        out.append(t)
    # wrap bare-argument functions: f x -> f(x) for single following atom
    s = " ".join(out)
    for f in _FUNCS:
        s = re.sub(rf'\b{f}\b\s+(\d+\.?\d*\*?[a-z]?|\w+)(?!\()', rf'{f}(\1)', s)
    return s


_ALLOWED_NODES = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Call, ast.Name,
                  ast.Constant, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
                  ast.USub, ast.UAdd, ast.Load)


def safe_eval(expr: str, **vars: float) -> float:
    """Evaluate a math expression with whitelisted AST nodes only."""
    py = _to_python(expr, tuple(vars))
    try:
        tree = ast.parse(py, mode="eval")
    except SyntaxError as e:
        raise CheckError(f"cannot parse {expr!r}: {e}") from None
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise CheckError(f"disallowed construct {type(node).__name__}")
        if isinstance(node, ast.Call):
            if not (isinstance(node.func, ast.Name) and node.func.id in _FUNCS):
                raise CheckError("disallowed function call")
        if isinstance(node, ast.Name) and node.id not in _FUNCS \
                and node.id not in _CONSTS and node.id not in vars:
            raise CheckError(f"unknown symbol {node.id!r}")
    env = {**_FUNCS, **_CONSTS, **vars, "__builtins__": {}}
    try:
        return float(eval(compile(tree, "<check>", "eval"), env))  # noqa: S307 - AST whitelisted above
    except (ValueError, ZeroDivisionError, OverflowError) as e:
        raise CheckError(f"evaluation failed: {e}") from None


# ---------------------------------------------------------- answer parsing

# (?![A-Za-z]) keeps prose like "the final answerS are:" from matching as the
# marker and shearing the real answer in half (observed live, Sprint 2).
# '(?:is|was)?' consumes prose filler in "the final answer is: \boxed{…}" so
# the first kept line is the answer, not the word "is" (observed live, Σ4-1).
_FINAL_RE = re.compile(
    r'(?:\*\*)?FINAL ANSWER(?![A-Za-z])(?:\s+(?:is|was))?\s*:?\s*(?:\*\*)?\s*',
    re.IGNORECASE)
_NUM = r'-?\d+(?:\.\d+)?(?:\s*/\s*-?\d+(?:\.\d+)?)?'


def _delatex(s: str) -> str:
    """Math models answer in LaTeX; normalize the common forms to plain
    math before extraction. Anything this misses still fails closed."""
    # unwrap \boxed{...} first (keeps content, tolerates one nesting level) —
    # a marker-path tail like 'final answer is: \[ \boxed{-\frac{1}{2}, -3} \]'
    # otherwise leaves an uneatable '\boxed(' shard in the extracted answer
    s = re.sub(r'\\boxed\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', r'\1', s)
    for _ in range(3):  # nested \frac
        s = re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'((\1)/(\2))', s)
    s = re.sub(r'\\(?:quad|qquad|,|;|!)', ' ', s)
    s = s.replace(r'\cdot', '*').replace(r'\times', '*')
    s = re.sub(r'\\(?:left|right|text\{[^}]*\}|mathrm\{[^}]*\})', '', s)
    s = re.sub(r'\\[\[\]()]', ' ', s)          # \[ \] \( \)
    s = re.sub(r'\\sqrt\{([^{}]+)\}', r'sqrt(\1)', s)
    s = s.replace("$", " ").replace("**", "").replace("{", "(").replace("}", ")")
    return s


def final_answer_line(model_text: str) -> str | None:
    """Text after the last FINAL ANSWER marker (the answer may sit on the
    same line or the following lines, e.g. inside a LaTeX display block)."""
    matches = list(_FINAL_RE.finditer(model_text))
    if not matches:
        # Math models' native convention: the last \boxed{...} is the answer.
        boxed = re.findall(r'\\boxed\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', model_text)
        if boxed:
            return _delatex(boxed[-1]).strip().rstrip(".")
        return None
    tail = _delatex(model_text[matches[-1].end():])
    kept: list[str] = []
    for ln in tail.splitlines():
        ln = ln.strip()
        if not ln:
            if kept:
                break       # blank line after content ends the answer block
            continue        # skip leading blanks/normalized-away markup
        kept.append(ln)
        if len(kept) >= 4:
            break
    if not kept:
        return None
    return " ".join(kept).strip().rstrip(".")


def _parse_number(s: str) -> float:
    s = s.strip().replace("−", "-")
    m = re.fullmatch(r'(-?\d+(?:\.\d+)?)\s*/\s*(-?\d+(?:\.\d+)?)', s)
    if m:
        return float(m.group(1)) / float(m.group(2))
    return float(s)


def _extract_values(answer: str, var: str) -> list[float]:
    """Values assigned to `var` ('x = -1/2 or x = -3', 'x = -1/2, -3',
    'x = -((1)/(2))'). 'or'/'and' are normalised to list separators so BOTH
    roots of a quadratic are captured, not just the first. Each value is
    evaluated with the safe evaluator, so fractions, parentheses and sqrt()
    all work. Adding more roots can only make a check stricter (every root
    must substitute correctly), so it never introduces a false verification."""
    answer = re.sub(r'\b(?:or|and)\b', ',', answer, flags=re.IGNORECASE)
    vals: list[float] = []

    def _add(tok: str) -> None:
        tok = tok.strip().rstrip(".")
        if not tok:
            return
        try:
            v = _parse_number(tok)
        except ValueError:
            try:
                v = safe_eval(tok)
            except CheckError:
                return
        if all(abs(v - u) > TOL for u in vals):   # dedupe repeated roots
            vals.append(v)

    # Primary: each "var = <expr>" occurrence (lookahead stops at the next
    # variable, so space-separated 'x = 2 y = 3' still splits correctly).
    for v in re.findall(rf'{var}\s*=\s*([^,;=\n]+?)(?=\s*(?:,|;|$|\b[a-wyz]\s*=))',
                        answer):
        _add(v)
    # Additive: bare numeric roots in a "var = a, b" list (the second root
    # written without repeating the variable). Numeric-only, so it cannot
    # swallow another variable's assignment.
    m = re.search(rf'{var}\s*=\s*(.+)$', answer)
    if m:
        for seg in re.split(r'[,;]', m.group(1)):
            seg = seg.strip()
            if seg and re.fullmatch(r'[-+0-9/.()\s]*', seg) and re.search(r'\d', seg):
                _add(seg)
    # Fallback: no '=' at all (math models answer '\\boxed{-1/2, -3}', which
    # _delatex renders as '-((1)/(2)), -3'). Split on list separators and
    # evaluate each segment whole — segment-wise safe_eval keeps parenthesised
    # fractions intact where a bare-number regex would shred them into wrong
    # roots (the x=1 misfire this replaces).
    if not vals and var == "x" and "=" not in answer:
        for seg in re.split(r'[,;]|\band\b|\bor\b', answer):
            _add(seg)
        if not vals:
            for tok in re.findall(rf'(?<![\d/.]){_NUM}', answer):
                _add(tok)
    return vals


# ------------------------------------------------------- question checkers

def _check_solve_equation(question: str, answer: str) -> dict | None:
    m = re.search(r'[Ss]olve\s*:?\s*(.+?)\s*=\s*([^=,;]+?)\s*(?:$|[.,;?]|\bfor\b)',
                  question.replace("\n", " "))
    if not m:
        return None
    lhs, rhs = m.group(1), m.group(2)
    if "y" in lhs + rhs:
        return None  # simultaneous handled separately
    roots = _extract_values(answer, "x")
    if not roots:
        raise CheckError("no roots found in final answer")
    for r in roots:
        residual = safe_eval(lhs, x=r) - safe_eval(rhs, x=r)
        if abs(residual) > TOL * (1 + abs(safe_eval(lhs, x=r))):
            return {"checked": True, "passed": False,
                    "method": "root substitution",
                    "note": f"x={r:g} does not satisfy the equation "
                            f"(residual {residual:.4g})"}
    return {"checked": True, "passed": True, "method": "root substitution",
            "note": f"all {len(roots)} given root(s) substitute correctly "
                    "(completeness not verified)"}


def _pair_values(answer: str) -> tuple[float, float] | None:
    """Parse a bare ordered pair like '(22/5, 7/5)' or '((22)/(5), (7)/(5))'
    into two floats, honouring nested parentheses. None if not that shape."""
    s = answer.strip()
    while s.startswith("(") and s.endswith(")"):
        depth = 0
        wraps = True
        for i, ch in enumerate(s):
            depth += ch == "("
            depth -= ch == ")"
            if depth == 0 and i < len(s) - 1:
                wraps = False
                break
        if not wraps:
            break
        s = s[1:-1].strip()
    parts, depth, cur = [], 0, ""
    for ch in s:
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) != 2:
        return None
    try:
        return safe_eval(parts[0]), safe_eval(parts[1])
    except CheckError:
        return None


def _check_simultaneous(question: str, answer: str) -> dict | None:
    # Sides restricted to equation-term characters (no prose letters), so
    # "solve the simultaneous equations 2x + 3y = 12 and x - y = 1" yields
    # exactly the two equations, not the surrounding words.
    eqs = re.findall(r'([0-9xy+\-*/^.() ]*[xy][0-9xy+\-*/^.() ]*)'
                     r'=\s*(-?[0-9xy+\-*/^.() ]+)', question)
    eqs = [(l.strip(), r.strip().rstrip(".")) for l, r in eqs
           if l.strip() and r.strip().rstrip(".")]
    if len(eqs) < 2 or "y" not in question:
        return None
    xs = _extract_values(answer, "x")
    ys = _extract_values(answer, "y")
    if xs and ys:
        x, y = xs[0], ys[0]
    else:
        # bare ordered pair '(22/5, 7/5)' — x first, y second by convention;
        # substitution into both equations still decides correctness
        pair = _pair_values(answer)
        if pair is None:
            raise CheckError("could not extract x and y from final answer")
        x, y = pair
    for l, r in eqs[:2]:
        residual = safe_eval(l, x=x, y=y) - safe_eval(r, x=x, y=y)
        if abs(residual) > TOL * (1 + abs(safe_eval(r, x=x, y=y))):
            return {"checked": True, "passed": False,
                    "method": "substitution into both equations",
                    "note": f"(x={x:g}, y={y:g}) fails {l} = {r} "
                            f"(residual {residual:.4g})"}
    return {"checked": True, "passed": True,
            "method": "substitution into both equations",
            "note": f"(x={x:g}, y={y:g}) satisfies both equations"}


def _check_derivative(question: str, answer: str) -> dict | None:
    m = re.search(r'(?:[Dd]ifferentiate|derivative of)\s*:?\s*(?:y\s*=\s*|f\(x\)\s*=\s*)?'
                  r'([^.,;?]+?)\s*(?:with respect to x)?\s*(?:$|[.,;?])', question)
    if not m:
        return None
    f_expr = m.group(1)
    g_expr = re.sub(r"^(?:dy/dx|f'\(x\)|y')\s*=\s*", "", answer).strip()
    pts, ok_pts = [0.3, 0.7, 1.1, 1.7, 2.3], 0
    h = 1e-5
    for t in pts:
        try:
            numeric = (safe_eval(f_expr, x=t + h) - safe_eval(f_expr, x=t - h)) / (2 * h)
            claimed = safe_eval(g_expr, x=t)
        except CheckError:
            continue
        if abs(claimed - numeric) > 1e-3 * (1 + abs(numeric)):
            return {"checked": True, "passed": False,
                    "method": "numeric derivative comparison",
                    "note": f"claimed derivative disagrees with numeric "
                            f"derivative at x={t} ({claimed:.5g} vs {numeric:.5g})"}
        ok_pts += 1
    if ok_pts < 3:
        raise CheckError("too few evaluable sample points")
    return {"checked": True, "passed": True,
            "method": "numeric derivative comparison",
            "note": f"claimed derivative matches numeric differentiation "
                    f"at {ok_pts} sample points"}


def _check_find_constants(question: str, answer: str,
                          full_text: str = "") -> dict | None:
    """WAEC classic: 'the roots of 2x^2 + (p+1)x + q = 0 are 1 and 3 — find
    p and q.' Deterministic check: substitute the model's constants back into
    the equation and confirm EVERY given root still satisfies it. Wrong
    constants cannot balance the equation at the given roots, so this cannot
    certify a wrong answer; values are read from the final answer first, then
    from the last 'p = …' in the working (substitution, not location, decides
    correctness)."""
    m = re.search(r'roots?\s+of\s+(?:the\s+)?(?:equation\s+)?(.+?)\s*=\s*0\s+'
                  r'(?:are|is)\s+(.+?)(?=,|\.|;|\?|$)', question, re.IGNORECASE)
    if not m:
        return None
    lhs, roots_str = m.group(1).strip(), m.group(2)
    letters = set(re.findall(r'[a-wyz]',
                             re.sub(r'sin|cos|tan|sqrt|log|ln|exp|pi', '', lhs)))
    if not letters or 'x' not in lhs:
        return None
    roots = [_parse_number(t) for t in re.findall(_NUM, roots_str)]
    if not roots:
        return None
    consts: dict[str, float] = {}
    for u in sorted(letters):
        vals = _extract_values(answer, u) if answer else []
        if not vals:
            found = re.findall(rf'\b{u}\s*=\s*({_NUM})', full_text)
            if found:
                vals = [_parse_number(found[-1])]
        if not vals:
            raise CheckError(f"no value for constant {u!r} in the answer")
        consts[u] = vals[-1]
    for r in roots:
        residual = safe_eval(lhs, x=r, **consts)
        if abs(residual) > TOL * (1 + abs(r)):
            pretty = ", ".join(f"{u}={v:g}" for u, v in consts.items())
            return {"checked": True, "passed": False,
                    "method": "constant substitution",
                    "note": f"with {pretty}, x={r:g} is no longer a root "
                            f"(residual {residual:.4g})"}
    pretty = ", ".join(f"{u}={v:g}" for u, v in consts.items())
    roots_pretty = ", ".join(f"x={r:g}" for r in roots)
    return {"checked": True, "passed": True, "method": "constant substitution",
            "note": f"{pretty} reproduce every given root ({roots_pretty})"}


def _check_percentage(question: str, answer: str) -> dict | None:
    """Percentage recomputation: '% of', 'increase/decrease N by p%', and
    percentage profit/loss from cost & selling price. Fail-closed guards:
    multi-'%' questions are refused (multi-step chains can't be re-derived
    from one pattern), and a value that matches only under a /100 or x100
    unit reading raises CheckError instead of loud-failing a possibly
    correct answer."""
    q = question.replace(",", "")
    if q.count("%") > 1:
        return None
    expected, desc = None, None
    m = re.search(r'(-?\d+(?:\.\d+)?)\s*%\s+of\s+(-?\d+(?:\.\d+)?)', q)
    if m:
        expected = float(m.group(1)) / 100.0 * float(m.group(2))
        desc = f"{m.group(1)}% of {m.group(2)}"
    if expected is None:
        m = re.search(r'\b(increase|decrease)\s+(-?\d+(?:\.\d+)?)\s+by\s+'
                      r'(\d+(?:\.\d+)?)\s*%', q, re.IGNORECASE)
        if m:
            a, p = float(m.group(2)), float(m.group(3))
            sign = 1 if m.group(1).lower() == "increase" else -1
            expected = a * (1 + sign * p / 100.0)
            desc = f"{m.group(2)} {m.group(1).lower()}d by {m.group(3)}%"
    if expected is None:
        kind = re.search(r'percentage\s+(profit|gain|loss)', q, re.IGNORECASE)
        if kind:
            buy = re.search(r'\b(?:buys?|bought|cost(?:s)?)\b[^0-9]*'
                            r'(\d+(?:\.\d+)?)', q, re.IGNORECASE)
            sell = re.search(r'\b(?:sells?|sold|selling\s+price)\b[^0-9]*'
                             r'(\d+(?:\.\d+)?)', q, re.IGNORECASE)
            if not buy or not sell:
                return None
            c, s = float(buy.group(1)), float(sell.group(1))
            if c == 0:
                return None
            k = kind.group(1).lower()
            expected = (s - c) / c * 100 if k in ("profit", "gain") else (c - s) / c * 100
            desc = f"percentage {k} (cost {c:g}, selling {s:g})"
    if expected is None:
        return None
    nums = re.findall(_NUM, answer.replace(",", ""))
    if not nums:
        raise CheckError("no numeric value in final answer")
    got = _parse_number(nums[-1])
    tol = TOL * (1 + abs(expected))
    if abs(got - expected) <= tol:
        return {"checked": True, "passed": True,
                "method": "percentage recomputation",
                "note": f"recomputed {desc} independently: {expected:g}"}
    if abs(got * 100 - expected) <= tol or abs(got / 100 - expected) <= tol:
        raise CheckError("answer units ambiguous (percent vs fraction)")
    return {"checked": True, "passed": False,
            "method": "percentage recomputation",
            "note": f"recomputed {desc} = {expected:g}, but the answer says {got:g}"}


def _check_subject_of_formula(question: str, answer: str) -> dict | None:
    """'Make x the subject of v = u + ax.' Roundtrip check: pick fixed
    sample values for the target and the other variables, compute the
    formula's lone-variable side, then feed everything into the model's
    rearranged expression — it must return the original target value at
    every sample point. A wrong rearrangement cannot survive this."""
    m = re.search(r'[Mm]ake\s+([a-zA-Z])\s+the\s+subject\s*(?:of\s+(?:the\s+)?'
                  r'formula)?\s*:?\s+(.+?)\s*(?:$|[.?])', question)
    if not m:
        return None
    target, formula = m.group(1), m.group(2)
    if "=" not in formula:
        return None
    lhs, rhs = (s.strip() for s in formula.split("=", 1))
    # [a-zA-Z] here, unlike the x-excluding classes elsewhere: the subject
    # target is routinely x itself, and formulas use uppercase vars (A, V, T)
    letters = set(re.findall(
        r'[a-zA-Z]', re.sub(r'sin|cos|tan|sqrt|log|ln|exp|pi', '', formula)))
    if target not in letters:
        return None
    # one side must be a lone variable (the formula's output), not the target
    if lhs in letters and lhs != target:
        out_var, expr_side = lhs, rhs
    elif rhs in letters and rhs != target:
        out_var, expr_side = rhs, lhs
    else:
        return None
    am = re.match(rf'\s*{target}\s*=\s*(.+)$', answer)
    if not am:
        raise CheckError(f"final answer is not of the form {target} = …")
    rearranged = am.group(1).strip()
    others = sorted(letters - {target, out_var})
    ok = 0
    for t_val in (0.6, 1.7, 2.9):
        env = {v: 1.3 + 0.7 * i for i, v in enumerate(others)}
        env[target] = t_val
        try:
            out_val = safe_eval(expr_side, **env)
            env2 = {v: env[v] for v in others}
            env2[out_var] = out_val
            claimed = safe_eval(rearranged, **env2)
        except CheckError:
            continue
        if abs(claimed - t_val) > TOL * (1 + abs(t_val)):
            return {"checked": True, "passed": False,
                    "method": "formula roundtrip",
                    "note": f"rearrangement gives {target}={claimed:.5g} where "
                            f"the original formula used {target}={t_val:g}"}
        ok += 1
    if ok < 2:
        raise CheckError("too few evaluable sample points")
    return {"checked": True, "passed": True, "method": "formula roundtrip",
            "note": f"rearrangement returns the original {target} at {ok} "
                    "independent sample points"}


def _check_coordinate_geometry(question: str, answer: str) -> dict | None:
    """Gradient / midpoint / equation of the line through two given points —
    all recomputed or substitution-checked from the coordinates in the
    question. Exactly two points required; anything else fails closed."""
    pts = re.findall(r'\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)',
                     question)
    if len(pts) != 2:
        return None
    (x1, y1), (x2, y2) = ((float(a), float(b)) for a, b in pts)
    ql = question.lower()
    if "gradient" in ql or "slope" in ql:
        if x2 == x1:
            return None    # vertical line: no numeric gradient to compare
        expected = (y2 - y1) / (x2 - x1)
        nums = re.findall(_NUM, answer)
        if not nums:
            raise CheckError("no numeric value in final answer")
        got = _parse_number(nums[-1])
        if abs(got - expected) > TOL * (1 + abs(expected)):
            return {"checked": True, "passed": False,
                    "method": "gradient recomputation",
                    "note": f"gradient from the given points is {expected:g}, "
                            f"the answer says {got:g}"}
        return {"checked": True, "passed": True,
                "method": "gradient recomputation",
                "note": f"recomputed from the two points: {expected:g}"}
    if "midpoint" in ql:
        pair = _pair_values(answer)
        if pair is None:
            raise CheckError("no coordinate pair in final answer")
        ex, ey = (x1 + x2) / 2, (y1 + y2) / 2
        if abs(pair[0] - ex) > TOL * (1 + abs(ex)) or \
           abs(pair[1] - ey) > TOL * (1 + abs(ey)):
            return {"checked": True, "passed": False,
                    "method": "midpoint recomputation",
                    "note": f"midpoint of the given points is ({ex:g}, {ey:g}), "
                            f"the answer says ({pair[0]:g}, {pair[1]:g})"}
        return {"checked": True, "passed": True,
                "method": "midpoint recomputation",
                "note": f"recomputed from the two points: ({ex:g}, {ey:g})"}
    if re.search(r'equation of (?:the )?(?:straight )?line', ql):
        am = re.match(r'\s*y\s*=\s*(.+)$', answer)
        if not am:
            raise CheckError("final answer is not of the form y = …")
        expr = am.group(1).strip()
        for px, py in ((x1, y1), (x2, y2)):
            claimed = safe_eval(expr, x=px)
            if abs(claimed - py) > TOL * (1 + abs(py)):
                return {"checked": True, "passed": False,
                        "method": "line through points",
                        "note": f"the given point ({px:g}, {py:g}) does not lie "
                                f"on the claimed line (y = {claimed:.5g})"}
        return {"checked": True, "passed": True, "method": "line through points",
                "note": "both given points satisfy the claimed equation"}
    return None


def _check_arithmetic(question: str, answer: str) -> dict | None:
    m = re.search(r'(?:[Ee]valuate|[Cc]ompute|[Cc]alculate)\s*:?\s*([^?]+?)\s*(?:$|[.?])',
                  question)
    if not m or re.search(r'[a-wyz]', re.sub(r'sin|cos|tan|sqrt|log|ln|exp|pi',
                                             '', m.group(1))):
        return None
    expected = safe_eval(m.group(1))
    nums = re.findall(_NUM, answer)
    if not nums:
        raise CheckError("no numeric value in final answer")
    got = _parse_number(nums[-1])
    if abs(got - expected) > TOL * (1 + abs(expected)):
        return {"checked": True, "passed": False, "method": "recomputation",
                "note": f"recomputed value {expected:g} != stated {got:g}"}
    return {"checked": True, "passed": True, "method": "recomputation",
            "note": f"recomputed independently: {expected:g}"}


def _check_expand(question: str, answer: str) -> dict | None:
    """Verify 'expand', 'factorise' and 'simplify' by numeric identity: the
    model's expression must agree with the original at several sample x
    values. Single-variable x only; fail-closed on anything else. A wrong
    expansion disagrees at the sample points, so this cannot certify a wrong
    answer (identity of bounded-degree polynomials is decided by enough
    points, and the points avoid the common roots)."""
    m = re.search(r'(?:[Ee]xpand|[Ss]implify|[Ff]actori[sz]e)\s*:?\s*'
                  r'([^.,;?=]+?)\s*(?:$|[.,;?])', question)
    if not m:
        return None
    lhs = m.group(1)
    rhs = re.sub(r"^[A-Za-z]\w*\s*=\s*", "", answer).strip()  # drop 'y =' etc.
    # single-variable x only: reject if any non-x letter survives (minus funcs)
    residue = re.sub(r'sin|cos|tan|sqrt|log|ln|exp|pi', '', lhs + " " + rhs)
    if re.search(r'[a-wyz]', residue):
        return None
    pts, ok = [0.3, 1.1, 1.7, 2.3, 3.1], 0
    for t in pts:
        try:
            want = safe_eval(lhs, x=t)
            got = safe_eval(rhs, x=t)
        except CheckError:
            continue
        if abs(got - want) > 1e-3 * (1 + abs(want)):
            return {"checked": True, "passed": False,
                    "method": "numeric identity check",
                    "note": f"result disagrees with the original at x={t} "
                            f"({got:.5g} vs {want:.5g})"}
        ok += 1
    if ok < 3:
        raise CheckError("too few evaluable sample points")
    return {"checked": True, "passed": True, "method": "numeric identity check",
            "note": f"matches the original expression at {ok} sample points"}


_CHECKERS = (_check_simultaneous, _check_find_constants,
             _check_coordinate_geometry, _check_subject_of_formula,
             _check_solve_equation, _check_derivative, _check_expand,
             _check_percentage, _check_arithmetic)


def check_answer(question: str, model_text: str) -> dict:
    """Returns {label, checked, passed, method, note}. Label semantics:
    DERIVED   - model answer, deterministic check PASSED
    HEURISTIC - model answer, not checkable (or check machinery failed)
    HEURISTIC + passed=False - check RAN and the answer FAILED it
    """
    answer = final_answer_line(model_text)
    if answer is None:
        # constants-style answers ('p = -9 ... q = 6') often live in the
        # working with no final-answer line; that family can still check.
        try:
            result = _check_find_constants(question, "", model_text)
        except CheckError:
            result = None
        if result is not None:
            label = "Derived" if result["passed"] else "Heuristic"
            return {"label": label, **result}
        return {"label": "Heuristic", "checked": False, "passed": None,
                "method": None,
                "note": "no machine-readable final answer to check"}
    for checker in _CHECKERS:
        try:
            if checker is _check_find_constants:
                result = checker(question, answer, model_text)
            else:
                result = checker(question, answer)
        except CheckError as e:
            return {"label": "Heuristic", "checked": False, "passed": None,
                    "method": checker.__name__.replace("_check_", ""),
                    "note": f"check not completable: {e}"}
        if result is not None:
            label = "Derived" if result["passed"] else "Heuristic"
            return {"label": label, **result}
    return {"label": "Heuristic", "checked": False, "passed": None,
            "method": None,
            "note": "question shape not in the checkable families"}


# Plain-English, teacher-facing rationale for a PASSED check. Written for a
# WAEC student, not an engineer. Never shown unless the deterministic check
# actually ran and passed — so it can never overstate what EulerMind did.
_TRUST_BULLETS = {
    "root substitution": [
        "Put the answer back into the original equation",
        "Both sides came out equal — nothing left over"],
    "substitution into both equations": [
        "Put the values into both equations",
        "Every equation balanced"],
    "numeric identity check": [
        "Compared the two expressions at several values of x",
        "They agreed every time — so they are genuinely the same expression"],
    "recomputation": [
        "Worked the calculation out independently",
        "Got exactly the same result"],
    "numeric derivative comparison": [
        "Measured the slope of the function directly from the graph",
        "The claimed derivative matched that slope at every test point"],
    "constant substitution": [
        "Put the found constants back into the original equation",
        "Every root the question gave still satisfies it exactly"],
    "percentage recomputation": [
        "Recomputed the percentage directly from the numbers in the question",
        "Got exactly the same value"],
    "formula roundtrip": [
        "Fed sample values through the original formula",
        "The rearranged formula returned the same values every time"],
    "gradient recomputation": [
        "Recomputed the gradient from the two given points",
        "The claimed value matches exactly"],
    "midpoint recomputation": [
        "Recomputed the midpoint from the two given points",
        "The claimed coordinates match exactly"],
    "line through points": [
        "Substituted both given points into the claimed equation",
        "Both points lie exactly on the line"],
}


def trust_rationale(result: dict) -> list[str]:
    """Plain-English bullets explaining WHY a checked answer is trusted.
    Empty unless the check ran and passed (Derived); the caller shows this
    only in that case."""
    if not (result.get("checked") and result.get("passed")):
        return []
    return _TRUST_BULLETS.get(result.get("method"), [
        "Re-checked the answer with an independent deterministic method",
        "It passed"])
