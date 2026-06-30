#!/usr/bin/env python3
"""Deterministically verify llm-judge evidence produced by run_evals.py."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("evidence must be a JSON object")
    return value


def verify(evidence_path: Path) -> list[str]:
    errors: list[str] = []
    evidence = _load_json(evidence_path)
    if evidence.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version must be 1")

    primary = evidence.get("primary_output")
    if not isinstance(primary, dict):
        errors.append("primary_output must be an object")
        return errors

    primary_path_value = primary.get("path")
    primary_hash = primary.get("sha256")
    if not isinstance(primary_path_value, str) or not primary_path_value:
        errors.append("primary_output.path is required")
        return errors
    primary_path = Path(primary_path_value)
    if not primary_path.exists():
        errors.append(f"primary output missing: {primary_path}")
        return errors
    if not isinstance(primary_hash, str) or primary_hash != _sha256(primary_path):
        errors.append("primary_output.sha256 does not match file")

    try:
        primary_json = _load_json(primary_path)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"primary output JSON invalid: {exc}")
    else:
        if primary_json.get("schema_version") != SCHEMA_VERSION:
            errors.append("primary output schema_version must be 1")
        if primary_json.get("status") != "success":
            errors.append("primary output status must be success")
        output = primary_json.get("output")
        if not isinstance(output, dict) or not isinstance(output.get("content"), str) or not output["content"].strip():
            errors.append("primary output output.content must be non-empty")

    artifacts = evidence.get("artifacts")
    if not isinstance(artifacts, list):
        errors.append("artifacts must be a list")
    else:
        for index, artifact in enumerate(artifacts):
            if not isinstance(artifact, dict):
                errors.append(f"artifacts[{index}] must be an object")
                continue
            artifact_path_value = artifact.get("path")
            if artifact.get("must_exist") and isinstance(artifact_path_value, str):
                artifact_path = Path(artifact_path_value)
                if not artifact_path.exists():
                    errors.append(f"artifact missing: {artifact_path}")
                elif artifact.get("sha256") and artifact["sha256"] != _sha256(artifact_path):
                    errors.append(f"artifact sha256 mismatch: {artifact_path}")

    text = evidence_path.read_text(encoding="utf-8")
    lowered = text.lower()
    for token in ("secret=", "token=", "password="):
        if token in lowered:
            errors.append(f"secret-like token leaked: {token}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify llm-judge deterministic evidence JSON.")
    parser.add_argument("--evidence", required=True, help="judge_evidence JSON path")
    args = parser.parse_args(argv)
    try:
        errors = verify(Path(args.evidence))
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS llm-judge evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
