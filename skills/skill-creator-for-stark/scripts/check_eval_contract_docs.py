#!/usr/bin/env python3
"""Verify skill-creator-for-stark case-based eval contract docs/templates."""

from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_TOKENS = [
    "evals/<skill-name>.eval.yaml",
    "evals/cases/*/case.yaml",
    "test_policy",
    "run_llm_judge.py",
    "expected_compare: auto",
]
SOURCE_FILES = [
    "references/skill-eval-authoring-rules.md",
    "templates/eval-spec.template.md",
    "SKILL.md",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    text = "\n".join(Path(path).read_text(encoding="utf-8") for path in SOURCE_FILES)
    missing = [token for token in REQUIRED_TOKENS if token not in text]
    output = Path(args.output)
    if missing:
        output.write_text("MISSING " + ",".join(missing) + "\n", encoding="utf-8")
        return 1
    output.write_text("PASS\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
