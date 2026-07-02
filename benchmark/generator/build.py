"""Dataset builder CLI.

    python -m benchmark.generator.build --per-category 40 --out benchmark/datasets/v0

Each base instance yields a clean and a messy variant sharing one ground
truth; the dev/holdout split is a deterministic hash of the base_id.
"""

from __future__ import annotations

import argparse
import collections
import json
import os

from ..schema import write_jsonl
from . import calculus, csp, lp


def build(per_category: int, unsat_fraction: float, start_seed: int) -> list[dict]:
    problems: list[dict] = []
    for i in range(per_category):
        problems += lp.generate(start_seed + i)
        problems += calculus.generate(start_seed + i)
    n_unsat = round(per_category * unsat_fraction)
    for i in range(per_category):
        problems += csp.generate(start_seed + i,
                                 force_unsat=(i >= per_category - n_unsat))
    return problems


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate the EulerMind benchmark dataset.")
    ap.add_argument("--per-category", type=int, default=40,
                    help="base instances per category (each yields clean+messy)")
    ap.add_argument("--unsat-fraction", type=float, default=0.15,
                    help="fraction of CSP instances made unsatisfiable")
    ap.add_argument("--start-seed", type=int, default=0)
    ap.add_argument("--out", default="benchmark/datasets/v0")
    args = ap.parse_args()

    problems = build(args.per_category, args.unsat_fraction, args.start_seed)
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, "problems.jsonl")
    write_jsonl(path, problems)

    counts = collections.Counter((p["category"], p["split"]) for p in problems)
    manifest = {
        "n_problems": len(problems),
        "per_category_bases": args.per_category,
        "unsat_fraction": args.unsat_fraction,
        "start_seed": args.start_seed,
        "counts": {f"{cat}/{split}": n for (cat, split), n in sorted(counts.items())},
    }
    with open(os.path.join(args.out, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)

    print(f"wrote {len(problems)} problems -> {path}")
    for key, n in sorted(manifest["counts"].items()):
        print(f"  {key}: {n}")


if __name__ == "__main__":
    main()
