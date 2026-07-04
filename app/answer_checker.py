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


def _to_python(expr: str, variables: tuple[str, ...]) -> str:
    """Normalize and insert implicit multiplication: 2x -> 2*x,
    x sin(x) -> x*sin(x), (x+1)(x-1) -> (x+1)*(x-1), sin x -> sin(x)."""
    for a, b in _NORMALIZE:
        expr = expr.replace(a, b)
    toks = _tokenize(expr)
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

_FINAL_RE = re.compile(r'(?:\*\*)?FINAL ANSWER\s*:?\s*(?:\*\*)?\s*', re.IGNORECASE)
_NUM = r'-?\d+(?:\.\d+)?(?:\s*/\s*-?\d+(?:\.\d+)?)?'


def _delatex(s: str) -> str:
    """Math models answer in LaTeX; normalize the common forms to plain
    math before extraction. Anything this misses still fails closed."""
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
    """Values assigned to `var` ('x = -1/2 or x = -3', 'x = -((1)/(2))').
    Each captured value is evaluated with the safe evaluator, so
    fractions, parentheses and sqrt() all work."""
    vals: list[float] = []
    for v in re.findall(rf'{var}\s*=\s*([^,;=\n]+?)(?=\s*(?:,|;|$|\b[a-wyz]\s*=))',
                        answer):
        v = v.strip()
        try:
            vals.append(_parse_number(v))
        except ValueError:
            try:
                vals.append(safe_eval(v))
            except CheckError:
                continue
    if not vals and var == "x" and "=" not in answer:
        vals = [_parse_number(v) for v in re.findall(rf'(?<![\d/.]){_NUM}', answer)]
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
    if not xs or not ys:
        raise CheckError("could not extract x and y from final answer")
    x, y = xs[0], ys[0]
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


_CHECKERS = (_check_simultaneous, _check_solve_equation,
             _check_derivative, _check_arithmetic)


def check_answer(question: str, model_text: str) -> dict:
    """Returns {label, checked, passed, method, note}. Label semantics:
    DERIVED   - model answer, deterministic check PASSED
    HEURISTIC - model answer, not checkable (or check machinery failed)
    HEURISTIC + passed=False - check RAN and the answer FAILED it
    """
    answer = final_answer_line(model_text)
    if answer is None:
        return {"label": "Heuristic", "checked": False, "passed": None,
                "method": None,
                "note": "no machine-readable final answer to check"}
    for checker in _CHECKERS:
        try:
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
