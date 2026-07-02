"""Generate the 3 validation levels from the existing 60 edge_ai_deployment
dev problems. Reads benchmark/datasets/v1/problems.jsonl (read-only - never
writes there); writes level{1,2,3}.jsonl under research/I1_validation/.

    python3 -m research.I1_validation.generate
"""

from __future__ import annotations

import os

from benchmark.schema import read_jsonl, write_jsonl

from .paraphrase import make_level1, make_level2, make_level3

HERE = os.path.dirname(__file__)


def main() -> None:
    all_problems = [p for p in read_jsonl("benchmark/datasets/v1/problems.jsonl")
                    if p["category"] == "edge_ai_deployment" and p["split"] == "dev"]

    # Bug found and fixed before this ran further: clean/messy variants of
    # the same base_id share one ground_truth, and paraphrase rendering
    # depends only on ground_truth (by design - guarantees zero numeric
    # drift) - so generating from all 60 rows silently produced 30
    # duplicate-id pairs. Dedupe to one representative per base_id first;
    # 30 unique instances is the honest count, not 60.
    seen = set()
    base_problems = []
    for p in all_problems:
        if p["base_id"] not in seen:
            seen.add(p["base_id"])
            base_problems.append(p)
    assert len(base_problems) == len(seen)

    level1 = [make_level1(p, i) for i, p in enumerate(base_problems)]
    level2 = [make_level2(p, i) for i, p in enumerate(base_problems)]
    level3 = [make_level3(p, i) for i, p in enumerate(base_problems)]

    write_jsonl(os.path.join(HERE, "level1.jsonl"), level1)
    write_jsonl(os.path.join(HERE, "level2.jsonl"), level2)
    write_jsonl(os.path.join(HERE, "level3.jsonl"), level3)
    print(f"level1: {len(level1)}, level2: {len(level2)}, level3: {len(level3)}")


if __name__ == "__main__":
    main()
