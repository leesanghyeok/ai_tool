#!/usr/bin/env python3
"""run_evals.py가 생성한 llm-judge evidence를 deterministic하게 검증한다."""
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


def _verify_primary_output_ref(evidence: dict[str, Any], errors: list[str]) -> Path | None:
    primary = evidence.get("primary_output")
    if not isinstance(primary, dict):
        errors.append("primary_output must be an object")
        return None
    primary_path_value = primary.get("path")
    primary_hash = primary.get("sha256")
    if not isinstance(primary_path_value, str) or not primary_path_value:
        errors.append("primary_output.path is required")
        return None
    primary_path = Path(primary_path_value)
    if not primary_path.exists():
        errors.append(f"primary output missing: {primary_path}")
        return None
    if not isinstance(primary_hash, str) or primary_hash != _sha256(primary_path):
        errors.append("primary_output.sha256 does not match file")
    return primary_path


def _verify_primary_output_content(primary_path: Path, errors: list[str]) -> None:
    try:
        primary_json = _load_json(primary_path)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"primary output JSON invalid: {exc}")
        return
    if primary_json.get("schema_version") != SCHEMA_VERSION:
        errors.append("primary output schema_version must be 1")
    if primary_json.get("status") != "success":
        errors.append("primary output status must be success")
    output = primary_json.get("output")
    files_written = primary_json.get("files_written")
    has_output_content = isinstance(output, dict) and isinstance(output.get("content"), str) and bool(output["content"].strip())
    has_pipeline_files = isinstance(files_written, list)
    if not has_output_content and not has_pipeline_files:
        errors.append("primary output must contain either non-empty output.content or pipeline files_written list")


def _verify_setup(evidence: dict[str, Any], primary_path: Path, errors: list[str]) -> None:
    setup = evidence.get("setup")
    if setup is None:
        return
    if not isinstance(setup, dict):
        errors.append("setup must be an object")
    else:
        _verify_setup_fields(setup, primary_path, errors)
    _verify_files_written_read_back(evidence.get("files_written_read_back"), errors)


def _verify_setup_fields(setup: dict[str, Any], primary_path: Path, errors: list[str]) -> None:
    if setup.get("exit_code") != 0:
        errors.append("setup.exit_code must be 0")
    pipeline_output = setup.get("pipeline_output")
    if not isinstance(pipeline_output, str) or not pipeline_output:
        errors.append("setup.pipeline_output is required")
    elif Path(pipeline_output) != primary_path:
        errors.append("setup.pipeline_output must match primary_output.path")
    if setup.get("pipeline_output_status") != "success":
        errors.append("setup.pipeline_output_status must be success")


def _verify_files_written_read_back(read_back: Any, errors: list[str]) -> None:
    if not isinstance(read_back, list):
        errors.append("files_written_read_back must be a list when setup is present")
        return
    for index, item in enumerate(read_back):
        if not isinstance(item, dict):
            errors.append(f"files_written_read_back[{index}] must be an object")
            continue
        if not item.get("exists"):
            errors.append(f"files_written_read_back[{index}] target is missing")


def _verify_artifacts(evidence: dict[str, Any], errors: list[str]) -> None:
    artifacts = evidence.get("artifacts")
    if not isinstance(artifacts, list):
        errors.append("artifacts must be a list")
        return
    for index, artifact in enumerate(artifacts):
        _verify_artifact(index, artifact, errors)


def _verify_artifact(index: int, artifact: Any, errors: list[str]) -> None:
    if not isinstance(artifact, dict):
        errors.append(f"artifacts[{index}] must be an object")
        return
    artifact_path_value = artifact.get("path")
    if artifact.get("must_exist") and isinstance(artifact_path_value, str):
        artifact_path = Path(artifact_path_value)
        if not artifact_path.exists():
            errors.append(f"artifact missing: {artifact_path}")
        elif artifact.get("sha256") and artifact["sha256"] != _sha256(artifact_path):
            errors.append(f"artifact sha256 mismatch: {artifact_path}")


def _verify_no_secret_tokens(evidence_path: Path, errors: list[str]) -> None:
    lowered = evidence_path.read_text(encoding="utf-8").lower()
    for token in ("secret=", "token=", "password="):
        if token in lowered:
            errors.append(f"secret-like token leaked: {token}")


def verify(evidence_path: Path) -> list[str]:
    errors: list[str] = []
    evidence = _load_json(evidence_path)
    if evidence.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version must be 1")
    primary_path = _verify_primary_output_ref(evidence, errors)
    if primary_path is not None:
        _verify_primary_output_content(primary_path, errors)
        _verify_setup(evidence, primary_path, errors)
    _verify_artifacts(evidence, errors)
    _verify_no_secret_tokens(evidence_path, errors)
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
