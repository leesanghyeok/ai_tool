#!/usr/bin/env python3
"""skill-creator-for-stark scenario eval을 위한 deterministic pipeline entrypoint.

This script intentionally renders only file-specific template bindings supplied in
input JSON. It does not interpret user intent, call external services, promote
expected files, commit, publish, or use credentials.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
VALID_MODES = {"create", "modify", "migrate"}
ROOT = Path(__file__).resolve().parent.parent
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class PipelineError(ValueError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PipelineError(f"invalid input JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise PipelineError("input must be a JSON object")
    return data


def _require_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise PipelineError(f"missing or invalid string field: {key}")
    return value


def _resolve_under(root: Path, rel: str) -> Path:
    if not isinstance(rel, str) or not rel.strip():
        raise PipelineError("path must be a non-empty relative path")
    rel_path = Path(rel)
    if rel_path.is_absolute() or ".." in rel_path.parts:
        raise PipelineError(f"path escapes target skill directory: {rel}")
    dest = (root / rel_path).resolve()
    root_resolved = root.resolve()
    if dest != root_resolved and root_resolved not in dest.parents:
        raise PipelineError(f"path escapes target skill directory: {rel}")
    return dest


def _template_text(template: str, data: dict[str, Any], target_skill: str) -> str:
    template_path = (ROOT / template).resolve()
    if template_path.exists() and ROOT in template_path.parents:
        text = template_path.read_text(encoding="utf-8")
    else:
        text = _builtin_template(template, data, target_skill)
    return _render(text, data, target_skill)


def _default_render_values(data: dict[str, Any], target_skill: str) -> dict[str, str]:
    values = {k: _stringify(v) for k, v in data.items()}
    values.setdefault("skill_name", target_skill)
    values.setdefault("description", f"{target_skill} 테스트용 스킬")
    values.setdefault("skill_goal", f"{target_skill} workflow 검증")
    values.setdefault("skill_title", target_skill.replace("-", " "))
    values.setdefault("change_summary", "승인된 범위의 최소 변경")
    return values


def _placeholder_replacements(data: dict[str, Any], values: dict[str, str]) -> dict[str, str]:
    return {
        "<skill-name>": values["skill_name"],
        "<언제 이 스킬을 사용할지 한 문장으로 설명>": values["description"],
        "<스킬 제목>": values["skill_title"],
        "<스킬의 목적, 직접 산출물, 성공 기준을 짧게 설명한다.>": values["skill_goal"],
        "<이 스킬을 사용해야 하는 trigger condition>": _bullet_text(data.get("trigger_conditions")) or "사용자가 이 스킬의 목적에 맞는 작업을 요청한다.",
        "<현실적인 사용자 요청 예시 또는 상황>": values["skill_goal"],
        "<non-goal, near-miss, 더 적합한 다른 스킬>": "credential 사용, external publish, commit/push는 별도 승인 전에는 하지 않는다.",
        "<키워드는 비슷하지만 이 스킬을 쓰면 안 되는 경우>": "단순 일회성 문장 수정처럼 재사용 workflow가 필요 없는 경우.",
        "<없으면 workflow를 시작할 수 없는 핵심 입력과 그 이유를 설명한다.>": "작업 목표와 source 범위가 없으면 산출물과 검증 기준을 정할 수 없다.",
        "<사용자가 바꾸면 산출물/검증/안전 경계가 어떻게 달라지는지 설명한다.>": "승인 범위가 달라지면 파일 write, external action, 검증 범위가 달라진다.",
        "<explicit-default>": "명시 승인 범위",
        "<완료 판단이나 검증에 반드시 필요한 산출물이다.>": "생성 또는 수정된 파일과 read-back 검증 결과다.",
        "<없을 수 있는 산출물과 없을 때 보고할 값이다.>": "지원 파일이 없으면 빈 배열로 보고한다.",
        "<command 또는 권한>": "filesystem read/write 권한",
        "<없으면 어떤 단계가 실패하거나 중단되는지 설명한다.>": "대상 파일을 읽거나 쓸 수 없으면 workflow를 중단한다.",
        "<산출물 불변 조건 또는 안전 조건>": "source에 없는 API, credential, publish step을 invented fact로 만들지 않는다.",
        "<evidence/idempotency/validation 같은 완료 전 필수 조건>": "완료 전 파일 read-back과 deterministic 검증 command를 실행한다.",
    }


def _workflow_replacements() -> dict[str, str]:
    return {
        "<필수 입력, 권한, source, 승인, 검증 전제가 없어 중단해야 하는 조건>": (
            "승인되지 않은 destructive overwrite, credential 사용, external publish가 필요하면 중단한다."
        ),
        "<필수 입력과 승인 범위를 확인한다.>": "필수 입력과 승인 범위를 확인한다.",
        "<source나 기존 state를 read-only로 확인한다.>": "source와 기존 파일을 read-only로 확인한다.",
        "<산출물을 만들거나 수정한다.>": "승인된 파일만 생성 또는 수정한다.",
        "<deterministic 검증 또는 read-back을 실행한다.>": "read-back, JSON parse, eval validate 같은 deterministic 검증을 실행한다.",
        (
            "<필요하면 `evals/<skill-name>.eval.yaml`, declared `evals/<case-id>/case.yaml`, "
            "`scripts/run_evals.py`를 생성하고 `--validate`를 실행한다.>"
        ): "필요하면 eval suite를 생성하고 `uv run python scripts/run_evals.py --validate`를 실행한다.",
        "<상태, 파일, 검증 결과, 미확인 항목을 보고한다.>": "상태, 파일, 검증 결과, 미확인 항목을 보고한다.",
        "<독립 조사, 초안, 검토, fixture 작성 등>": "독립 조사, fixture 초안, 문서 검토.",
        "<승인 확인, 최종 write, 최종 검증 등>": "승인 확인, 최종 write, 최종 검증.",
        "<subagent self-report가 아니라 파일/read-back/test 결과로 확인한다.>": "subagent self-report가 아니라 파일 read-back과 test output으로 확인한다.",
        "<스킬별 commit 주의사항>": "commit/push는 별도 요청 전에는 하지 않는다.",
    }


def _apply_replacements(text: str, replacements: dict[str, str]) -> str:
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _apply_value_replacements(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
        text = text.replace("<" + key + ">", value)
    return text


def _ensure_feedback_and_contract_text(text: str) -> str:
    if "feedback/" not in text:
        text += "\n## 피드백 로깅 (Feedback Logging)\n\n- 불만족 사건은 `feedback/` 아래 raw Markdown으로 남기고, 중복 검사와 read-back 검증을 수행한다.\n"
    if "INPUT_" not in text:
        text += "\n- `INPUT_SCOPE`와 `OUTPUT_VERIFICATION`은 검증 보고에 사용한다.\n"
    return text


def _render(text: str, data: dict[str, Any], target_skill: str) -> str:
    values = _default_render_values(data, target_skill)
    text = _apply_replacements(text, _placeholder_replacements(data, values))
    text = _apply_replacements(text, _workflow_replacements())
    text = _apply_value_replacements(text, values)
    return _ensure_feedback_and_contract_text(text).rstrip() + "\n"

def _stringify(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _bullet_text(value: Any) -> str:
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value)
    if isinstance(value, str):
        return value
    return ""


def _builtin_template(template: str, data: dict[str, Any], target_skill: str) -> str:
    name = Path(template).name
    if name == "reference.template.md":
        return _reference_template(data)
    if name == "output.template.md":
        return "# {{output_kind}} output template\n\n- 상태: completed | partial | blocked | unverified\n- 근거: <read-back/test output>\n"
    if name == "case.template.yaml":
        return _case_template(data)
    if name == "run_pipeline.py.template":
        return _runner_template()
    if name == "run_evals.py.template":
        source = ROOT / "scripts" / "run_evals_template.py"
        if source.exists():
            return source.read_text(encoding="utf-8")
        return "#!/usr/bin/env python3\nprint('run_evals placeholder')\n"
    if name == "feedback-log.template.md":
        source = ROOT / "templates" / "feedback-log.template.md"
        if source.exists():
            return source.read_text(encoding="utf-8")
        return "# Feedback log\n\n- raw feedback markdown\n"
    raise PipelineError(f"template file not found: {template}")


def _reference_template(data: dict[str, Any]) -> str:
    raw_rules = data.get("rules")
    rules = raw_rules if isinstance(raw_rules, list) else ["source에 없는 API/path를 만들지 않는다"]
    body = "\n".join(f"- {rule}" for rule in rules)
    return f"# Reference\n\n{body}\n"


def _case_template(data: dict[str, Any]) -> str:
    case_id = data.get("case_id", "basic")
    case_type = data.get("case_type", "happy-path")
    return (
        f"id: {case_id}\n"
        f"type: {case_type}\n\n"
        "cases:\n"
        f"  - id: {case_id}\n"
        "    run:\n"
        "      command: {python} scripts/run_pipeline.py --input {input} --output {output}\n"
        "      timeout_sec: 120\n"
        "    assertions:\n"
        "      - id: output-created\n"
        "        title: 출력 파일 생성 여부 검증\n"
        "        type: command\n"
        "        cmd: test -s {output}\n"
    )


def _runner_template() -> str:
    return (
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "import argparse, json\n"
        "ap=argparse.ArgumentParser(); ap.add_argument('--input'); "
        "ap.add_argument('--output', required=True)\n"
        "a=ap.parse_args(); "
        "Path(a.output).write_text(json.dumps({'status':'success'}, ensure_ascii=False)+'\\n', "
        "encoding='utf-8')\n"
    )


def _validate_input(data: dict[str, Any]) -> tuple[str, Path, str, list[dict[str, Any]]]:
    if data.get("schema_version") != SCHEMA_VERSION:
        raise PipelineError("schema_version must be 1")
    mode = _require_string(data, "mode")
    if mode not in VALID_MODES:
        raise PipelineError(f"unsupported mode: {mode}")
    skill_root, skill_name = _validate_target(data.get("target"))
    template_inputs = _validate_template_inputs(data.get("template_inputs"))
    return mode, skill_root, skill_name, template_inputs


def _validate_target(target: Any) -> tuple[Path, str]:
    if not isinstance(target, dict):
        raise PipelineError("target must be an object")
    skill_name = _require_string(target, "skill_name")
    if not SLUG_RE.fullmatch(skill_name):
        raise PipelineError(f"skill_name is not lowercase hyphen slug: {skill_name}")
    skill_root = Path(_require_string(target, "skill_root")).expanduser().resolve()
    if not skill_root.is_absolute():
        raise PipelineError("skill_root must resolve to an absolute path")
    return skill_root, skill_name


def _validate_template_inputs(template_inputs: Any) -> list[dict[str, Any]]:
    if not isinstance(template_inputs, list) or not template_inputs:
        raise PipelineError("template_inputs must be a non-empty list")
    for item in template_inputs:
        _validate_template_input_item(item)
    return template_inputs


def _validate_template_input_item(item: Any) -> None:
    if not isinstance(item, dict):
        raise PipelineError("template_inputs items must be objects")
    _require_string(item, "path")
    _require_string(item, "template")
    if not isinstance(item.get("data"), dict):
        raise PipelineError("template_inputs[].data must be an object")


def _initial_result() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "failed",
        "mode": None,
        "skill_dir": "",
        "files_written": [],
        "errors": [],
        "warnings": [],
    }


def _postprocess_written_file(dest: Path, template: str) -> None:
    if dest.suffix == ".py":
        dest.chmod(0o755)
    if template == "templates/run_evals.py.template":
        template_copy = ROOT / "scripts" / "run_evals_template.py"
        if template_copy.exists():
            shutil.copyfile(template_copy, dest)
            dest.chmod(0o755)


def _write_template_item(skill_dir: Path, skill_name: str, item: dict[str, Any]) -> dict[str, str]:
    dest = _resolve_under(skill_dir, item["path"])
    rendered = _template_text(item["template"], item["data"], skill_name)
    action = "modify" if dest.exists() else "create"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(rendered, encoding="utf-8")
    _postprocess_written_file(dest, item["template"])
    return {"path": str(dest), "action": action, "source_template": item["template"]}


def _execute(input_path: Path, result: dict[str, Any]) -> None:
    data = _load_json(input_path)
    mode, skill_root, skill_name, template_inputs = _validate_input(data)
    skill_dir = (skill_root / skill_name).resolve()
    if skill_root not in skill_dir.parents and skill_dir != skill_root:
        raise PipelineError("target skill directory escapes skill_root")
    result["mode"] = mode
    result["skill_dir"] = str(skill_dir)
    skill_dir.mkdir(parents=True, exist_ok=True)
    for item in sorted(template_inputs, key=lambda i: i["path"]):
        result["files_written"].append(_write_template_item(skill_dir, skill_name, item))
    result["status"] = "success"


def _write_result(output_path: Path, result: dict[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run(input_path: Path, output_path: Path) -> int:
    result = _initial_result()
    try:
        _execute(input_path, result)
    except Exception as exc:  # noqa: BLE001 - write structured failure for eval read-back.
        result["errors"].append(str(exc))
    _write_result(output_path, result)
    return 0 if result["status"] == "success" else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render skill package files from a deterministic input JSON.")
    parser.add_argument("--input", required=True, help="pipeline input JSON path")
    parser.add_argument("--output", required=True, help="pipeline output JSON path")
    args = parser.parse_args(argv)
    return run(Path(args.input), Path(args.output))


if __name__ == "__main__":
    raise SystemExit(main())
