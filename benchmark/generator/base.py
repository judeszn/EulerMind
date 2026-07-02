"""Shared helpers for procedural generators.

Messy variants stress the dominant expected failure mode — formalization —
by planting irrelevant numerical facts and unit conversions in the text while
keeping the ground truth identical to the clean variant.
"""

from __future__ import annotations

import random

DISTRACTOR_TEMPLATES = [
    "The facility cafeteria serves {n} meals every day.",
    "Last quarter, the maintenance team replaced {n} light fixtures.",
    "The night-shift supervisor has {n} years of experience.",
    "Electricity costs {n} cents per kilowatt-hour on weekdays.",
    "The delivery van holds up to {n} crates at a time.",
    "The building was constructed {n} years ago.",
    "The parking lot has space for {n} vehicles.",
    "Management reviewed {n} improvement proposals this month.",
]


def distractor_sentences(rng: random.Random, count: int) -> list[str]:
    templates = rng.sample(DISTRACTOR_TEMPLATES, count)
    return [t.format(n=rng.randint(3, 480)) for t in templates]


def insert_distractors(rng: random.Random, paragraphs: list[str], count: int) -> list[str]:
    """Insert distractor sentences as standalone paragraphs at random interior
    positions (never before the opening sentence, never after the final ask)."""
    paras = list(paragraphs)
    for sentence in distractor_sentences(rng, count):
        pos = rng.randint(1, max(1, len(paras) - 1))
        paras.insert(pos, sentence)
    return paras


def join_paragraphs(paragraphs: list[str]) -> str:
    return "\n\n".join(paragraphs)
