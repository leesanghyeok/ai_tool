#!/usr/bin/env python3
"""Rough Korean-first spot check for Markdown files.

Usage:
  python3 scripts/check-korean-first.py <path> [<path> ...]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ENGLISH_HEADING_LIMIT = 0
ENGLISH_RATIO_LIMIT = 0.35
ALLOWLIST = {
    "JSON", "YAML", "API", "CLI", "URL", "LLM", "INPUT", "OUTPUT", "ENV",
    "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8",
    "SKILL", "AGENT", "JUDGE", "SCORE", "SCORECARD", "SCHEMA", "RUBRIC",
    "CAP", "CAPS", "GATE", "HARD", "QUALITY", "CLEAN", "SUBAGENT", "SHARD",
    "PARENT", "CONTEXT", "TEMPLATE", "REFERENCE", "SCRIPT", "CHECKER",
    "PATH", "COMMAND", "KEY", "ENUM", "PROPER", "NOUN", "RUNTIME",
    "READ", "BACK", "DIFF", "STATUS", "PASS", "FAIL", "TRUE", "FALSE",
}


def strip_machine_text(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"/[^\s)]+", " ", text)
    return text


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def analyze(path: Path) -> tuple[str, int, list[str], float]:
    text = path.read_text(encoding="utf-8")
    prose = strip_machine_text(text)
    headings = re.findall(r"^#{1,6}\s+(.+)$", prose, flags=re.M)
    english_only_headings: list[str] = []
    for heading in headings:
        words = re.findall(r"[A-Za-z][A-Za-z0-9_-]*", heading)
        hangul = re.findall(r"[가-힣]", heading)
        significant_words = [w for w in words if w.upper() not in ALLOWLIST]
        if significant_words and not hangul:
            english_only_headings.append(heading)
    english_tokens = [w for w in re.findall(r"[A-Za-z][A-Za-z0-9_-]*", prose) if w.upper() not in ALLOWLIST]
    korean_tokens = re.findall(r"[가-힣]+", prose)
    ratio = len(english_tokens) / max(1, len(english_tokens) + len(korean_tokens))
    return str(path), len(headings), english_only_headings, ratio


def main() -> None:
    if len(sys.argv) < 2:
        fail("Usage: check-korean-first.py <path> [<path> ...]")
    failed = False
    for arg in sys.argv[1:]:
        path = Path(arg)
        paths = list(path.rglob("*.md")) if path.is_dir() else [path]
        for md in paths:
            path_text, heading_count, english_only_headings, english_ratio = analyze(md)
            print(
                f"CHECK: {path_text} headings={heading_count} "
                f"english_only_headings={len(english_only_headings)} "
                f"english_ratio={english_ratio:.3f}"
            )
            if english_only_headings:
                print("  english_only_headings=" + "; ".join(english_only_headings[:5]))
            if len(english_only_headings) > ENGLISH_HEADING_LIMIT or english_ratio > ENGLISH_RATIO_LIMIT:
                failed = True
    if failed:
        fail("Korean-first spot check failed")
    print("PASS: Korean-first spot check")


if __name__ == "__main__":
    main()
