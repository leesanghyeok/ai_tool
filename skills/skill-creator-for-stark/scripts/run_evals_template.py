#!/usr/bin/env python3
"""
생성된 skill 내부에 scripts/run_evals.py로 포함되는 case-based eval runner.

Spec model:
  evals/<skill>.eval.yaml          # suite manifest + 사람이 읽는 case map
  evals/<case-id>/case.yaml        # canonical case group definition

eval.yaml manifest가 source of truth다. eval.yaml에 선언된 case만 validate/run하며,
disk에 남아 있지만 선언되지 않은 case directory는 무시한다.

non-llm-judge case는 자체 run command와 assertions를 가진다. llm-judge case는
top-level judge command와 assertion-level prompts를 가진다. global assertions와
top-level suite run command는 없다. 지원 assertion type은 다음 두 가지다.
  - command: shell command exits 0
  - llm-judge: subprocess judge command가 non-empty natural-language response를 반환

Expected 처리는 자동이다. case가 `expected`를 선언하면 --promote가 없을 때
produced output을 해당 file과 byte-compare한다. --promote를 쓰면 passing case
output으로 expected file을 생성하거나 overwrite한다.

Usage:
  uv run python scripts/run_evals.py [skill_dir] [--validate] [--promote] [--json]

Exit codes:
  0 - valid / 선택된 suite case 전체 통과
  1 - malformed spec, failed command, failed judge, or failed expected compare
  2 - eval suite not found
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

VALID_ASSERTION_TYPES = ("command", "llm-judge")
VALID_CASE_TYPES = ("happy-path", "edge", "regression", "safety", "llm-judge", "integration")
VALID_JUDGE_METHODS = ("aggregate", "each-session", "subagent")
DEFAULT_TIMEOUT = 120
INPUT_PLACEHOLDER = "{input}"
OUTPUT_PLACEHOLDER = "{output}"
EXPECTED_PLACEHOLDER = "{expected}"
JUDGE_PACKET_PLACEHOLDER = "{judge_packet}"
JUDGE_OUTPUT_PLACEHOLDER = "{judge_output}"
ASSERTION_INPUT_PLACEHOLDER = "{assertion_input}"
JUDGE_EVIDENCE_PLACEHOLDER = "{judge_evidence}"
PRIMARY_OUTPUT_PLACEHOLDER = "{primary_output}"
PIPELINE_OUTPUT_PLACEHOLDER = "{pipeline_output}"
PYTHON_PLACEHOLDER = "{python}"


class SimpleYamlError(ValueError):
    pass


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            return line[:i].rstrip()
    return line.rstrip()


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value in ("null", "~"):
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if value.startswith("[") or value.startswith("{"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
    try:
        return int(value)
    except ValueError:
        return value


def _is_block_scalar(content: str) -> bool:
    return content.endswith(": |") or content.endswith(": >") or content in ("|", ">")


def _block_key_prefix(content: str) -> str:
    return content if content in ("|", ">") else content[:-2].rstrip() + ":"


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _collect_literal_block(raw: list[str], index: int, indent: int) -> tuple[str, int]:
    block_indent = None
    block_lines: list[str] = []
    index += 1
    while index < len(raw):
        line = raw[index]
        if not line.strip():
            block_lines.append("")
            index += 1
            continue
        nindent = _indent_of(line)
        if nindent <= indent:
            break
        block_indent = nindent if block_indent is None else block_indent
        block_lines.append(line[block_indent:])
        index += 1
    return "\n".join(block_lines).rstrip("\n"), index


def _next_logical_line(raw: list[str], index: int) -> tuple[tuple[int, str] | None, int]:
    stripped_comment = _strip_comment(raw[index])
    if not stripped_comment.strip():
        return None, index + 1
    indent = _indent_of(stripped_comment)
    content = stripped_comment.strip()
    if not _is_block_scalar(content):
        return (indent, content), index + 1
    joined, index = _collect_literal_block(raw, index, indent)
    return (indent, f"{_block_key_prefix(content)} {json.dumps(joined, ensure_ascii=False)}"), index


def _logical_lines(text: str) -> list[tuple[int, str]]:
    raw = text.splitlines()
    out: list[tuple[int, str]] = []
    i = 0
    while i < len(raw):
        logical, i = _next_logical_line(raw, i)
        if logical is not None:
            out.append(logical)
    return out

def _parse_yaml_key_value(
    lines: list[tuple[int, str]],
    path: Path,
    index: int,
    indent: int,
) -> tuple[str, Any, int]:
    cur_indent, text = lines[index]
    if cur_indent != indent:
        raise SimpleYamlError(f"{path}: unexpected indent at logical line {index + 1}")
    if ":" not in text:
        raise SimpleYamlError(f"{path}: expected key: value at logical line {index + 1}")

    key, raw_val = text.split(":", 1)
    index += 1
    if raw_val.strip():
        return key.strip(), _parse_scalar(raw_val), index
    if index < len(lines) and lines[index][0] > indent:
        val, index = _parse_yaml_block(lines, path, index, lines[index][0])
        return key.strip(), val, index
    return key.strip(), None, index


def _parse_yaml_list(
    lines: list[tuple[int, str]],
    path: Path,
    index: int,
    indent: int,
) -> tuple[list[Any], int]:
    arr: list[Any] = []
    while index < len(lines) and lines[index][0] == indent and lines[index][1].startswith("- "):
        item_text = lines[index][1][2:].strip()
        index += 1
        if not item_text:
            val, index = _parse_yaml_block(lines, path, index, indent + 2)
            arr.append(val)
        elif ":" in item_text:
            item, index = _parse_yaml_list_mapping_item(lines, path, item_text, index, indent)
            arr.append(item)
        else:
            arr.append(_parse_scalar(item_text))
    return arr, index


def _parse_yaml_list_mapping_item(
    lines: list[tuple[int, str]],
    path: Path,
    item_text: str,
    index: int,
    indent: int,
) -> tuple[dict[str, Any], int]:
    key, raw_val = item_text.split(":", 1)
    item: dict[str, Any] = {}
    if raw_val.strip():
        item[key.strip()] = _parse_scalar(raw_val)
    else:
        val, index = _parse_yaml_block(lines, path, index, indent + 2)
        item[key.strip()] = val

    while index < len(lines) and lines[index][0] > indent:
        child_indent, child_text = lines[index]
        if child_indent < indent + 2 or child_text.startswith("- "):
            break
        ckey, cval, index = _parse_yaml_key_value(lines, path, index, child_indent)
        item[ckey] = cval
    return item, index


def _parse_yaml_mapping(
    lines: list[tuple[int, str]],
    path: Path,
    index: int,
    indent: int,
) -> tuple[dict[str, Any], int]:
    mapping: dict[str, Any] = {}
    while index < len(lines) and lines[index][0] == indent and not lines[index][1].startswith("- "):
        key, val, index = _parse_yaml_key_value(lines, path, index, indent)
        mapping[key] = val
    return mapping, index


def _parse_yaml_block(lines: list[tuple[int, str]], path: Path, index: int, indent: int) -> tuple[Any, int]:
    if index >= len(lines) or lines[index][0] < indent:
        return {}, index
    if lines[index][1].startswith("- "):
        return _parse_yaml_list(lines, path, index, indent)
    return _parse_yaml_mapping(lines, path, index, indent)


def parse_yaml_subset(path: Path) -> Any:
    """eval.yaml/case.yaml에서 사용하는 작은 YAML 부분집합을 파싱한다.

    Nested mappings, mappings/scalars list, quoted/unquoted scalars,
    ints/bools/null, inline JSON arrays/objects, literal/folded blocks를 지원한다.
    의도적으로 general YAML parser가 아니다. generated spec은 generated skill에
    PyYAML dependency를 추가하지 않도록 이 제한된 shape를 유지해야 한다.
    """
    lines = _logical_lines(path.read_text(encoding="utf-8"))
    if not lines:
        return {}

    parsed, end = _parse_yaml_block(lines, path, 0, lines[0][0])
    if end != len(lines):
        raise SimpleYamlError(f"{path}: could not parse all lines")
    return parsed


def find_spec(skill_dir: Path) -> Path | None:
    evals_dir = skill_dir / "evals"
    if not evals_dir.is_dir():
        return None
    preferred = sorted(evals_dir.glob("*.eval.yaml")) + sorted(evals_dir.glob("*.eval.yml"))
    return preferred[0] if preferred else None


def parse_spec(spec_path: Path) -> dict:
    try:
        spec = parse_yaml_subset(spec_path)
    except Exception as exc:
        raise ValueError(f"{spec_path}: malformed eval yaml: {exc}") from exc
    if not isinstance(spec, dict):
        raise ValueError(f"{spec_path}: eval spec must be a mapping")
    return spec


def _case_path(skill_dir: Path, case_entry: dict) -> Path:
    return (skill_dir / "evals" / str(case_entry.get("path", ""))).resolve()


def _manifest_entries(spec: dict) -> tuple[list[dict], str]:
    if "entries" in spec:
        entries = spec.get("entries")
        return (entries if isinstance(entries, list) else []), "entries"
    entries = spec.get("cases")
    return (entries if isinstance(entries, list) else []), "cases"


def _stable_slug(index: int, case_id: str) -> str:
    digest = hashlib.sha256(case_id.encode("utf-8")).hexdigest()[:12]
    return f"{index:02d}-{digest}"


def _case_base(case_group: dict, path: Path, entry: dict) -> dict:
    return {
        "__path": str(path),
        "__dir": str(path.parent),
        "__case_group_id": case_group.get("id", entry.get("id")),
        "__entry_id": entry.get("id"),
    }


def _expanded_subcase(case_group: dict, entry: dict, base: dict, item: dict, index: int) -> dict:
    case = dict(item)
    case.setdefault("type", case_group.get("type") or entry.get("type"))
    case.setdefault("title", case.get("id", "case"))
    case.update(base)
    case["__case_index"] = index
    case["__artifact_slug"] = _stable_slug(index, str(case.get("id", f"case-{index}")))
    return case


def _expand_case_group(case_group: dict, path: Path, entry: dict) -> list[dict]:
    base = _case_base(case_group, path, entry)
    group_cases = case_group.get("cases")
    if isinstance(group_cases, list):
        return [
            _expanded_subcase(case_group, entry, base, item, index)
            for index, item in enumerate(group_cases, start=1)
            if isinstance(item, dict)
        ]
    case = dict(case_group)
    case.update(base)
    case["__case_index"] = 1
    case["__artifact_slug"] = _stable_slug(1, str(case.get("id", entry.get("id", "case"))))
    return [case]

def load_cases(spec: dict, skill_dir: Path) -> list[dict]:
    cases: list[dict] = []
    entries, _ = _manifest_entries(spec)
    for entry in entries:
        path = _case_path(skill_dir, entry)
        case_group = parse_yaml_subset(path)
        if not isinstance(case_group, dict):
            raise ValueError(f"{path}: case spec must be a mapping")
        cases.extend(_expand_case_group(case_group, path, entry))
    return cases


def _validate_spec_header(spec: dict) -> list[str]:
    errors: list[str] = []
    if not spec.get("skill"):
        errors.append("eval.yaml: missing 'skill'")
    if not spec.get("title"):
        errors.append("eval.yaml: missing 'title'")
    if "description" in spec:
        errors.append("eval.yaml: 'description' is not allowed; keep only 'title'")
    policy = spec.get("test_policy", {}) or {}
    if not isinstance(policy, dict):
        errors.append("eval.yaml: 'test_policy' must be a mapping when present")
    if "entries" in spec and "cases" in spec:
        errors.append("eval.yaml: use either 'entries' or legacy 'cases', not both")
    return errors


def _required_manifest_fields(manifest_key: str) -> tuple[str, ...]:
    if manifest_key == "entries":
        return ("id", "type", "path")
    return ("id", "type", "title", "path")


def _validate_manifest_entry_shape(entry: Any, where: str, manifest_key: str) -> list[str]:
    if not isinstance(entry, dict):
        return [f"{where}: must be a mapping"]
    errors = [f"{where}: missing '{field}'" for field in _required_manifest_fields(manifest_key) if not entry.get(field)]
    if entry.get("type") and entry["type"] not in VALID_CASE_TYPES:
        errors.append(f"{where}: unsupported type {entry['type']!r}")
    return errors


def _record_declared_id(entry: dict, where: str, declared_ids: set[str]) -> list[str]:
    entry_id = entry.get("id")
    if not isinstance(entry_id, str):
        return []
    if entry_id in declared_ids:
        return [f"{where}: duplicate id {entry['id']!r}"]
    declared_ids.add(entry_id)
    return []


def _validate_case_file_entry(entry: dict, where: str, skill_dir: Path, manifest_key: str) -> list[str]:
    if not entry.get("path"):
        return []
    cpath = _case_path(skill_dir, entry)
    if not cpath.exists():
        return [f"{where}: case file not found: {entry['path']}"]
    try:
        case = parse_yaml_subset(cpath)
    except Exception as exc:
        return [f"{where}: malformed case yaml: {exc}"]
    return validate_case(case, cpath, entry, new_shape=(manifest_key == "entries"))


def _validate_manifest_entry(entry: Any, where: str, skill_dir: Path, manifest_key: str, declared_ids: set[str]) -> list[str]:
    errors = _validate_manifest_entry_shape(entry, where, manifest_key)
    if not isinstance(entry, dict):
        return errors
    errors.extend(_record_declared_id(entry, where, declared_ids))
    errors.extend(_validate_case_file_entry(entry, where, skill_dir, manifest_key))
    return errors


def validate_spec(spec: dict, skill_dir: Path) -> list[str]:
    errors = _validate_spec_header(spec)
    case_entries, manifest_key = _manifest_entries(spec)
    if not isinstance(case_entries, list) or not case_entries:
        return errors + ["eval.yaml: 'entries' must be a non-empty list"]
    declared_ids: set[str] = set()
    for i, entry in enumerate(case_entries):
        errors.extend(_validate_manifest_entry(entry, f"eval.yaml {manifest_key}[{i}]", skill_dir, manifest_key, declared_ids))
    return errors

def _case_prefix(cpath: Path) -> str:
    return f"{cpath.relative_to(cpath.parents[2]) if len(cpath.parents) > 2 else cpath}"


def _validate_case_group_header(case: dict, entry: dict, prefix: str, new_shape: bool) -> list[str]:
    errors = [f"{prefix}: missing '{field}'" for field in ("id", "type") if not case.get(field)]
    if not new_shape and not case.get("title"):
        errors.append(f"{prefix}: missing 'title'")
    for field in ("id", "type"):
        if case.get(field) != entry.get(field):
            errors.append(f"{prefix}: {field} does not match eval.yaml entry")
    if not new_shape and case.get("title") != entry.get("title"):
        errors.append(f"{prefix}: title does not match eval.yaml entry")
    return errors


def _subcase_entry(case: dict, subcase: dict) -> dict:
    return {
        "id": subcase.get("id"),
        "type": subcase.get("type", case.get("type")),
        "title": subcase.get("title", subcase.get("id")),
    }


def _validate_subcase(case: dict, cpath: Path, subcase: Any, where: str, seen_case_ids: set[str]) -> list[str]:
    if not isinstance(subcase, dict):
        return [f"{where}: must be a mapping"]
    errors: list[str] = []
    if not subcase.get("id"):
        errors.append(f"{where}: missing 'id'")
    elif subcase["id"] in seen_case_ids:
        errors.append(f"{where}: duplicate id {subcase['id']!r}")
    else:
        seen_case_ids.add(subcase["id"])
    sub = dict(subcase)
    sub.setdefault("type", case.get("type"))
    sub.setdefault("title", subcase.get("id"))
    errors.extend(_validate_executable_case(sub, cpath, _subcase_entry(case, subcase), where))
    return errors


def _validate_case_group_cases(case: dict, cpath: Path, prefix: str, group_cases: list) -> list[str]:
    if not group_cases:
        return [f"{prefix}: cases must be a non-empty list"]
    errors: list[str] = []
    seen_case_ids: set[str] = set()
    for index, subcase in enumerate(group_cases):
        errors.extend(_validate_subcase(case, cpath, subcase, f"{prefix} cases[{index}]", seen_case_ids))
    return errors


def validate_case(case: dict, cpath: Path, entry: dict, new_shape: bool = False) -> list[str]:
    prefix = _case_prefix(cpath)
    errors = _validate_case_group_header(case, entry, prefix, new_shape)
    group_cases = case.get("cases")
    if isinstance(group_cases, list):
        return errors + _validate_case_group_cases(case, cpath, prefix, group_cases)
    return errors + _validate_executable_case(case, cpath, entry, prefix, require_title=not new_shape)

def _validate_judge_command(command: Any, prefix: str) -> list[str]:
    if not command:
        return [f"{prefix}: judge.command is required"]
    has_packet = JUDGE_PACKET_PLACEHOLDER in command and JUDGE_OUTPUT_PLACEHOLDER in command
    has_assertion = ASSERTION_INPUT_PLACEHOLDER in command and JUDGE_OUTPUT_PLACEHOLDER in command
    if has_packet or has_assertion:
        return []
    return [
        f"{prefix}: judge.command must contain either {JUDGE_PACKET_PLACEHOLDER} and "
        f"{JUDGE_OUTPUT_PLACEHOLDER}, or {ASSERTION_INPUT_PLACEHOLDER} and {JUDGE_OUTPUT_PLACEHOLDER}"
    ]


def _validate_judge_case_definition(case: dict, prefix: str) -> list[str]:
    errors: list[str] = []
    judge = case.get("judge")
    if case.get("run") is not None:
        errors.append(f"{prefix}: type 'llm-judge' must not define run.command; use top-level judge.command")
    if not isinstance(judge, dict):
        return errors + [f"{prefix}: type 'llm-judge' must define top-level judge mapping"]
    if judge.get("method") not in VALID_JUDGE_METHODS:
        errors.append(f"{prefix}: judge.method must be one of {VALID_JUDGE_METHODS}")
    errors.extend(_validate_judge_command(judge.get("command"), prefix))
    verify_command = judge.get("verifyCommand")
    if verify_command and JUDGE_EVIDENCE_PLACEHOLDER not in verify_command:
        errors.append(f"{prefix}: judge.verifyCommand must contain {JUDGE_EVIDENCE_PLACEHOLDER}")
    return errors

def _validate_judge_setup(case: dict, prefix: str) -> list[str]:
    setup = case.get("setup")
    if setup is None:
        return []
    if not isinstance(setup, dict):
        return [f"{prefix}: setup must be a mapping when present"]

    setup_command = setup.get("command")
    if not setup_command:
        return [f"{prefix}: setup.command is required when setup is present"]
    if PIPELINE_OUTPUT_PLACEHOLDER not in setup_command:
        return [f"{prefix}: setup.command must contain {PIPELINE_OUTPUT_PLACEHOLDER}"]
    return []


def _validate_run_case_definition(case: dict, prefix: str) -> list[str]:
    errors: list[str] = []
    run = case.get("run")
    if case.get("judge") is not None:
        errors.append(f"{prefix}: non-llm-judge case must not define top-level judge")
    if not isinstance(run, dict) or not run.get("command"):
        errors.append(f"{prefix}: non-llm-judge case must define run.command")
    elif OUTPUT_PLACEHOLDER not in run["command"]:
        errors.append(f"{prefix}: run.command must contain {OUTPUT_PLACEHOLDER}")
    return errors


def _validate_assertions(case: dict, prefix: str) -> list[str]:
    errors: list[str] = []
    assertions = case.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        return [f"{prefix}: assertions must be a non-empty list"]

    for i, assertion in enumerate(assertions):
        errors.extend(_validate_assertion(case, assertion, f"{prefix} assertions[{i}]"))
    return errors


def _validate_assertion(case: dict, assertion: Any, awhere: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(assertion, dict):
        return [f"{awhere}: must be a mapping"]

    for field in ("id", "title", "type"):
        if not assertion.get(field):
            errors.append(f"{awhere}: missing '{field}'")
    atype = assertion.get("type")
    if atype not in VALID_ASSERTION_TYPES:
        errors.append(f"{awhere}: type must be one of {VALID_ASSERTION_TYPES}, got {atype!r}")
    if atype == "command" and not assertion.get("cmd"):
        errors.append(f"{awhere}: command assertion needs 'cmd'")
    if atype == "llm-judge":
        errors.extend(_validate_llm_judge_assertion(case, assertion, awhere))
    return errors


def _validate_llm_judge_assertion(case: dict, assertion: dict, awhere: str) -> list[str]:
    errors: list[str] = []
    if case.get("type") != "llm-judge":
        errors.append(f"{awhere}: llm-judge assertion is only allowed in type 'llm-judge' cases")
    if assertion.get("judge") is not None:
        errors.append(f"{awhere}: llm-judge assertion must not define judge; use top-level judge")
    if assertion.get("checks") is not None:
        errors.append(f"{awhere}: llm-judge assertion must not define checks; put the prompt on the assertion")
    if not assertion.get("prompt"):
        errors.append(f"{awhere}: llm-judge assertion needs 'prompt'")
    return errors


def _validate_case_paths(case: dict, cpath: Path, prefix: str) -> list[str]:
    errors: list[str] = []

    if case.get("input") and not (cpath.parent / case["input"]).exists():
        errors.append(f"{prefix}: input file not found: {case['input']}")
    if case.get("expected") and not (cpath.parent / case["expected"]).exists():
        errors.append(f"{prefix}: expected file not found: {case['expected']}")
    return errors


def _validate_executable_case(case: dict, cpath: Path, entry: dict, prefix: str, require_title: bool = True) -> list[str]:
    errors: list[str] = []
    if require_title and not case.get("title"):
        errors.append(f"{prefix}: missing 'title'")

    if case.get("type") == "llm-judge":
        errors.extend(_validate_judge_case_definition(case, prefix))
        errors.extend(_validate_judge_setup(case, prefix))
    else:
        errors.extend(_validate_run_case_definition(case, prefix))
    errors.extend(_validate_case_paths(case, cpath, prefix))
    errors.extend(_validate_assertions(case, prefix))
    return errors


def _bind_placeholders(cmd: str, **paths: Path | None) -> str:
    replacements = {
        PYTHON_PLACEHOLDER: Path(sys.executable),
        INPUT_PLACEHOLDER: paths.get("input_path"),
        OUTPUT_PLACEHOLDER: paths.get("output_path"),
        EXPECTED_PLACEHOLDER: paths.get("expected_path"),
        JUDGE_PACKET_PLACEHOLDER: paths.get("judge_packet"),
        JUDGE_OUTPUT_PLACEHOLDER: paths.get("judge_output"),
        ASSERTION_INPUT_PLACEHOLDER: paths.get("assertion_input"),
        JUDGE_EVIDENCE_PLACEHOLDER: paths.get("judge_evidence"),
        PRIMARY_OUTPUT_PLACEHOLDER: paths.get("primary_output"),
        PIPELINE_OUTPUT_PLACEHOLDER: paths.get("pipeline_output"),
    }
    bound = cmd
    for placeholder, path in replacements.items():
        if placeholder in bound:
            if path is None:
                raise ValueError(f"placeholder {placeholder} has no bound path")
            bound = bound.replace(placeholder, shlex.quote(str(path)))
    return bound


def _run_shell(cmd: str, cwd: Path, timeout: int) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, shell=True, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)  # noqa: S602
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "timeout")
        return 124, stdout, stderr


def _expected_path(case: dict) -> Path | None:
    if case.get("expected"):
        return Path(case["__dir"]) / case["expected"]
    return None


def _input_path(case: dict) -> Path | None:
    if case.get("input"):
        return Path(case["__dir"]) / case["input"]
    return None


def _promote_path(case: dict, output_path: Path) -> Path:
    expected = _expected_path(case)
    if expected is not None:
        return expected
    return Path(case["__dir"]) / "expected.json"


def _compare_expected(case: dict, output_path: Path) -> dict | None:
    expected = _expected_path(case)
    if expected is None:
        return None
    ok = expected.read_bytes() == output_path.read_bytes()
    return {"id": "expected-equality", "title": "expected와 실제 출력이 동일한지 자동 검증", "type": "expected", "status": "pass" if ok else "fail"}


def _run_command_assertion(assertion: dict, case: dict, output_path: Path, cwd: Path) -> dict:
    expected = _expected_path(case)
    cmd = _bind_placeholders(assertion["cmd"], input_path=_input_path(case), output_path=output_path, expected_path=expected)
    rc, stdout, stderr = _run_shell(cmd, cwd, int(assertion.get("timeout_sec") or DEFAULT_TIMEOUT))
    return {
        "id": assertion["id"],
        "title": assertion["title"],
        "type": "command",
        "status": "pass" if rc == 0 else "fail",
        "exit_code": rc,
        "stdout": stdout[-2000:],
        "stderr": stderr[-2000:],
    }


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _excerpt(path: Path, limit: int = 1200) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - evidence should record read-back failures.
        return f"<read failed: {exc}>"
    return text[:limit]


def _pipeline_status(path: Path) -> str:
    try:
        payload = _load_json_file(path)
    except Exception:
        return "unknown"
    if isinstance(payload, dict) and isinstance(payload.get("status"), str):
        return payload["status"]
    return "unknown"


def _files_written_read_back(path: Path) -> list[dict[str, Any]]:
    try:
        payload = _load_json_file(path)
    except Exception:
        return []
    files = payload.get("files_written") if isinstance(payload, dict) else None
    if not isinstance(files, list):
        return []
    out: list[dict[str, Any]] = []
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            continue
        fpath = Path(item["path"])
        exists = fpath.exists()
        out.append({
            "path": str(fpath),
            "exists": exists,
            "sha256": _sha256_file(fpath) if exists and fpath.is_file() else "",
            "excerpt": _excerpt(fpath, 500) if exists and fpath.is_file() else "",
        })
    return out


def _primary_output_text(primary_output: Path) -> str:
    try:
        payload = json.loads(primary_output.read_text(encoding="utf-8"))
    except Exception:
        return primary_output.read_text(encoding="utf-8")
    output = payload.get("output") if isinstance(payload, dict) else None
    if isinstance(output, dict) and isinstance(output.get("content"), str):
        return output["content"]
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _write_judge_evidence(case: dict, input_path: Path | None, primary_output: Path, evidence_path: Path, setup_result: dict | None = None) -> None:
    payload = {
        "schema_version": 1,
        "case_id": case["id"],
        "input": {"path": str(input_path) if input_path else "", "sha256": _sha256_file(input_path) if input_path and input_path.exists() else ""},
        "primary_output": {
            "path": str(primary_output),
            "sha256": _sha256_file(primary_output),
            "status": _pipeline_status(primary_output),
            "required_fields": ["schema_version", "status"],
            "summary": _primary_output_text(primary_output)[:500],
            "read_back_excerpt": _excerpt(primary_output, 1000),
        },
        "artifacts": [{"path": str(primary_output), "sha256": _sha256_file(primary_output), "kind": "primary-output", "must_exist": True}],
        "checks": [
            {"id": "primary-output-exists", "type": "file-exists", "path": "primary_output.path"},
            {"id": "primary-output-hash", "type": "sha256-matches", "path": "primary_output.path"},
        ],
        "redaction": {"secret_like_values_removed": True, "rules": ["secret", "token", "private-url"]},
    }
    if setup_result is not None:
        payload["setup"] = setup_result
        payload["primary_output"]["kind"] = "pipeline-output"
        payload["files_written_read_back"] = _files_written_read_back(primary_output)
    else:
        payload["primary_output"]["required_fields"].append("output.content")
    evidence_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _evidence_prompt(primary_output: Path, evidence_path: Path) -> str:
    return (
        "Primary output:\n"
        + _primary_output_text(primary_output)
        + "\n\nCase-local provenance evidence:\n"
        + _excerpt(evidence_path, 1800)
    )


def _run_llm_judge_setup(case: dict, cwd: Path, temp_dir: Path) -> tuple[dict | None, Path | None]:
    setup = case.get("setup")
    if not setup:
        return None, None
    pipeline_output = temp_dir / "pipeline-output.json"
    try:
        cmd = _bind_placeholders(
            setup["command"],
            input_path=_input_path(case),
            output_path=None,
            expected_path=_expected_path(case),
            pipeline_output=pipeline_output,
        )
        rc, stdout, stderr = _run_shell(cmd, cwd, int(setup.get("timeout_sec") or DEFAULT_TIMEOUT))
    except ValueError as exc:
        cmd, rc, stdout, stderr = setup.get("command", ""), 1, "", str(exc)
    exists = pipeline_output.exists()
    result = {
        "id": "judge.setup",
        "title": "llm-judge setup.command 실행",
        "type": "run",
        "status": "pass" if rc == 0 and exists else "fail",
        "command": cmd,
        "exit_code": rc,
        "stdout": stdout[-2000:],
        "stderr": stderr[-2000:],
        "pipeline_output": str(pipeline_output),
        "pipeline_output_sha256": _sha256_file(pipeline_output) if exists else "",
        "pipeline_output_status": _pipeline_status(pipeline_output) if exists else "missing",
    }
    return result, pipeline_output if exists else None


def _run_llm_judge_output(case: dict, cwd: Path, primary_output: Path) -> dict:
    input_path = _input_path(case)
    if input_path is None:
        primary_output.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "success",
                    "output": {"format": "text", "content": "", "summary": ""},
                    "artifacts": [],
                    "redactions_applied": [],
                    "errors": [],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return {
            "id": "judge.output",
            "title": "llm-judge primary output 생성",
            "type": "run",
            "status": "pass",
            "exit_code": 0,
            "primary_output": str(primary_output),
        }
    cmd = (
        f"{shlex.quote(sys.executable)} scripts/run_llm_judge.py output "
        f"--input {shlex.quote(str(input_path))} --output {shlex.quote(str(primary_output))}"
    )
    rc, stdout, stderr = _run_shell(cmd, cwd, int(case.get("judge", {}).get("timeout_sec") or DEFAULT_TIMEOUT))
    return {
        "id": "judge.output",
        "title": "llm-judge primary output 생성",
        "type": "run",
        "status": "pass" if rc == 0 and primary_output.exists() else "fail",
        "exit_code": rc,
        "stdout": stdout[-2000:],
        "stderr": stderr[-2000:],
        "primary_output": str(primary_output),
    }


def _prepare_llm_primary_output(case: dict, cwd: Path, temp_dir: Path, checks: list[dict]) -> tuple[Path | None, dict | None]:
    primary_output = temp_dir / "primary-output.json"
    setup_result, setup_output = _run_llm_judge_setup(case, cwd, temp_dir)
    if setup_result is not None:
        checks.append(setup_result)
        return (setup_output if setup_result["status"] == "pass" else None), setup_result
    output_check = _run_llm_judge_output(case, cwd, primary_output)
    checks.append(output_check)
    return (primary_output if output_check["status"] == "pass" else None), None


def _write_assertion_input(case: dict, judge: dict, assertion_input: Path, primary_output: Path, evidence_path: Path) -> None:
    payload = {
        "schema_version": 1,
        "method": judge.get("method", "aggregate"),
        "primary_output": _evidence_prompt(primary_output, evidence_path),
        "assertions": [
            {"id": a["id"], "title": a["title"], "prompt": a["prompt"]}
            for a in case.get("assertions", [])
            if a.get("type") == "llm-judge"
        ],
    }
    assertion_input.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_judge_packet(packet_path: Path, primary_output: Path, evidence_path: Path) -> None:
    payload = {"schema_version": 1, "prompt": _evidence_prompt(primary_output, evidence_path)}
    packet_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _judge_command_failure(rc: int, stdout: str, stderr: str) -> dict:
    return {
        "id": "judge.command",
        "title": "llm-judge assertion mode 실행",
        "type": "llm-judge",
        "status": "fail",
        "exit_code": rc,
        "stdout": stdout[-2000:],
        "stderr": stderr[-2000:],
        "error": "judge command failed or did not create judge_output",
    }


def _empty_judge_output_failure() -> dict:
    return {"id": "judge.command", "title": "llm-judge assertion mode 실행", "type": "llm-judge", "status": "fail", "error": "judge output is empty"}


def _parse_judge_output(judge_text: str) -> tuple[str, list]:
    try:
        judge_payload = json.loads(judge_text)
    except json.JSONDecodeError:
        return "pass", []
    results = judge_payload.get("results") if isinstance(judge_payload.get("results"), list) else []
    return ("pass" if judge_payload.get("status") == "success" else "fail"), results


def _judge_evidence(assertion_input: Path, primary_output: Path, evidence_path: Path) -> dict:
    return {
        "assertion_input": str(assertion_input),
        "primary_output": str(primary_output),
        "judge_evidence": str(evidence_path),
        "provenance": json.loads(evidence_path.read_text(encoding="utf-8")),
    }


def _append_structured_judge_results(checks: list[dict], case: dict, results: list, evidence: dict) -> None:
    for result in results:
        assertion_id = result.get("assertion_id", "judge.command")
        matching = next((a for a in case.get("assertions", []) if a.get("id") == assertion_id), {})
        checks.append({
            "id": assertion_id,
            "title": matching.get("title", assertion_id),
            "type": "llm-judge",
            "status": "pass" if result.get("status") == "pass" else "fail",
            "judge_output": str(result.get("judge_output", ""))[-2000:],
            "evidence": evidence,
        })


def _append_judge_result_checks(checks: list[dict], case: dict, judge_text: str, result_status: str, results: list, evidence: dict) -> None:
    if results:
        _append_structured_judge_results(checks, case, results, evidence)
    else:
        checks.append({
            "id": "judge.command",
            "title": "llm-judge assertion mode 실행",
            "type": "llm-judge",
            "status": result_status,
            "judge_output": judge_text[-2000:],
            "evidence": evidence,
        })


def _append_verify_command(
    checks: list[dict],
    case: dict,
    judge: dict,
    paths: dict[str, Path],
    cwd: Path,
) -> None:
    verify_command = judge.get("verifyCommand")
    if not verify_command or not all(c.get("status") == "pass" for c in checks):
        return
    verify_cmd = _bind_placeholders(
        verify_command,
        input_path=_input_path(case),
        output_path=paths["output"],
        expected_path=_expected_path(case),
        judge_output=paths["judge_output"],
        assertion_input=paths["assertion_input"],
        judge_evidence=paths["evidence"],
        primary_output=paths["primary"],
    )
    vrc, vstdout, vstderr = _run_shell(verify_cmd, cwd, int(judge.get("timeout_sec") or DEFAULT_TIMEOUT))
    checks.append({
        "id": "judge.verifyCommand",
        "title": "llm-judge deterministic evidence 검증",
        "type": "command",
        "status": "pass" if vrc == 0 else "fail",
        "exit_code": vrc,
        "stdout": vstdout[-2000:],
        "stderr": vstderr[-2000:],
        "evidence": str(paths["evidence"]),
    })


def _run_bound_judge_command(
    case: dict,
    judge: dict,
    output_path: Path,
    temp_dir: Path,
    primary_output: Path,
    evidence_path: Path,
    cwd: Path,
) -> tuple[int, str, str, Path, Path]:
    assertion_input = temp_dir / "assertion-input.json"
    judge_output = temp_dir / "assertion-output.json"
    packet_path = temp_dir / "judge-packet.json"
    _write_assertion_input(case, judge, assertion_input, primary_output, evidence_path)
    _write_judge_packet(packet_path, primary_output, evidence_path)
    cmd = _bind_placeholders(
        judge["command"],
        input_path=_input_path(case),
        output_path=output_path,
        expected_path=_expected_path(case),
        judge_packet=packet_path,
        judge_output=judge_output,
        assertion_input=assertion_input,
        judge_evidence=evidence_path,
        primary_output=primary_output,
    )
    rc, stdout, stderr = _run_shell(cmd, cwd, int(judge.get("timeout_sec") or DEFAULT_TIMEOUT))
    return rc, stdout, stderr, assertion_input, judge_output


def _run_judge_assertion_phase(
    case: dict,
    output_path: Path,
    cwd: Path,
    temp_dir: Path,
    primary_output: Path,
    evidence_path: Path,
) -> tuple[list[dict], str]:
    judge = case["judge"]
    rc, stdout, stderr, assertion_input, judge_output = _run_bound_judge_command(
        case, judge, output_path, temp_dir, primary_output, evidence_path, cwd
    )
    if rc != 0 or not judge_output.exists():
        return [_judge_command_failure(rc, stdout, stderr)], "fail"
    judge_text = judge_output.read_text(encoding="utf-8")
    if not judge_text.strip():
        return [_empty_judge_output_failure()], "fail"
    result_status, results = _parse_judge_output(judge_text)
    evidence = _judge_evidence(assertion_input, primary_output, evidence_path)
    checks: list[dict] = []
    _append_judge_result_checks(checks, case, judge_text, result_status, results, evidence)
    paths = {"output": output_path, "judge_output": judge_output, "assertion_input": assertion_input, "evidence": evidence_path, "primary": primary_output}
    if result_status == "pass":
        _append_verify_command(checks, case, judge, paths, cwd)
    return checks, result_status


def _run_llm_judge_case(case: dict, output_path: Path, cwd: Path) -> list[dict]:
    checks: list[dict] = []
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        evidence_path = temp_dir / "judge-evidence.json"
        primary_output, setup_result = _prepare_llm_primary_output(case, cwd, temp_dir, checks)
        if primary_output is None:
            return checks
        shutil.copyfile(primary_output, output_path)
        _write_judge_evidence(case, _input_path(case), primary_output, evidence_path, setup_result)
        assertion_checks, _ = _run_judge_assertion_phase(case, output_path, cwd, temp_dir, primary_output, evidence_path)
        checks.extend(assertion_checks)
        return checks

def _case_output_path(temp_dir: Path, case: dict) -> Path:
    output_suffix = ".json" if (case.get("expected") or "").endswith(".json") else ".out"
    return temp_dir / f"{case.get('__artifact_slug', 'output')}{output_suffix}"


def _run_command_case(case: dict, skill_dir: Path, output_path: Path) -> tuple[str, list[dict]]:
    run = case["run"]
    try:
        cmd = _bind_placeholders(run["command"], input_path=_input_path(case), output_path=output_path, expected_path=_expected_path(case))
        rc, stdout, stderr = _run_shell(cmd, skill_dir, int(run.get("timeout_sec") or DEFAULT_TIMEOUT))
    except ValueError as exc:
        rc, stdout, stderr = 1, "", str(exc)
    if rc == 0 and output_path.exists():
        return "pass", []
    return "fail", [{
        "id": "run.command",
        "title": "case run.command 실행",
        "type": "run",
        "status": "fail",
        "exit_code": rc,
        "stdout": stdout[-2000:],
        "stderr": stderr[-2000:],
    }]


def _run_case_body(case: dict, skill_dir: Path, output_path: Path) -> tuple[str, list[dict]]:
    if case.get("type") == "llm-judge":
        checks = _run_llm_judge_case(case, output_path, skill_dir)
        return "pass", checks
    return _run_command_case(case, skill_dir, output_path)


def _append_post_run_checks(checks: list[dict], case: dict, output_path: Path, skill_dir: Path, promote: bool, run_status: str) -> None:
    if run_status == "pass" and not promote:
        expected_check = _compare_expected(case, output_path)
        if expected_check:
            checks.append(expected_check)
    if run_status != "pass":
        return
    for assertion in case.get("assertions", []):
        if assertion["type"] == "command":
            checks.append(_run_command_assertion(assertion, case, output_path, skill_dir))


def _promote_case_output(case: dict, output_path: Path, promote: bool, failed: bool, run_status: str) -> str | None:
    if not promote or failed or run_status != "pass":
        return None
    dest = _promote_path(case, output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(output_path, dest)
    return str(dest)


def _case_result(case: dict, checks: list[dict], promoted: str | None, run_status: str) -> dict:
    failed = any(c["status"] != "pass" for c in checks)
    return {
        "id": case["id"],
        "case_group_id": case.get("__case_group_id", case["id"]),
        "artifact_slug": case.get("__artifact_slug"),
        "type": case["type"],
        "title": case.get("title", case["id"]),
        "status": "fail" if failed or run_status == "fail" else "pass",
        "checks": checks,
        "promoted": promoted,
    }


def run_case(case: dict, skill_dir: Path, promote: bool = False) -> dict:
    with tempfile.TemporaryDirectory() as td:
        output_path = _case_output_path(Path(td), case)
        run_status, checks = _run_case_body(case, skill_dir, output_path)
        _append_post_run_checks(checks, case, output_path, skill_dir, promote, run_status)
        failed = any(c["status"] != "pass" for c in checks)
        promoted = _promote_case_output(case, output_path, promote, failed, run_status)
        return _case_result(case, checks, promoted, run_status)

def run_suite(spec: dict, skill_dir: Path, promote: bool = False) -> dict:
    cases = load_cases(spec, skill_dir)
    case_results = [run_case(case, skill_dir, promote=promote) for case in cases]
    passed = sum(1 for c in case_results if c["status"] == "pass")
    failed = sum(1 for c in case_results if c["status"] != "pass")
    return {"skill": spec.get("skill"), "title": spec.get("title"), "passed": passed, "failed": failed, "cases": case_results}


def _default_skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a skill's case-based eval suite.")
    parser.add_argument("skill_dir", nargs="?", default=None, help="Skill root (default: parent of scripts/).")
    parser.add_argument("--validate", action="store_true", help="Only validate eval.yaml and declared case.yaml files.")
    parser.add_argument("--promote", action="store_true", help="Create or overwrite expected files for passing cases.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser


def _print_error(message: str, as_json: bool) -> None:
    print(json.dumps({"error": message}) if as_json else f"ERROR: {message}", file=sys.stderr)


def _load_suite(skill_dir: Path, as_json: bool) -> tuple[Path | None, dict | None, int]:
    spec_path = find_spec(skill_dir)
    if spec_path is None:
        _print_error(f"no evals/*.eval.yaml found under {skill_dir}", as_json)
        return None, None, 2
    try:
        return spec_path, parse_spec(spec_path), 0
    except ValueError as exc:
        _print_error(str(exc), as_json)
        return spec_path, None, 1


def _handle_validate(spec_path: Path, errors: list[str], as_json: bool) -> int:
    if as_json:
        print(json.dumps({"valid": not errors, "errors": errors}, indent=2, ensure_ascii=False))
    elif errors:
        print(f"INVALID {spec_path.name}:")
        for err in errors:
            print(f"  - {err}")
    else:
        print(f"VALID {spec_path.name}")
    return 1 if errors else 0


def _print_suite_result(result: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    for case in result["cases"]:
        print(f"[{case['status']}] {case['id']} — {case['title']}")
        for check in case["checks"]:
            print(f"  [{check['status']}] {check['id']} — {check['title']}")
        if case.get("promoted"):
            print(f"  promoted: {case['promoted']}")
    print(f"\nsummary: {result['passed']} passed, {result['failed']} failed")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    skill_dir = Path(args.skill_dir).resolve() if args.skill_dir else _default_skill_dir()
    spec_path, spec, load_exit = _load_suite(skill_dir, args.json)
    if load_exit:
        return load_exit
    errors = validate_spec(spec, skill_dir)
    if args.validate:
        return _handle_validate(spec_path, errors, args.json)
    if errors:
        message = json.dumps({"error": "eval suite is malformed", "errors": errors}, ensure_ascii=False)
        print(message if args.json else "ERROR: eval suite is malformed; run --validate", file=sys.stderr)
        return 1
    result = run_suite(spec, skill_dir, promote=args.promote)
    _print_suite_result(result, args.json)
    return 1 if result["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
