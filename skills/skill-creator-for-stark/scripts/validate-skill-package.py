#!/usr/bin/env python3
"""portable skill package를 검증한다.

Usage:
  python3 skills/skill-creator-for-stark/scripts/validate-skill-package.py skills/<skill-name>
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REQUIRED_KEYS = ["name", "description", "version", "author", "license"]
ALLOWED_SUPPORT_DIRS = {"references", "templates", "scripts", "assets", "history", "feedback", "evals"}
IGNORED_TOP_LEVEL_DIRS = {".venv", ".ruff_cache", "__pycache__"}
REQUIRED_SECTIONS = [
    "## 입력 변수",
    "## 출력 변수",
    "## 필수 환경",
    "## 하드 게이트 (Hard Gates)",
    "## 빠른 중단 조건 (Fast Fail)",
    "## 작업 절차 (Workflow)",
    "## 커밋 주의사항 (Commit Pitfalls)",
    "## 검증 체크리스트 (Verification Checklist)",
]
FEEDBACK_REQUIRED_TOKENS = ["feedback/", "중복", "read-back"]
VARIABLE_TABLE_HEADER = "| 변수 | 필수 | 기본값 | 설명 |"
ENV_TABLE_HEADER = "| 환경 항목 | 필수 | 기본값 | 설명 |"
VALID_REQUIRED_VALUES = {"required", "optional"}
DESCRIPTION_MAX_CHARS = 1024
DESCRIPTION_TARGET_WORDS = 100
SKILL_BODY_MAX_WORDS = 5000
NAME_MAX_CHARS = 64
INPUT_WARNING_THRESHOLD = 6
OUTPUT_WARNING_THRESHOLD = 6
ENV_WARNING_THRESHOLD = 4
PACKAGE_HARD_GATE_TERMS = [
    "Metadata gate",
    "Body size gate",
    "directory basename",
    "description은 1-1024",
    "5,000 words",
    "5000 words",
]
PACKAGE_AUTHORING_ALLOWLIST = {
    "skill-creator-for-stark",
    "agent-skill-authoring",
}
VALID_EVAL_TYPES = {"command", "llm-judge"}
MIN_GOLDEN_CASES = 3
OUTPUT_PLACEHOLDER = "{output}"
_JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)

TEMPLATE_HINT_TERMS = [
    "template",
    "템플릿",
    "skeleton",
    "골격",
    "copy this",
    "복사",
    "frontmatter",
]

warnings: list[str] = []


def warn(message: str) -> None:
    warnings.append(message)


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
    generated_skill_examples = {"scripts/run_evals.py", "scripts/run_pipeline.py"}
    for match in re.findall(r"`((?:references|templates|scripts|assets|history|evals)/[^`]+)`", text):
        if "<" in match or ">" in match:
            continue
        if skill_dir.name in PACKAGE_AUTHORING_ALLOWLIST and match in generated_skill_examples:
            continue
        if "*" in match or " " in match:
            continue
        candidate = skill_dir / match
        if not candidate.exists():
            fail(f"linked support file not found in {label}: {match}")


def section_text(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    next_match = re.search(r"^## ", text[start + len(heading) :], flags=re.MULTILINE)
    if not next_match:
        return text[start:]
    return text[start : start + len(heading) + next_match.start()]


def section_by_any_heading(text: str, headings: list[str]) -> str:
    for heading in headings:
        section = section_text(text, heading)
        if section:
            return section
    return ""


def parse_table_rows(section: str) -> list[list[str]]:
    rows = []
    for line in section.splitlines():
        if line.startswith("| `"):
            rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    return rows


def check_variable_tables(text: str) -> tuple[int, int, int]:
    counts = []
    for heading in ["## 입력 변수", "## 출력 변수"]:
        section = section_text(text, heading)
        if VARIABLE_TABLE_HEADER not in section:
            fail(f"variable table header missing in section: {heading}")
        rows = parse_table_rows(section)
        if not rows:
            fail(f"no variable rows found in section: {heading}")
        for row in rows:
            if len(row) < 4:
                fail(f"variable table row must have at least 4 cells in {heading}: {row}")
            if row[1] not in VALID_REQUIRED_VALUES:
                fail(f"variable required cell must be required or optional in {heading}: {row}")
            if not row[2] or row[2] in {"-", "TBD", "<default>"}:
                fail(f"variable default cell must be explicit in {heading}: {row}")
            if len(row[3]) < 20:
                fail(f"variable description too short in {heading}: {' | '.join(row)}")
        counts.append(len(rows))

    env_section = section_text(text, "## 필수 환경")
    if ENV_TABLE_HEADER not in env_section:
        fail("environment table header missing in section: ## 필수 환경")
    env_rows = parse_table_rows(env_section)
    if not env_rows:
        fail("no ENV rows found in section: ## 필수 환경")
    for row in env_rows:
        if len(row) < 4:
            fail(f"ENV table row must have at least 4 cells: {row}")
        if row[1] not in VALID_REQUIRED_VALUES:
            fail(f"ENV required cell must be required or optional: {row}")
        if not row[2] or row[2] in {"-", "TBD", "<default>"}:
            fail(f"ENV default cell must be explicit: {row}")
        if len(row[3]) < 20:
            fail(f"ENV description too short: {' | '.join(row)}")
    return counts[0], counts[1], len(env_rows)


def check_contract_minimalism(input_count: int, output_count: int, env_count: int) -> None:
    if input_count > INPUT_WARNING_THRESHOLD:
        warn(f"INPUT_ rows exceed review threshold {INPUT_WARNING_THRESHOLD}: {input_count}")
    if output_count > OUTPUT_WARNING_THRESHOLD:
        warn(f"OUTPUT_ rows exceed review threshold {OUTPUT_WARNING_THRESHOLD}: {output_count}")
    if env_count > ENV_WARNING_THRESHOLD:
        warn(f"ENV_ rows exceed review threshold {ENV_WARNING_THRESHOLD}: {env_count}")


def check_trigger_duplication(text: str) -> None:
    has_use = "## 사용 시점" in text
    has_not_use = "## 사용하지 말아야 할 때" in text
    has_examples = "## Trigger Examples" in text or "## Trigger 예시" in text
    has_canonical = "## 사용 판단" in text or "## Trigger 예시 운영" in text
    if has_use and has_not_use and has_examples and not has_canonical:
        fail("trigger judgment is duplicated across 사용 시점/사용하지 말아야 할 때/Trigger Examples")
    if has_use and has_not_use and has_examples:
        warn("trigger judgment may be duplicated; prefer one canonical trigger section")


def check_hard_gate_specificity(skill_name: str, text: str) -> None:
    section = section_by_any_heading(text, ["## 하드 게이트 (Hard Gates)", "## Hard Gates"])
    if not section:
        fail("hard gate section missing")
    leaked = [term for term in PACKAGE_HARD_GATE_TERMS if term in section]
    if leaked and skill_name not in PACKAGE_AUTHORING_ALLOWLIST:
        fail("generated skill Hard Gates contain package-authoring terms: " + ", ".join(leaked))
    if leaked:
        warn("package-authoring hard gate terms present; allowed for authoring skill: " + ", ".join(leaked))


def check_template_placement(skill_dir: Path) -> None:
    templates_dir = skill_dir / "templates"
    template_files = list(templates_dir.rglob("*")) if templates_dir.exists() else []
    has_template_file = any(p.is_file() for p in template_files)
    suspicious_refs: list[str] = []
    for ref in (skill_dir / "references").rglob("*.md") if (skill_dir / "references").exists() else []:
        ref_text = ref.read_text(encoding="utf-8")
        lower = ref_text.lower()
        if any(term.lower() in lower for term in TEMPLATE_HINT_TERMS):
            if "```yaml" in ref_text or "```markdown" in ref_text or "---" in ref_text:
                suspicious_refs.append(str(ref.relative_to(skill_dir)))
    if suspicious_refs and not has_template_file:
        fail("reference files appear to contain output skeletons but templates/ has no files: " + ", ".join(suspicious_refs))
    if suspicious_refs:
        warn("check whether output skeleton belongs in templates/: " + ", ".join(suspicious_refs[:5]))


def check_feedback_guidance(text: str) -> None:
    missing = [token for token in FEEDBACK_REQUIRED_TOKENS if token not in text]
    if missing:
        fail("skill feedback logging guidance missing concrete tokens: " + ", ".join(missing))
    if "skill-dissatisfaction" not in text and "불만족" not in text:
        fail("skill feedback logging guidance must identify dissatisfaction incidents")


def check_eval_spec(skill_dir: Path) -> None:
    evals_dir = skill_dir / "evals"
    if not evals_dir.exists():
        return
    if not evals_dir.is_dir():
        fail("evals exists but is not a directory")

    specs = sorted(evals_dir.glob("*.eval.yaml")) + sorted(evals_dir.glob("*.eval.yml"))
    if not specs:
        fail("evals/ exists but no evals/*.eval.yaml suite manifest was found")
    runner = skill_dir / "scripts" / "run_evals.py"
    if not runner.exists():
        fail("evals/ exists but scripts/run_evals.py is missing")
    proc = subprocess.run(
        [sys.executable, str(runner), str(skill_dir), "--validate"],
        cwd=str(skill_dir),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        fail("case-based eval suite validation failed: " + (proc.stdout + proc.stderr).strip())


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

    input_count, output_count, env_count = check_variable_tables(text)
    check_contract_minimalism(input_count, output_count, env_count)
    check_trigger_duplication(text)
    check_hard_gate_specificity(name, text)
    check_template_placement(skill_dir)
    check_feedback_guidance(text)
    check_eval_spec(skill_dir)

    for child in skill_dir.iterdir():
        if child.is_dir() and child.name not in ALLOWED_SUPPORT_DIRS and child.name not in IGNORED_TOP_LEVEL_DIRS:
            fail(f"unsupported support directory: {child.name}")

    check_fence_balance(text, "SKILL.md")
    check_links(skill_dir, text, "SKILL.md")
    for md in skill_dir.rglob("*.md"):
        rel = str(md.relative_to(skill_dir))
        md_text = md.read_text(encoding="utf-8")
        check_fence_balance(md_text, rel)
        check_links(skill_dir, md_text, rel)

    print(f"PASS: {skill_dir}")
    print(
        f"name_chars={len(name)} description_chars={len(description)} "
        f"description_words={desc_words} body_words={body_words} "
        f"input_rows={input_count} output_rows={output_count} env_rows={env_count}"
    )
    for message in warnings:
        print(f"WARN: {message}")


if __name__ == "__main__":
    main()
