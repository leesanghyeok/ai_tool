#!/usr/bin/env python3
"""
Case-based eval runner shipped inside generated skills as scripts/run_evals.py.

Spec model:
  evals/<skill>.eval.yaml          # suite manifest + human-readable case map
  evals/cases/<case-id>/case.yaml  # independent test case definition

The suite manifest is the source of truth: only cases listed in eval.yaml run.
Case directories that exist on disk but are not declared are validation errors.

Each case owns its own run command and assertions. There are no global
assertions and no top-level run command. Supported assertion types are:
  - command: shell command exits 0
  - llm-judge: subprocess judge command returns structured JSON verdicts

Expected handling is automatic: when a case declares `expected`, produced output
is byte-compared to that file unless --promote is set. With --promote, passing
case output creates or overwrites the expected file.

Usage:
  python3 scripts/run_evals.py [skill_dir] [--validate] [--promote] [--json]

Exit codes:
  0 - valid / all selected suite cases passed
  1 - malformed spec, failed command, failed judge, or failed expected compare
  2 - eval suite not found
"""

from __future__ import annotations

import argparse
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
VALID_JUDGE_METHODS = ("aggregate", "subagent")
DEFAULT_TIMEOUT = 120
INPUT_PLACEHOLDER = "{input}"
OUTPUT_PLACEHOLDER = "{output}"
EXPECTED_PLACEHOLDER = "{expected}"
JUDGE_PACKET_PLACEHOLDER = "{judge_packet}"
JUDGE_OUTPUT_PLACEHOLDER = "{judge_output}"


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


def _logical_lines(text: str) -> list[tuple[int, str]]:
    raw = text.splitlines()
    out: list[tuple[int, str]] = []
    i = 0
    while i < len(raw):
        stripped_comment = _strip_comment(raw[i])
        if not stripped_comment.strip():
            i += 1
            continue
        indent = len(stripped_comment) - len(stripped_comment.lstrip(" "))
        content = stripped_comment.strip()
        if content.endswith(": |") or content.endswith(": >") or content in ("|", ">"):
            if content in ("|", ">"):
                key_prefix = content
            else:
                key_prefix = content[:-2].rstrip() + ":"
            block_indent = None
            block_lines: list[str] = []
            i += 1
            while i < len(raw):
                nxt = raw[i]
                if not nxt.strip():
                    block_lines.append("")
                    i += 1
                    continue
                nindent = len(nxt) - len(nxt.lstrip(" "))
                if nindent <= indent:
                    break
                if block_indent is None:
                    block_indent = nindent
                block_lines.append(nxt[block_indent:])
                i += 1
            joined = "\n".join(block_lines).rstrip("\n")
            out.append((indent, f"{key_prefix} {json.dumps(joined, ensure_ascii=False)}"))
            continue
        out.append((indent, content))
        i += 1
    return out


def parse_yaml_subset(path: Path) -> Any:
    """Parse the small YAML subset used by eval.yaml/case.yaml.

    Supports nested mappings, lists of mappings/scalars, quoted/unquoted scalars,
    ints/bools/null, inline JSON arrays/objects, and literal/folded blocks.
    It is intentionally not a general YAML parser; generated specs should stay in
    this constrained shape to avoid a PyYAML dependency in generated skills.
    """
    lines = _logical_lines(path.read_text(encoding="utf-8"))
    if not lines:
        return {}

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(lines):
            return {}, index
        if lines[index][0] < indent:
            return {}, index
        is_list = lines[index][1].startswith("- ")
        if is_list:
            arr: list[Any] = []
            while index < len(lines) and lines[index][0] == indent and lines[index][1].startswith("- "):
                item_text = lines[index][1][2:].strip()
                index += 1
                if not item_text:
                    val, index = parse_block(index, indent + 2)
                    arr.append(val)
                    continue
                if ":" in item_text:
                    key, raw_val = item_text.split(":", 1)
                    item: dict[str, Any] = {}
                    if raw_val.strip():
                        item[key.strip()] = _parse_scalar(raw_val)
                    else:
                        val, index = parse_block(index, indent + 2)
                        item[key.strip()] = val
                    while index < len(lines) and lines[index][0] > indent:
                        child_indent, child_text = lines[index]
                        if child_indent < indent + 2:
                            break
                        if child_text.startswith("- "):
                            break
                        ckey, cval, index = parse_key_value(index, child_indent)
                        item[ckey] = cval
                    arr.append(item)
                else:
                    arr.append(_parse_scalar(item_text))
            return arr, index

        mapping: dict[str, Any] = {}
        while index < len(lines) and lines[index][0] == indent and not lines[index][1].startswith("- "):
            key, val, index = parse_key_value(index, indent)
            mapping[key] = val
        return mapping, index

    def parse_key_value(index: int, indent: int) -> tuple[str, Any, int]:
        cur_indent, text = lines[index]
        if cur_indent != indent:
            raise SimpleYamlError(f"{path}: unexpected indent at logical line {index + 1}")
        if ":" not in text:
            raise SimpleYamlError(f"{path}: expected key: value at logical line {index + 1}")
        key, raw_val = text.split(":", 1)
        key = key.strip()
        raw_val = raw_val.strip()
        index += 1
        if raw_val:
            return key, _parse_scalar(raw_val), index
        if index < len(lines) and lines[index][0] > indent:
            val, index = parse_block(index, lines[index][0])
            return key, val, index
        return key, None, index

    parsed, end = parse_block(0, lines[0][0])
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


def load_cases(spec: dict, skill_dir: Path) -> list[dict]:
    cases: list[dict] = []
    for entry in spec.get("cases", []) or []:
        path = _case_path(skill_dir, entry)
        case = parse_yaml_subset(path)
        if not isinstance(case, dict):
            raise ValueError(f"{path}: case spec must be a mapping")
        case["__path"] = str(path)
        case["__dir"] = str(path.parent)
        cases.append(case)
    return cases


def validate_spec(spec: dict, skill_dir: Path) -> list[str]:
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

    case_entries = spec.get("cases")
    if not isinstance(case_entries, list) or not case_entries:
        errors.append("eval.yaml: 'cases' must be a non-empty list")
        case_entries = []

    declared_paths: set[Path] = set()
    declared_ids: set[str] = set()
    for i, entry in enumerate(case_entries):
        where = f"eval.yaml cases[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{where}: must be a mapping")
            continue
        for field in ("id", "type", "title", "path"):
            if not entry.get(field):
                errors.append(f"{where}: missing '{field}'")
        if entry.get("type") and entry["type"] not in VALID_CASE_TYPES:
            errors.append(f"{where}: unsupported type {entry['type']!r}")
        entry_id = entry.get("id")
        if isinstance(entry_id, str) and entry_id in declared_ids:
            errors.append(f"{where}: duplicate id {entry['id']!r}")
        if isinstance(entry_id, str):
            declared_ids.add(entry_id)
        if entry.get("path"):
            cpath = _case_path(skill_dir, entry)
            declared_paths.add(cpath)
            if not cpath.exists():
                errors.append(f"{where}: case file not found: {entry['path']}")
                continue
            try:
                case = parse_yaml_subset(cpath)
            except Exception as exc:
                errors.append(f"{where}: malformed case yaml: {exc}")
                continue
            errors.extend(validate_case(case, cpath, entry))

    cases_dir = skill_dir / "evals" / "cases"
    if cases_dir.is_dir():
        for case_file in sorted(cases_dir.glob("*/case.yaml")):
            if case_file.resolve() not in declared_paths:
                errors.append(f"eval.yaml: undeclared case directory is present: {case_file.parent.name}")
    return errors


def validate_case(case: dict, cpath: Path, entry: dict) -> list[str]:
    errors: list[str] = []
    prefix = f"{cpath.relative_to(cpath.parents[2]) if len(cpath.parents) > 2 else cpath}"
    for field in ("id", "type", "title"):
        if not case.get(field):
            errors.append(f"{prefix}: missing '{field}'")
    if case.get("id") != entry.get("id"):
        errors.append(f"{prefix}: id does not match eval.yaml entry")
    if case.get("type") != entry.get("type"):
        errors.append(f"{prefix}: type does not match eval.yaml entry")
    if case.get("title") != entry.get("title"):
        errors.append(f"{prefix}: title does not match eval.yaml entry")

    ctype = case.get("type")
    run = case.get("run")
    if ctype == "llm-judge":
        if run is not None:
            errors.append(f"{prefix}: type 'llm-judge' must not define run.command; use llm-judge judge.command")
    else:
        if not isinstance(run, dict) or not run.get("command"):
            errors.append(f"{prefix}: non-llm-judge case must define run.command")
        elif OUTPUT_PLACEHOLDER not in run["command"]:
            errors.append(f"{prefix}: run.command must contain {OUTPUT_PLACEHOLDER}")

    if case.get("input") and not (cpath.parent / case["input"]).exists():
        errors.append(f"{prefix}: input file not found: {case['input']}")
    if case.get("expected") and not (cpath.parent / case["expected"]).exists():
        errors.append(f"{prefix}: expected file not found: {case['expected']}")

    assertions = case.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        errors.append(f"{prefix}: assertions must be a non-empty list")
        assertions = []
    for i, assertion in enumerate(assertions):
        awhere = f"{prefix} assertions[{i}]"
        if not isinstance(assertion, dict):
            errors.append(f"{awhere}: must be a mapping")
            continue
        for field in ("id", "title", "type"):
            if not assertion.get(field):
                errors.append(f"{awhere}: missing '{field}'")
        atype = assertion.get("type")
        if atype not in VALID_ASSERTION_TYPES:
            errors.append(f"{awhere}: type must be one of {VALID_ASSERTION_TYPES}, got {atype!r}")
        if atype == "command" and not assertion.get("cmd"):
            errors.append(f"{awhere}: command assertion needs 'cmd'")
        if atype == "llm-judge":
            judge = assertion.get("judge")
            if not isinstance(judge, dict):
                errors.append(f"{awhere}: llm-judge assertion needs 'judge' mapping")
            else:
                if judge.get("method") not in VALID_JUDGE_METHODS:
                    errors.append(f"{awhere}: judge.method must be one of {VALID_JUDGE_METHODS}")
                command = judge.get("command")
                if not command:
                    errors.append(f"{awhere}: judge.command is required")
                elif JUDGE_PACKET_PLACEHOLDER not in command or JUDGE_OUTPUT_PLACEHOLDER not in command:
                    errors.append(
                        f"{awhere}: judge.command must contain {JUDGE_PACKET_PLACEHOLDER} and {JUDGE_OUTPUT_PLACEHOLDER}"
                    )
            checks = assertion.get("checks")
            if not isinstance(checks, list) or not checks:
                errors.append(f"{awhere}: llm-judge assertion needs non-empty 'checks' list")
            else:
                for j, check in enumerate(checks):
                    cwhere = f"{awhere} checks[{j}]"
                    if not isinstance(check, dict):
                        errors.append(f"{cwhere}: must be a mapping")
                        continue
                    for field in ("id", "title", "prompt"):
                        if not check.get(field):
                            errors.append(f"{cwhere}: missing '{field}'")
    return errors


def _bind_placeholders(cmd: str, *, input_path: Path | None, output_path: Path | None,
                       expected_path: Path | None, judge_packet: Path | None = None,
                       judge_output: Path | None = None) -> str:
    replacements = {
        INPUT_PLACEHOLDER: input_path,
        OUTPUT_PLACEHOLDER: output_path,
        EXPECTED_PLACEHOLDER: expected_path,
        JUDGE_PACKET_PLACEHOLDER: judge_packet,
        JUDGE_OUTPUT_PLACEHOLDER: judge_output,
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


def _judge_packet(case: dict, assertion: dict, output_path: Path) -> dict:
    packet = {
        "case": {"id": case["id"], "type": case["type"], "title": case["title"]},
        "assertion": {"id": assertion["id"], "title": assertion["title"]},
        "method": assertion["judge"]["method"],
        "input_path": str(_input_path(case)) if _input_path(case) else None,
        "output_path": str(output_path),
        "expected_path": str(_expected_path(case)) if _expected_path(case) else None,
        "checks": assertion["checks"],
        "required_response_schema": {
            "verdict": "pass|fail",
            "checks": [{"id": "string", "verdict": "pass|fail", "evidence": ["string"], "reason": "string"}],
        },
    }
    return packet


def _validate_judge_result(result: Any, assertion: dict) -> tuple[bool, str]:
    if not isinstance(result, dict):
        return False, "judge result must be a JSON object"
    if result.get("verdict") not in ("pass", "fail"):
        return False, "judge result verdict must be pass or fail"
    checks = result.get("checks")
    if not isinstance(checks, list):
        return False, "judge result checks must be a list"
    expected_ids = {c["id"] for c in assertion.get("checks", [])}
    seen: set[str] = set()
    for check in checks:
        if not isinstance(check, dict):
            return False, "each judge check result must be an object"
        cid = check.get("id")
        if cid not in expected_ids:
            return False, f"unknown judge check id: {cid}"
        if isinstance(cid, str):
            seen.add(cid)
        if check.get("verdict") not in ("pass", "fail"):
            return False, f"judge check {cid} verdict must be pass or fail"
        if not check.get("evidence"):
            return False, f"judge check {cid} must include evidence"
    missing = expected_ids - seen
    if missing:
        return False, f"judge result missing checks: {', '.join(sorted(missing))}"
    return True, ""


def _run_llm_judge_assertion(assertion: dict, case: dict, output_path: Path, cwd: Path) -> dict:
    judge = assertion["judge"]
    with tempfile.TemporaryDirectory() as td:
        packet_path = Path(td) / "judge-packet.json"
        judge_output = Path(td) / "judge-output.json"
        packet_path.write_text(json.dumps(_judge_packet(case, assertion, output_path), indent=2, ensure_ascii=False), encoding="utf-8")
        cmd = _bind_placeholders(
            judge["command"],
            input_path=_input_path(case),
            output_path=output_path,
            expected_path=_expected_path(case),
            judge_packet=packet_path,
            judge_output=judge_output,
        )
        rc, stdout, stderr = _run_shell(cmd, cwd, int(judge.get("timeout_sec") or DEFAULT_TIMEOUT))
        if rc != 0 or not judge_output.exists():
            return {
                "id": assertion["id"], "title": assertion["title"], "type": "llm-judge",
                "status": "fail", "exit_code": rc, "stdout": stdout[-2000:], "stderr": stderr[-2000:],
                "error": "judge command failed or did not create judge_output",
            }
        try:
            result = json.loads(judge_output.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return {"id": assertion["id"], "title": assertion["title"], "type": "llm-judge", "status": "fail", "error": f"judge output is not JSON: {exc}"}
        valid, error = _validate_judge_result(result, assertion)
        if not valid:
            return {"id": assertion["id"], "title": assertion["title"], "type": "llm-judge", "status": "fail", "error": error, "judge_result": result}
        return {"id": assertion["id"], "title": assertion["title"], "type": "llm-judge", "status": "pass" if result["verdict"] == "pass" else "fail", "judge_result": result}


def run_case(case: dict, skill_dir: Path, promote: bool = False) -> dict:
    output_suffix = ".json" if (case.get("expected") or "").endswith(".json") else ".out"
    with tempfile.TemporaryDirectory() as td:
        output_path = Path(td) / f"output{output_suffix}"
        checks: list[dict] = []
        run_status = "pass"
        if case.get("type") == "llm-judge":
            # Judge-only cases evaluate input directly unless assertions create their own output.
            inp = _input_path(case)
            if inp is not None:
                shutil.copyfile(inp, output_path)
            else:
                output_path.write_text("", encoding="utf-8")
        else:
            run = case["run"]
            try:
                cmd = _bind_placeholders(run["command"], input_path=_input_path(case), output_path=output_path, expected_path=_expected_path(case))
                rc, stdout, stderr = _run_shell(cmd, skill_dir, int(run.get("timeout_sec") or DEFAULT_TIMEOUT))
            except ValueError as exc:
                rc, stdout, stderr = 1, "", str(exc)
            if rc != 0 or not output_path.exists():
                run_status = "fail"
                checks.append({"id": "run.command", "title": "case run.command 실행", "type": "run", "status": "fail", "exit_code": rc, "stdout": stdout[-2000:], "stderr": stderr[-2000:]})

        if run_status == "pass" and not promote:
            expected_check = _compare_expected(case, output_path)
            if expected_check:
                checks.append(expected_check)

        if run_status == "pass":
            for assertion in case.get("assertions", []):
                if assertion["type"] == "command":
                    checks.append(_run_command_assertion(assertion, case, output_path, skill_dir))
                elif assertion["type"] == "llm-judge":
                    checks.append(_run_llm_judge_assertion(assertion, case, output_path, skill_dir))

        failed = any(c["status"] != "pass" for c in checks)
        promoted = None
        if promote and not failed and run_status == "pass":
            dest = _promote_path(case, output_path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(output_path, dest)
            promoted = str(dest)

        return {
            "id": case["id"],
            "type": case["type"],
            "title": case["title"],
            "status": "fail" if failed or run_status == "fail" else "pass",
            "checks": checks,
            "promoted": promoted,
        }


def run_suite(spec: dict, skill_dir: Path, promote: bool = False) -> dict:
    cases = load_cases(spec, skill_dir)
    case_results = [run_case(case, skill_dir, promote=promote) for case in cases]
    passed = sum(1 for c in case_results if c["status"] == "pass")
    failed = sum(1 for c in case_results if c["status"] != "pass")
    return {"skill": spec.get("skill"), "title": spec.get("title"), "passed": passed, "failed": failed, "cases": case_results}


def _default_skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a skill's case-based eval suite.")
    parser.add_argument("skill_dir", nargs="?", default=None, help="Skill root (default: parent of scripts/).")
    parser.add_argument("--validate", action="store_true", help="Only validate eval.yaml and declared case.yaml files.")
    parser.add_argument("--promote", action="store_true", help="Create or overwrite expected files for passing cases.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    skill_dir = Path(args.skill_dir).resolve() if args.skill_dir else _default_skill_dir()
    spec_path = find_spec(skill_dir)
    if spec_path is None:
        msg = f"no evals/*.eval.yaml found under {skill_dir}"
        print(json.dumps({"error": msg}) if args.json else f"ERROR: {msg}", file=sys.stderr)
        return 2
    try:
        spec = parse_spec(spec_path)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}) if args.json else f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors = validate_spec(spec, skill_dir)
    if args.validate:
        if args.json:
            print(json.dumps({"valid": not errors, "errors": errors}, indent=2, ensure_ascii=False))
        elif errors:
            print(f"INVALID {spec_path.name}:")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"VALID {spec_path.name}")
        return 1 if errors else 0
    if errors:
        print(json.dumps({"error": "eval suite is malformed", "errors": errors}, ensure_ascii=False) if args.json else "ERROR: eval suite is malformed; run --validate", file=sys.stderr)
        return 1

    result = run_suite(spec, skill_dir, promote=args.promote)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for case in result["cases"]:
            print(f"[{case['status']}] {case['id']} — {case['title']}")
            for check in case["checks"]:
                print(f"  [{check['status']}] {check['id']} — {check['title']}")
            if case.get("promoted"):
                print(f"  promoted: {case['promoted']}")
        print(f"\nsummary: {result['passed']} passed, {result['failed']} failed")
    return 1 if result["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
