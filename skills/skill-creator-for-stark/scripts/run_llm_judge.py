#!/usr/bin/env python3
"""Portable subprocess adapter for llm-judge eval assertions.

The runner passes a JSON packet with schema_version and prompt. This adapter
validates that contract and writes a non-empty natural-language judge response.
It performs no external API call, credential access, commit, publish, or
promotion. In a full Hermes runtime this file is the boundary where an isolated
subagent call can be swapped in; the portable eval path stays deterministic.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1


def _failure(output: Path, message: str) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "상태: failed\n"
        f"핵심 오류: {message}\n"
        "영향: judge_output은 생성됐지만 llm-judge assertion은 실패해야 한다.\n",
        encoding="utf-8",
    )
    return 1


def _load_packet(path: Path) -> dict[str, Any]:
    try:
        packet = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid judge input JSON: {exc}") from exc
    if not isinstance(packet, dict):
        raise ValueError("judge input must be a JSON object")
    return packet


def run(input_path: Path, output_path: Path) -> int:
    try:
        packet = _load_packet(input_path)
        if packet.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("schema_version must be 1")
        prompt = packet.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be a non-empty string")
    except Exception as exc:  # noqa: BLE001 - convert to judge failure text.
        return _failure(output_path, str(exc))

    excerpt = " ".join(prompt.strip().split())[:500]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "상태: pass\n"
        "판단: judge input JSON의 schema_version과 prompt 계약을 확인했고, "
        "portable eval 환경에서는 external LLM API나 credential 없이 deterministic smoke judge 응답을 생성했다.\n"
        "근거:\n"
        f"- prompt가 비어 있지 않음: {excerpt}\n"
        "- commit/push, external publish, --promote, credential 사용을 수행하지 않음.\n"
        "주의:\n"
        "- 이 응답은 subprocess adapter 계약 검증용 자연어 output이며, 사람 review 또는 별도 isolated subagent 품질 평가는 후속 단계에서 수행한다.\n",
        encoding="utf-8",
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a portable llm-judge subprocess adapter.")
    parser.add_argument("--input", required=True, help="judge input JSON path")
    parser.add_argument("--output", required=True, help="judge output text path")
    args = parser.parse_args(argv)
    return run(Path(args.input), Path(args.output))


if __name__ == "__main__":
    raise SystemExit(main())
