"""Problem schema and dataset split assignment.

Every problem is a plain JSONL-serializable dict. The dev/holdout split is a
deterministic hash of the base_id, so clean/messy variants of the same
underlying instance always land in the same split, and regeneration never
reshuffles the split.

Convention: solvers may read every field except `ground_truth`. The oracle
solver reads it by design (it validates the harness, not the reasoning).
"""

from __future__ import annotations

import hashlib
import json

HOLDOUT_PERCENT = 25


def split_for(base_id: str) -> str:
    digest = hashlib.sha256(base_id.encode()).hexdigest()
    return "holdout" if int(digest, 16) % 100 < HOLDOUT_PERCENT else "dev"


def make_problem(*, base_id: str, category: str, variant: str, seed,
                 text: str, ground_truth: dict, answer_spec: dict) -> dict:
    return {
        "id": f"{base_id}-{variant}",
        "base_id": base_id,
        "category": category,
        "variant": variant,           # "clean" | "messy"
        "split": split_for(base_id),  # "dev" | "holdout"
        "seed": seed,
        "text": text,
        "ground_truth": ground_truth,
        "answer_spec": answer_spec,
    }


def write_jsonl(path: str, problems: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for p in problems:
            fh.write(json.dumps(p) + "\n")


def read_jsonl(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]
