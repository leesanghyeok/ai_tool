#!/usr/bin/env python3
"""Generate a raw feedback Markdown file from a normalized incident JSON input.

This is the deterministic happy-path entrypoint used by the skill eval rollout. It
intentionally does not select incidents, judge severity, compare semantic duplicates,
or update processing ledgers. Those steps remain agent workflow because they require
judgment or approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

TASK_TYPES = {"research", "coding", "recommendation", "summarization", "planning", "automation", "review", "translation", "conversation", "skill-usage", "other"}
SEVERITIES = {"low", "medium", "high", "critical"}
SOURCE_TYPES = {"ai-dissatisfaction", "skill-dissatisfaction"}
CATEGORIES = {"requirement-miss", "evidence", "freshness", "verification", "specificity", "decision-criteria", "format", "tone", "context-misread", "overconfidence", "hallucination", "actionability", "verbosity", "insufficient-detail", "skill-workflow"}
REQUIRED_INPUT_FIELDS = [
    "source_type", "source_platform", "source_ref", "session_id", "ingested",
    "created_at", "task_type", "agent_or_model", "severity", "categories",
    "title", "situation", "dissatisfaction", "expected_behavior",
    "actual_behavior", "evidence", "candidate_agent_rule", "candidate_checklist_items",
]


def _load_input(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = [field for field in REQUIRED_INPUT_FIELDS if field not in data]
    if missing:
        raise ValueError("missing required input fields: " + ", ".join(missing))
    if data["source_type"] not in SOURCE_TYPES:
        raise ValueError(f"source_type taxonomy 위반: {data['source_type']}")
    if data["task_type"] not in TASK_TYPES:
        raise ValueError(f"task_type taxonomy 위반: {data['task_type']}")
    if data["severity"] not in SEVERITIES:
        raise ValueError(f"severity taxonomy 위반: {data['severity']}")
    categories = data["categories"]
    if not isinstance(categories, list) or not categories:
        raise ValueError("categories must be a non-empty list")
    bad_categories = [item for item in categories if item not in CATEGORIES]
    if bad_categories:
        raise ValueError("categories taxonomy 위반: " + ", ".join(bad_categories))
    checklist = data["candidate_checklist_items"]
    if not isinstance(checklist, list) or not checklist:
        raise ValueError("candidate_checklist_items must be a non-empty list")
    evidence = data["evidence"]
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("evidence must be a non-empty list")
    return data


def _as_bullets(items: list[Any]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render_body(data: dict[str, Any]) -> str:
    categories = ", ".join(data["categories"])
    return (
        f"# {data['title']}\n\n"
        "## 상황 (Situation)\n\n"
        f"{data['situation']}\n\n"
        "## 불만족한 점 (Dissatisfaction)\n\n"
        f"{data['dissatisfaction']}\n\n"
        "## 기대한 동작 (Expected Behavior)\n\n"
        f"{data['expected_behavior']}\n\n"
        "## 실제 동작 (Actual Behavior)\n\n"
        f"{data['actual_behavior']}\n\n"
        "## 근거 (Evidence)\n\n"
        f"{_as_bullets(data['evidence'])}\n\n"
        "## 실패 범주 (Failure Categories)\n\n"
        f"- categories: [{categories}]\n"
        f"- task_type: {data['task_type']}\n\n"
        "## 심각도 (Severity)\n\n"
        f"{data['severity']}\n\n"
        "## 후보 Agent 규칙 (Candidate Agent Rule)\n\n"
        f"{data['candidate_agent_rule']}\n\n"
        "## 후보 체크리스트 항목 (Candidate Checklist Items)\n\n"
        f"{_as_bullets(data['candidate_checklist_items'])}\n"
    )


def _yaml_scalar(value: Any) -> str:
    if isinstance(value, list):
        return "[" + ", ".join(str(item) for item in value) + "]"
    return json.dumps(str(value), ensure_ascii=False)


def render_document(data: dict[str, Any]) -> str:
    body = render_body(data)
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    frontmatter = {
        "type": "feedback-log",
        "source_type": data["source_type"],
        "source_platform": data["source_platform"],
        "source_ref": data["source_ref"],
        "session_id": data["session_id"],
        "ingested": data["ingested"],
        "created_at": data["created_at"],
        "task_type": data["task_type"],
        "agent_or_model": data["agent_or_model"],
        "severity": data["severity"],
        "categories": data["categories"],
        "sha256": digest,
    }
    lines = ["---"]
    for key, value in frontmatter.items():
        lines.append(f"{key}: {_yaml_scalar(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n" + body


def _validate_output(path: Path) -> int:
    validator = Path(__file__).resolve().parent / "validate-feedback-log.py"
    proc = subprocess.run([sys.executable, str(validator), "--content-only", str(path)])
    return proc.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="normalized incident JSON을 raw feedback Markdown으로 변환한다.")
    parser.add_argument("--input", required=True, help="Normalized incident JSON input path")
    parser.add_argument("--output", required=True, help="Output Markdown file path")
    parser.add_argument("--validate", action="store_true", help="작성 후 content-only validator를 실행한다.")
    args = parser.parse_args(argv)

    try:
        data = _load_input(Path(args.input))
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_document(data), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - CLI entrypoint reports concise failure
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.validate:
        return _validate_output(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
