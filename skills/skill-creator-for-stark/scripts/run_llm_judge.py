#!/usr/bin/env python3
"""llm-judge output/assertion eval 계약을 위한 portable subprocess adapter.

Canonical modes:
  python3 scripts/run_llm_judge.py output --input input.json --output primary-output.json
  python3 scripts/run_llm_judge.py assertion --input assertion-input.json --output assertion-output.json

Legacy migration form도 계속 지원한다:
  python3 scripts/run_llm_judge.py --input judge-packet.json --output judge-output.txt

이 adapter는 의도적으로 deterministic하며 external LLM/API 호출, credential 접근, commit, publish, promotion을 수행하지 않는다. Portable JSON 계약을 검증하고 eval runner가 확인할 수 있는 bounded smoke-judge artifact를 쓴다.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
PUBLIC_INPUT_KEYS = {"schema_version", "prompt"}
ASSERTION_INPUT_KEYS = {"schema_version", "method", "primary_output", "assertions"}
VALID_ASSERTION_METHODS = {"aggregate", "each-session", "subagent"}


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid {label} JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _failure_json(output: Path, message: str, *, mode: str, method: str | None = None,
                  primary_output: str = "") -> int:
    if mode == "output":
        payload = {
            "schema_version": SCHEMA_VERSION,
            "status": "failed",
            "output": {"format": "text", "content": "", "summary": ""},
            "artifacts": [],
            "redactions_applied": [],
            "errors": [message],
        }
    else:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "status": "failed",
            "method": method or "",
            "primary_output_ref": {"sha256": _sha256_text(primary_output) if primary_output else ""},
            "results": [],
            "errors": [message],
        }
    _write_json(output, payload)
    return 1


def _legacy_failure(output: Path, message: str) -> int:
    _write_text(
        output,
        "상태: failed\n"
        f"핵심 오류: {message}\n"
        "영향: judge_output은 생성됐지만 llm-judge assertion은 실패해야 한다.\n",
    )
    return 1


def _validate_public_prompt_packet(packet: dict[str, Any], *, label: str) -> str:
    extra = set(packet) - PUBLIC_INPUT_KEYS
    missing = PUBLIC_INPUT_KEYS - set(packet)
    if missing:
        raise ValueError(f"{label} missing required field(s): {', '.join(sorted(missing))}")
    if extra:
        raise ValueError(f"{label} allows only schema_version and prompt; unexpected field(s): {', '.join(sorted(extra))}")
    if packet.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("schema_version must be 1")
    prompt = packet.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt must be a non-empty string")
    return prompt


def _summary(text: str, limit: int = 160) -> str:
    compact = " ".join(text.strip().split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def run_output(input_path: Path, output_path: Path) -> int:
    try:
        packet = _load_json_object(input_path, "output input")
        prompt = _validate_public_prompt_packet(packet, label="output input")
    except Exception as exc:  # noqa: BLE001 - convert validation failure into contract artifact.
        return _failure_json(output_path, str(exc), mode="output")

    content = (
        "Portable llm-judge primary output\n"
        "status: deterministic-smoke\n"
        "external_calls: none\n"
        f"prompt_excerpt: {_summary(prompt, 500)}"
    )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": "success",
        "output": {
            "format": "text",
            "content": content,
            "summary": _summary(content),
        },
        "artifacts": [],
        "redactions_applied": [],
        "errors": [],
    }
    _write_json(output_path, payload)
    return 0


def _normalize_method(method: Any) -> str:
    if method not in VALID_ASSERTION_METHODS:
        raise ValueError("method must be one of aggregate, each-session, subagent")
    return "each-session" if method == "subagent" else str(method)


def _validate_assertion_input(packet: dict[str, Any]) -> tuple[str, str, list[dict[str, str]]]:
    extra = set(packet) - ASSERTION_INPUT_KEYS
    missing = ASSERTION_INPUT_KEYS - set(packet)
    if missing:
        raise ValueError(f"assertion input missing required field(s): {', '.join(sorted(missing))}")
    if extra:
        raise ValueError(f"assertion input has unexpected field(s): {', '.join(sorted(extra))}")
    if packet.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("schema_version must be 1")
    method = _normalize_method(packet.get("method"))
    primary_output = packet.get("primary_output")
    if not isinstance(primary_output, str) or not primary_output.strip():
        raise ValueError("primary_output must be a non-empty string")
    assertions_value = packet.get("assertions")
    if not isinstance(assertions_value, list) or not assertions_value:
        raise ValueError("assertions must be a non-empty array")

    assertions: list[dict[str, str]] = []
    for i, assertion in enumerate(assertions_value):
        where = f"assertions[{i}]"
        if not isinstance(assertion, dict):
            raise ValueError(f"{where} must be a JSON object")
        for field in ("id", "title", "prompt"):
            if not isinstance(assertion.get(field), str) or not assertion[field].strip():
                raise ValueError(f"{where}.{field} must be a non-empty string")
        assertions.append({"id": assertion["id"], "title": assertion["title"], "prompt": assertion["prompt"]})
    return method, primary_output, assertions


def _judge_result(assertion: dict[str, str], *, method: str, session_id: str, primary_output: str) -> dict[str, Any]:
    prompt_excerpt = _summary(assertion["prompt"], 240)
    output_excerpt = _summary(primary_output, 240)
    return {
        "assertion_id": assertion["id"],
        "status": "pass",
        "judge_output": (
            "상태: pass\n"
            f"판단: portable {method} smoke judge가 assertion prompt와 primary_output 문자열을 확인했다.\n"
            f"근거: prompt='{prompt_excerpt}' / primary_output='{output_excerpt}'\n"
            "제약: external LLM API, credential, commit/push, --promote를 사용하지 않았다."
        ),
        "session_id": session_id,
    }


def run_assertion(input_path: Path, output_path: Path) -> int:
    method = ""
    primary_output = ""
    try:
        packet = _load_json_object(input_path, "assertion input")
        method, primary_output, assertions = _validate_assertion_input(packet)
    except Exception as exc:  # noqa: BLE001 - convert validation failure into contract artifact.
        return _failure_json(output_path, str(exc), mode="assertion", method=method, primary_output=primary_output)

    if method == "aggregate":
        results = [
            _judge_result(assertion, method=method, session_id="aggregate", primary_output=primary_output)
            for assertion in assertions
        ]
    else:
        results = [
            _judge_result(assertion, method=method, session_id=f"each-session:{index}:{assertion['id']}", primary_output=primary_output)
            for index, assertion in enumerate(assertions, start=1)
        ]

    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": "success",
        "method": method,
        "primary_output_ref": {"sha256": _sha256_text(primary_output)},
        "results": results,
        "errors": [],
    }
    _write_json(output_path, payload)
    return 0


def run_legacy_alias(input_path: Path, output_path: Path) -> int:
    """B1 이전 --input/--output judge_packet -> text output 형식을 지원한다."""
    try:
        packet = _load_json_object(input_path, "judge input")
        prompt = _validate_public_prompt_packet(packet, label="judge input")
    except Exception as exc:  # noqa: BLE001 - convert to judge failure text for old runner compatibility.
        return _legacy_failure(output_path, str(exc))

    _write_text(
        output_path,
        "상태: pass\n"
        "판단: legacy assertion alias가 schema_version과 prompt 계약을 확인했고, "
        "portable eval 환경에서는 external LLM API나 credential 없이 deterministic smoke judge 응답을 생성했다.\n"
        "근거:\n"
        f"- prompt가 비어 있지 않음: {_summary(prompt, 500)}\n"
        "- commit/push, external publish, --promote, credential 사용을 수행하지 않음.\n"
        "주의:\n"
        "- canonical B1 entrypoint는 output/assertion subcommand이며, 이 경로는 migration 호환용이다.\n",
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in {"output", "assertion"}:
        mode = argv.pop(0)
        parser = argparse.ArgumentParser(description=f"Run portable llm-judge {mode} mode.")
        parser.add_argument("--input", required=True, help=f"{mode} input JSON path")
        parser.add_argument("--output", required=True, help=f"{mode} output JSON path")
        args = parser.parse_args(argv)
        if mode == "output":
            return run_output(Path(args.input), Path(args.output))
        return run_assertion(Path(args.input), Path(args.output))

    parser = argparse.ArgumentParser(description="Run a portable llm-judge adapter.")
    parser.add_argument("--input", required=True, help="legacy judge_packet JSON path")
    parser.add_argument("--output", required=True, help="legacy judge_output text path")
    args = parser.parse_args(argv)
    return run_legacy_alias(Path(args.input), Path(args.output))


if __name__ == "__main__":
    raise SystemExit(main())
