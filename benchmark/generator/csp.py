"""Generator: engineer/project assignment puzzles (category: constraint_csp).

Ground truth by exhaustive enumeration (5 engineers, 7 distinct projects:
2520 permutations — exact and instant). A configurable fraction of instances
is deliberately UNSATISFIABLE: constraints are tightened until no assignment
exists, and a minimal (irreducible) conflicting constraint set is computed by
greedy deletion. These instances are the mechanical test of epistemic
discipline — the correct answer is "no valid assignment exists", and any
solver that invents one is graded wrong (Law 1: never fabricate certainty).

Grading accepts ANY valid assignment (re-verified against the constraint
spec), not just the stored example.
"""

from __future__ import annotations

import itertools
import random

from ..schema import make_problem
from .base import insert_distractors, join_paragraphs

NAMES = ["Alice", "Ben", "Chika", "David", "Esther", "Femi",
         "Grace", "Hassan", "Ifeoma", "Jide", "Kemi", "Lola"]
TAG_PALETTE = ["AI", "cybersecurity", "web", "data", "embedded"]
N_ENGINEERS, N_PROJECTS = 5, 7


def check_assignment(constraints: list[dict], tags: dict, assignment: dict) -> bool:
    """True iff `assignment` (engineer -> project) satisfies every constraint.
    Also used by the grader to re-verify solver answers."""
    for con in constraints:
        kind = con["kind"]
        if kind == "forbidden":
            if assignment[con["engineer"]] == con["project"]:
                return False
        elif kind == "exact_tag":
            count = sum(1 for p in assignment.values() if tags[p] == con["tag"])
            if count != con["count"]:
                return False
        elif kind == "not_both_tag":
            if (tags[assignment[con["e1"]]] == con["tag"]
                    and tags[assignment[con["e2"]]] == con["tag"]):
                return False
        elif kind == "implies":
            if (assignment[con["e1"]] == con["p1"]
                    and assignment[con["e2"]] != con["p2"]):
                return False
        else:
            raise ValueError(f"unknown constraint kind: {kind}")
    return True


def _solutions(engineers, projects, tags, constraints, limit=None):
    sols = []
    for perm in itertools.permutations(projects, len(engineers)):
        assignment = dict(zip(engineers, perm))
        if check_assignment(constraints, tags, assignment):
            sols.append(assignment)
            if limit is not None and len(sols) >= limit:
                break
    return sols


def _render(con: dict) -> str:
    kind = con["kind"]
    if kind == "forbidden":
        return f"{con['engineer']} cannot be assigned {con['project']}."
    if kind == "exact_tag":
        plural = "engineer" if con["count"] == 1 else "engineers"
        return f"Exactly {con['count']} {plural} must be assigned {con['tag']} projects."
    if kind == "not_both_tag":
        return f"{con['e1']} and {con['e2']} cannot both be assigned {con['tag']} projects."
    return (f"If {con['e1']} is assigned {con['p1']}, "
            f"then {con['e2']} must be assigned {con['p2']}.")


def generate(base_seed: int, force_unsat: bool = False) -> list[dict]:
    """Returns [clean_problem, messy_problem] sharing one ground truth.
    Retries internally until a valid instance is found."""
    for attempt in range(200):
        rng = random.Random(f"csp-{base_seed}-{attempt}")
        result = _try_generate(rng, base_seed, force_unsat)
        if result is not None:
            return result
    raise RuntimeError(f"no valid CSP instance for seed {base_seed}")


def _try_generate(rng, base_seed, force_unsat):
    engineers = rng.sample(NAMES, N_ENGINEERS)
    projects = [f"Project {ch}" for ch in rng.sample("PQRSTUVWXYZ", N_PROJECTS)]
    # Guarantee the tag constraints have teeth: >= 2 AI and >= 2 cybersecurity projects.
    tag_list = ["AI", "AI", "cybersecurity", "cybersecurity"] + [
        rng.choice(TAG_PALETTE) for _ in range(N_PROJECTS - 4)]
    rng.shuffle(tag_list)
    tags = dict(zip(projects, tag_list))

    constraints = []
    for _ in range(rng.randint(2, 3)):
        constraints.append({"kind": "forbidden",
                            "engineer": rng.choice(engineers),
                            "project": rng.choice(projects)})
    constraints.append({"kind": "exact_tag", "tag": "AI",
                        "count": rng.randint(1, 2)})
    e1, e2 = rng.sample(engineers, 2)
    constraints.append({"kind": "not_both_tag", "e1": e1, "e2": e2,
                        "tag": "cybersecurity"})
    if rng.random() < 0.5:
        ea, eb = rng.sample(engineers, 2)
        constraints.append({"kind": "implies", "e1": ea,
                            "p1": rng.choice(projects), "e2": eb,
                            "p2": rng.choice(projects)})

    sols = _solutions(engineers, projects, tags, constraints)

    if force_unsat:
        # Tighten until unsatisfiable: forbidding a surviving solution's pick
        # always eliminates at least that solution, so this terminates.
        while sols:
            victim = sols[0]
            eng = rng.choice(engineers)
            constraints.append({"kind": "forbidden", "engineer": eng,
                                "project": victim[eng]})
            sols = _solutions(engineers, projects, tags, constraints)
        # Minimal (irreducible) conflict set by greedy deletion.
        core = list(constraints)
        for con in list(core):
            trial = [c for c in core if c is not con]
            if not _solutions(engineers, projects, tags, trial, limit=1):
                core = trial
        ground_truth = {
            "satisfiable": False, "solution_count": 0,
            "minimal_conflict": [_render(c) for c in core],
            "constraints_spec": constraints, "project_tags": tags,
            "engineers": engineers, "projects": projects,
        }
    else:
        if not sols:
            return None  # resample
        ground_truth = {
            "satisfiable": True, "solution_count": len(sols),
            "example": sols[0],
            "constraints_spec": constraints, "project_tags": tags,
            "engineers": engineers, "projects": projects,
        }

    answer_spec = {
        "type": "csp",
        "fields": {"satisfiable": "boolean",
                   "assignment": "dict engineer -> project (required when satisfiable)"},
    }

    project_lines = "\n".join(f"- {p} ({tags[p]})" for p in projects)
    constraint_lines = "\n".join(f"- {_render(c)}" for c in constraints)
    names_str = ", ".join(engineers[:-1]) + f" and {engineers[-1]}"
    ask = ("Produce a valid assignment of engineers to projects, or state "
           "that no valid assignment exists. If an assignment exists, also "
           "state whether more than one valid assignment exists.")

    intro = (f"Five engineers—{names_str}—must each be assigned exactly one "
             "project, and no two engineers may share a project.")
    body = [intro,
            "Available projects and their focus areas:\n" + project_lines,
            "Constraints:\n" + constraint_lines,
            ask]

    base_id = f"csp-{base_seed:05d}"
    common = dict(base_id=base_id, category="constraint_csp", seed=base_seed,
                  ground_truth=ground_truth, answer_spec=answer_spec)
    return [
        make_problem(variant="clean", text=join_paragraphs(body), **common),
        make_problem(variant="messy",
                     text=join_paragraphs(insert_distractors(rng, body, count=2)),
                     **common),
    ]
