#!/usr/bin/env python3
"""Validate a skill-quality scorecard JSON file.

Usage:
  python3 skills/skill-creator-for-stark/scripts/validate-quality-scorecard.py <scorecard.json> [minimum_score]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HARD_GATE_THRESHOLDS = {
    "D1": 13,
    "D2": 17,
    "D3": 13,
    "D4": 13,
    "D5": 9,
}
DIMENSION_MAX = {
    "D1": 15,
    "D2": 20,
    "D3": 15,
    "D4": 15,
    "D5": 10,
    "D6": 10,
    "D7": 8,
    "D8": 7,
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) not in {2, 3}:
        fail("Usage: validate-quality-scorecard.py <scorecard.json> [minimum_score]")

    path = Path(sys.argv[1]).resolve()
    minimum_score = int(sys.argv[2]) if len(sys.argv) == 3 else 95
    data = json.loads(path.read_text(encoding="utf-8"))

    for key in ["skill_path", "rubric_version", "raw_total_score", "certification_score", "hard_gates", "dimension_scores"]:
        if key not in data:
            fail(f"scorecard missing required key: {key}")

    dimensions = {item.get("dimension_id"): item for item in data["dimension_scores"]}
    if set(dimensions) != set(DIMENSION_MAX):
        fail(f"dimension_scores must contain D1-D8 exactly: {sorted(dimensions)}")

    total = 0
    for dimension_id, max_score in DIMENSION_MAX.items():
        item = dimensions[dimension_id]
        score = item.get("score")
        if not isinstance(score, (int, float)):
            fail(f"score must be numeric for {dimension_id}")
        if score < 0 or score > max_score:
            fail(f"score out of bounds for {dimension_id}: {score}/{max_score}")
        total += score

    if total != data["raw_total_score"]:
        fail(f"raw_total_score mismatch: dimensions={total} raw_total_score={data['raw_total_score']}")

    hard_gates = {item.get("dimension_id"): item for item in data["hard_gates"]}
    for dimension_id, required in HARD_GATE_THRESHOLDS.items():
        actual = dimensions[dimension_id]["score"]
        if actual < required:
            fail(f"hard gate failed: {dimension_id} {actual} < {required}")
        if dimension_id in hard_gates:
            gate = hard_gates[dimension_id]
            if gate.get("actual_score") != actual:
                fail(f"hard gate actual_score mismatch for {dimension_id}")
            if gate.get("required_score") != required:
                fail(f"hard gate required_score mismatch for {dimension_id}")
            if gate.get("passed") is not True:
                fail(f"hard gate passed flag must be true for {dimension_id}")

    if data["certification_score"] < minimum_score:
        fail(f"certification_score below minimum: {data['certification_score']} < {minimum_score}")

    print(f"PASS: {path}")
    print(f"raw_total_score={data['raw_total_score']} certification_score={data['certification_score']} minimum_score={minimum_score}")


if __name__ == "__main__":
    main()
