#!/usr/bin/env python3
"""Validate rubric-design-v2 scorecard JSON.

Supports two families:
  1. skill-quality certification scorecard with D1-D8, hard_gates, certification_score.
  2. generated judge scorecard with evaluation_target and dimension_scores.

Usage:
  python3 scripts/validate-scorecard.py <scorecard.json> [minimum_score]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

JUDGING_CONTEXTS = {"clean_subagent", "parallel_clean_subagents", "same_context_exception"}
CONFIDENCE = {"low", "medium", "high"}
HARD_GATE_THRESHOLDS = {"D1": 13, "D2": 17, "D3": 13, "D4": 13, "D5": 9}
DIMENSION_MAX = {"D1": 15, "D2": 20, "D3": 15, "D4": 15, "D5": 10, "D6": 10, "D7": 8, "D8": 7}

JUDGE_REQUIRED = {
    "evaluation_target",
    "judging_context",
    "context_contamination_notes",
    "total_score",
    "max_score",
    "global_caps_applied",
    "dimension_scores",
    "critical_missing_points",
    "recommended_revisions",
    "confidence",
    "needs_human_review",
}
SKILL_QUALITY_REQUIRED = {
    "skill_path",
    "rubric_version",
    "judging_context",
    "workflow_mode",
    "minimum_certification_score",
    "raw_total_score",
    "certification_score",
    "max_score",
    "pass",
    "hard_gates",
    "global_caps_applied",
    "dimension_scores",
    "parent_verification",
    "contract_checks",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def number(value, label: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        fail(f"{label} must be numeric")
    return float(value)


def check_context(data: dict) -> None:
    if data.get("judging_context") not in JUDGING_CONTEXTS:
        fail("invalid judging_context")


def check_arrays(data: dict, keys: list[str]) -> None:
    for key in keys:
        if not isinstance(data.get(key), list):
            fail(f"{key} must be an array")


def validate_dimensions_generic(dimensions: list, total_score: float, max_score: float) -> None:
    if not isinstance(dimensions, list) or not dimensions:
        fail("dimension_scores must be a non-empty array")
    dimension_sum = 0.0
    max_sum = 0.0
    for i, dim in enumerate(dimensions):
        for key in ["score", "max_score", "checklist"]:
            if key not in dim:
                fail(f"dimension_scores[{i}] missing {key}")
        score = number(dim["score"], f"dimension_scores[{i}].score")
        dim_max = number(dim["max_score"], f"dimension_scores[{i}].max_score")
        if not 0 <= score <= dim_max:
            fail(f"dimension score out of bounds at index {i}")
        dimension_sum += score
        max_sum += dim_max
        if not isinstance(dim["checklist"], list) or not dim["checklist"]:
            fail(f"dimension_scores[{i}].checklist must be non-empty")
        for j, item in enumerate(dim["checklist"]):
            for key in ["score", "max_score"]:
                if key not in item:
                    fail(f"dimension_scores[{i}].checklist[{j}] missing {key}")
            item_score = number(item["score"], f"dimension_scores[{i}].checklist[{j}].score")
            item_max = number(item["max_score"], f"dimension_scores[{i}].checklist[{j}].max_score")
            if not 0 <= item_score <= item_max:
                fail(f"checklist score out of bounds at dimension {i} item {j}")
    if max_sum != max_score:
        fail(f"dimension max sum mismatch: {max_sum} != {max_score}")
    if dimension_sum != total_score:
        fail(f"dimension score sum mismatch: {dimension_sum} != {total_score}")


def validate_judge(data: dict, minimum_score: float) -> None:
    missing = JUDGE_REQUIRED - set(data)
    if missing:
        fail("missing required keys: " + ", ".join(sorted(missing)))
    check_context(data)
    if data.get("confidence") not in CONFIDENCE:
        fail("invalid confidence")
    if not isinstance(data.get("needs_human_review"), bool):
        fail("needs_human_review must be boolean")
    total_score = number(data["total_score"], "total_score")
    max_score = number(data["max_score"], "max_score")
    if max_score != 100 or not 0 <= total_score <= max_score:
        fail("total_score/max_score out of bounds")
    if total_score < minimum_score:
        fail(f"total_score below minimum: {total_score} < {minimum_score}")
    validate_dimensions_generic(data["dimension_scores"], total_score, max_score)
    check_arrays(data, ["global_caps_applied", "critical_missing_points", "recommended_revisions"])
    print(f"PASS: judge scorecard {data.get('evaluation_target')}")
    print(f"total_score={int(total_score) if total_score.is_integer() else total_score} max_score={int(max_score)} minimum_score={int(minimum_score) if minimum_score.is_integer() else minimum_score}")


def validate_skill_quality(data: dict, minimum_score: float) -> None:
    missing = SKILL_QUALITY_REQUIRED - set(data)
    if missing:
        fail("missing required keys: " + ", ".join(sorted(missing)))
    check_context(data)
    raw_total = number(data["raw_total_score"], "raw_total_score")
    certification = number(data["certification_score"], "certification_score")
    max_score = number(data["max_score"], "max_score")
    if max_score != 100:
        fail("max_score must be 100")
    dimensions = {item.get("dimension_id"): item for item in data["dimension_scores"]}
    if set(dimensions) != set(DIMENSION_MAX):
        fail("dimension_scores must contain D1-D8 exactly")
    dim_total = 0.0
    for did, max_value in DIMENSION_MAX.items():
        score = number(dimensions[did].get("score"), f"{did}.score")
        if not 0 <= score <= max_value:
            fail(f"score out of bounds for {did}: {score}/{max_value}")
        dim_total += score
    if dim_total != raw_total:
        fail(f"raw_total_score mismatch: dimensions={dim_total} raw_total_score={raw_total}")

    gates = {item.get("dimension_id"): item for item in data["hard_gates"]}
    for did, required in HARD_GATE_THRESHOLDS.items():
        actual = dimensions[did]["score"]
        if did not in gates:
            fail(f"missing hard gate: {did}")
        gate = gates[did]
        if gate.get("required_score") != required:
            fail(f"hard gate required_score mismatch for {did}")
        if gate.get("actual_score") != actual:
            fail(f"hard gate actual_score mismatch for {did}")
        if (actual >= required) != bool(gate.get("passed")):
            fail(f"hard gate passed flag mismatch for {did}")

    gates_pass = all(dimensions[did]["score"] >= req for did, req in HARD_GATE_THRESHOLDS.items())
    expected_pass = certification >= minimum_score and gates_pass
    if bool(data.get("pass")) != expected_pass:
        fail("pass flag does not match certification_score and hard gates")
    if certification > raw_total:
        fail("certification_score cannot exceed raw_total_score")
    if certification < minimum_score:
        fail(f"certification_score below minimum: {certification} < {minimum_score}")
    if not gates_pass:
        fail("one or more hard gates failed")
    parent = data["parent_verification"]
    for key in ["score_bounds_checked", "hard_gates_checked", "caps_checked", "schema_parse_checked"]:
        if parent.get(key) is not True:
            fail(f"parent_verification.{key} must be true")
    print(f"PASS: skill-quality scorecard {data.get('skill_path')}")
    print(f"raw_total_score={int(raw_total) if raw_total.is_integer() else raw_total} certification_score={int(certification) if certification.is_integer() else certification} minimum_score={int(minimum_score) if minimum_score.is_integer() else minimum_score}")


def main() -> None:
    if len(sys.argv) not in {2, 3}:
        fail("Usage: validate-scorecard.py <scorecard.json> [minimum_score]")
    path = Path(sys.argv[1]).resolve()
    minimum_score = float(sys.argv[2]) if len(sys.argv) == 3 else 0.0
    data = json.loads(path.read_text(encoding="utf-8"))
    if "skill_path" in data or "certification_score" in data or "hard_gates" in data:
        validate_skill_quality(data, minimum_score)
    else:
        validate_judge(data, minimum_score)


if __name__ == "__main__":
    main()
