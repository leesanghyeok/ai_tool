#!/usr/bin/env python3
"""Validate a portable skill package.

Usage:
  python3 skills/skill-creator-for-stark/scripts/validate-skill-package.py skills/<skill-name>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_KEYS = ["name", "description", "version", "author", "license"]
ALLOWED_SUPPORT_DIRS = {"references", "templates", "scripts", "assets", "history"}
REQUIRED_SECTIONS = [
    "## 입력 변수",
    "## 출력 변수",
    "## 필수 환경",
    "## Hard Gates",
    "## Fast Fail",
    "## Workflow",
    "## Commit Pitfalls",
    "## Verification Checklist",
]
DESCRIPTION_MAX_CHARS = 1024
DESCRIPTION_TARGET_WORDS = 100
SKILL_BODY_MAX_WORDS = 5000
NAME_MAX_CHARS = 64


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        fail("SKILL.md frontmatter closing marker not found")
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.startswith(" "):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data, body


def check_fence_balance(text: str, label: str) -> None:
    fence_count = len(re.findall(r"^```", text, flags=re.MULTILINE))
    if fence_count % 2 != 0:
        fail(f"Markdown code fences are not balanced: {label}")


def word_count(text: str) -> int:
    return len(re.findall(r"[\w가-힣]+", text))


def check_links(skill_dir: Path, text: str, label: str) -> None:
    for match in re.findall(r"`((?:references|templates|scripts|assets|history)/[^`]+)`", text):
        if "<" in match or ">" in match:
            continue
        candidate = skill_dir / match
        if not candidate.exists():
            fail(f"linked support file not found in {label}: {match}")


def main() -> None:
    if len(sys.argv) != 2:
        fail("Usage: validate-skill-package.py <skill-dir>")

    skill_dir = Path(sys.argv[1]).resolve()
    if not skill_dir.exists() or not skill_dir.is_dir():
        fail(f"skill directory does not exist: {skill_dir}")

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        fail(f"SKILL.md not found: {skill_md}")

    text = skill_md.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(text)

    for key in REQUIRED_KEYS:
        if key not in frontmatter or not frontmatter[key]:
            fail(f"frontmatter missing required key: {key}")

    name = frontmatter["name"]
    if name != skill_dir.name:
        fail(f"frontmatter name '{name}' does not match directory '{skill_dir.name}'")

    if len(name) > NAME_MAX_CHARS:
        fail(f"skill name exceeds {NAME_MAX_CHARS} characters")

    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        fail(f"skill name is not lowercase hyphen slug: {name}")

    description = frontmatter["description"]
    if len(description) > DESCRIPTION_MAX_CHARS:
        fail(f"description exceeds {DESCRIPTION_MAX_CHARS} characters")
    if not description.strip():
        fail("description is empty")
    desc_words = word_count(description)
    if desc_words > DESCRIPTION_TARGET_WORDS:
        fail(f"description exceeds target {DESCRIPTION_TARGET_WORDS} words: {desc_words}")

    body_words = word_count(body)
    if body_words > SKILL_BODY_MAX_WORDS:
        fail(f"SKILL.md body exceeds {SKILL_BODY_MAX_WORDS} words: {body_words}")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            fail(f"required section missing: {section}")

    for token in ["INPUT_", "OUTPUT_", "ENV_"]:
        if token not in text:
            fail(f"required variable prefix missing in SKILL.md: {token}")

    for child in skill_dir.iterdir():
        if child.is_dir() and child.name not in ALLOWED_SUPPORT_DIRS:
            fail(f"unsupported support directory: {child.name}")

    check_fence_balance(text, "SKILL.md")
    check_links(skill_dir, text, "SKILL.md")
    for md in skill_dir.rglob("*.md"):
        rel = str(md.relative_to(skill_dir))
        md_text = md.read_text(encoding="utf-8")
        check_fence_balance(md_text, rel)
        check_links(skill_dir, md_text, rel)

    print(f"PASS: {skill_dir}")
    print(f"name_chars={len(name)} description_chars={len(description)} description_words={desc_words} body_words={body_words}")


if __name__ == "__main__":
    main()
