#!/usr/bin/env python3
"""Validate a generated rubric Markdown artifact.

Usage:
  python3 scripts/validate-rubric-artifact.py <rubric.md>
"""
from __future__ import annotations
import re, sys, json
from pathlib import Path

REQUIRED = [
    "평가 목적", "평가 대상", "총점", "세부 채점 기준", "전역 상한", "채점 절차", "JSON"
]

def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)

def main() -> None:
    if len(sys.argv) != 2:
        fail("Usage: validate-rubric-artifact.py <rubric.md>")
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    missing = [token for token in REQUIRED if token not in text]
    if missing:
        fail("missing required rubric sections/tokens: " + ", ".join(missing))
    fences = len(re.findall(r"^```", text, flags=re.MULTILINE))
    if fences % 2:
        fail("unbalanced markdown fences")
    nums = [int(x) for x in re.findall(r"\|[^|]+\|\s*(\d+)\s*\|", text)]
    if nums and 100 not in nums and sum(nums) != 100:
        fail(f"dimension point sum is not 100: {sum(nums)}")
    json_blocks = re.findall(r"```json\n(.*?)\n```", text, flags=re.S)
    for block in json_blocks:
        stripped = block.strip()
        if stripped == "{scorecard_schema}" or re.search(r"\{[a-zA-Z0-9_]+\}", stripped):
            continue
        if "{" in stripped and "}" in stripped:
            try:
                json.loads(stripped)
            except Exception as exc:
                fail(f"invalid JSON block: {exc}")
    print(f"PASS: {path}")

if __name__ == "__main__":
    main()
