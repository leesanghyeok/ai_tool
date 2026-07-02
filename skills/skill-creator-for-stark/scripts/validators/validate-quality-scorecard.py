#!/usr/bin/env python3
"""skill-quality scorecard JSON 파일을 검증한다.

Usage:
  python3 skills/skill-creator-for-stark/scripts/validators/validate-quality-scorecard.py <scorecard.json> [minimum_score]
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
CONTRACT_CHECK_KEYS = {
    "input_contract_minimal",
    "output_contract_actionable",
    "env_contract_separated",
    "variable_table_columns_valid",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def _load_args() -> tuple[Path, int]:
    if len(sys.argv) not in {2, 3}:
        fail("Usage: validate-quality-scorecard.py <scorecard.json> [minimum_score]")
    path = Path(sys.argv[1]).resolve()
    minimum_score = int(sys.argv[2]) if len(sys.argv) == 3 else 95
    return path, minimum_score


def _require_keys(data: dict) -> None:
    required = [
        "skill_path",
        "rubric_version",
        "raw_total_score",
        "certification_score",
        "hard_gates",
        "dimension_scores",
        "contract_checks",
    ]
    for key in required:
        if key not in data:
            fail(f"scorecard missing required key: {key}")


def _validate_contract_checks(data: dict) -> None:
    contract_checks = data["contract_checks"]
    if not isinstance(contract_checks, dict):
        fail("contract_checks must be an object")
    actual_contract_keys = set(contract_checks)
    if actual_contract_keys != CONTRACT_CHECK_KEYS:
        fail(
            "contract_checks must contain exactly "
            f"{sorted(CONTRACT_CHECK_KEYS)}: {sorted(actual_contract_keys)}"
        )
    for key, value in contract_checks.items():
        if not isinstance(value, bool):
            fail(f"contract_checks.{key} must be boolean")


def _dimension_map(data: dict) -> dict:
    dimensions = {item.get("dimension_id"): item for item in data["dimension_scores"]}
    if set(dimensions) != set(DIMENSION_MAX):
        fail(f"dimension_scores must contain D1-D8 exactly: {sorted(dimensions)}")
    return dimensions


def _validate_dimension_scores(dimensions: dict) -> int | float:
    total = 0
    for dimension_id, max_score in DIMENSION_MAX.items():
        score = dimensions[dimension_id].get("score")
        if not isinstance(score, (int, float)):
            fail(f"score must be numeric for {dimension_id}")
        if score < 0 or score > max_score:
            fail(f"score out of bounds for {dimension_id}: {score}/{max_score}")
        total += score
    return total


def _validate_hard_gates(data: dict, dimensions: dict) -> None:
    hard_gates = {item.get("dimension_id"): item for item in data["hard_gates"]}
    missing_hard_gates = set(HARD_GATE_THRESHOLDS) - set(hard_gates)
    if missing_hard_gates:
        fail(f"hard_gates missing required dimensions: {sorted(missing_hard_gates)}")
    for dimension_id, required in HARD_GATE_THRESHOLDS.items():
        _validate_hard_gate(dimension_id, required, dimensions, hard_gates)


def _validate_hard_gate(dimension_id: str, required: int, dimensions: dict, hard_gates: dict) -> None:
    actual = dimensions[dimension_id]["score"]
    if actual < required:
        fail(f"hard gate failed: {dimension_id} {actual} < {required}")
    gate = hard_gates[dimension_id]
    if gate.get("actual_score") != actual:
        fail(f"hard gate actual_score mismatch for {dimension_id}")
    if gate.get("required_score") != required:
        fail(f"hard gate required_score mismatch for {dimension_id}")
    if gate.get("passed") is not True:
        fail(f"hard gate passed flag must be true for {dimension_id}")


def main() -> None:
    path, minimum_score = _load_args()
    data = json.loads(path.read_text(encoding="utf-8"))
    _require_keys(data)
    _validate_contract_checks(data)
    dimensions = _dimension_map(data)
    total = _validate_dimension_scores(dimensions)
    if total != data["raw_total_score"]:
        fail(f"raw_total_score mismatch: dimensions={total} raw_total_score={data['raw_total_score']}")
    _validate_hard_gates(data, dimensions)
    if data["certification_score"] < minimum_score:
        fail(f"certification_score below minimum: {data['certification_score']} < {minimum_score}")
    print(f"PASS: {path}")
    print(f"raw_total_score={data['raw_total_score']} certification_score={data['certification_score']} minimum_score={minimum_score}")


if __name__ == "__main__":
    main()
