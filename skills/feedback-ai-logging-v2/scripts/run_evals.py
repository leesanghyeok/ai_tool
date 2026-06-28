#!/usr/bin/env python3
"""
생성되는 각 skill 안에 `scripts/run_evals.py`로 포함되는 eval runner다.

생성된 skill은 `evals/<skill>.eval.md`에 자기 loss function을 가진다.
구성은 shell command로 채점되는 binary check, `llm-judge` checklist,
그리고 몇 개의 golden case다. 이 runner는 그 spec을 deterministic regression gate,
형식 검증기, 그리고 spec에 `run` command가 있을 때 end-to-end rollout harness로
사용한다. 단, `llm-judge` check는 자동 채점하지 않는다. agent나
autoresearch-universal이 볼 checklist로 출력만 한다.

모드:
    python3 scripts/run_evals.py                 # golden baseline에 대해 command check 실행.
                                                 # 하나라도 실패하면 non-zero exit.
    python3 scripts/run_evals.py --validate      # spec 형식이 올바른지만 확인.
    python3 scripts/run_evals.py --output OUT [--case ID]
                                                 # 실제 produced output을 채점.
    python3 scripts/run_evals.py --rollout [--promote] [--timeout N] [--case ID]
                                                 # spec의 `run` command로 golden input마다
                                                 # skill을 실행한 뒤 produced output을 채점.
                                                 # --promote는 pending-first-green case의
                                                 # 첫 passing output을 baseline으로 저장.
    python3 scripts/run_evals.py --json          # machine-readable JSON 출력.

spec의 optional `run` field는 {input}(golden case input path)과
{output}(produced output path)을 binding하는 command template이다. 예:
    "run": "python3 scripts/run_pipeline.py --input {input} --output {output}"

Exit code:
    0 - 모든 check 통과. 또는 --validate error 없음. 또는 spec에 `run` command가 없어
        --rollout에서 실행할 것이 없음.
    1 - check 실패, rollout case error, 또는 malformed spec.
    2 - eval spec 없음.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VALID_TYPES = ("command", "llm-judge")
MIN_GOLDEN_CASES = 3
OUTPUT_PLACEHOLDER = "{output}"
INPUT_PLACEHOLDER = "{input}"
DEFAULT_ROLLOUT_TIMEOUT = 120

_JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


def find_spec(skill_dir: Path) -> Path | None:
    """skill_dir 아래 첫 번째 evals/*.eval.md를 반환한다. 없으면 None을 반환한다."""
    evals_dir = skill_dir / "evals"
    if not evals_dir.is_dir():
        return None
    specs = sorted(evals_dir.glob("*.eval.md"))
    return specs[0] if specs else None


def parse_spec(spec_path: Path) -> dict:
    """eval spec에서 첫 번째 fenced ```json block을 추출해 parse한다.

    Raises:
        ValueError: JSON block이 없거나 parse되지 않을 때.
    """
    text = spec_path.read_text(encoding="utf-8")
    match = _JSON_BLOCK.search(text)
    if not match:
        raise ValueError(f"{spec_path}: no ```json block found")
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{spec_path}: malformed JSON block: {exc}") from exc


def validate_spec(spec: dict, skill_dir: Path) -> list[str]:
    """spec 형식 error 목록을 반환한다. 빈 list면 valid라는 뜻이다."""
    errors: list[str] = []

    if not spec.get("skill"):
        errors.append("missing 'skill' name")

    # 선택 항목인 `run` command는 --rollout을 가능하게 한다. 없어도 valid하다.
    # 단, 있으면 produced output을 어디에 쓸지 알 수 있는 non-empty string이어야 한다.
    if "run" in spec:
        run_cmd = spec.get("run")
        if not isinstance(run_cmd, str) or not run_cmd.strip():
            errors.append("'run' must be a non-empty string when present")
        elif OUTPUT_PLACEHOLDER not in run_cmd:
            errors.append(f"'run' must contain the {OUTPUT_PLACEHOLDER} placeholder")

    criteria = spec.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        errors.append("'criteria' must be a non-empty list")
        criteria = []
    for i, crit in enumerate(criteria):
        where = f"criteria[{i}]"
        if not crit.get("id"):
            errors.append(f"{where}: missing 'id'")
        if not crit.get("text"):
            errors.append(f"{where}: missing 'text'")
        ctype = crit.get("type")
        if ctype not in VALID_TYPES:
            errors.append(f"{where}: 'type' must be one of {VALID_TYPES}, got {ctype!r}")
        if ctype == "command" and not crit.get("cmd"):
            errors.append(f"{where}: command criterion needs a non-empty 'cmd'")

    golden = spec.get("golden")
    if not isinstance(golden, list):
        errors.append("'golden' must be a list")
        golden = []
    if len(golden) < MIN_GOLDEN_CASES:
        errors.append(f"need at least {MIN_GOLDEN_CASES} golden cases, found {len(golden)}")
    for i, case in enumerate(golden):
        where = f"golden[{i}]"
        if not case.get("id"):
            errors.append(f"{where}: missing 'id'")
        inp = case.get("input")
        if not inp:
            errors.append(f"{where}: missing 'input'")
        elif not (skill_dir / "evals" / inp).exists():
            errors.append(f"{where}: input file not found: evals/{inp}")
        expected = case.get("expected")
        if expected is not None and not (skill_dir / "evals" / expected).exists():
            errors.append(f"{where}: expected file not found: evals/{expected}")
        if expected is None and case.get("expected_status") != "pending-first-green":
            errors.append(
                f"{where}: null 'expected' must be marked expected_status='pending-first-green'"
            )

    if golden and all(
        case.get("expected_status") == "pending-first-green" for case in golden
    ):
        print(
            "WARNING: every golden case is pending-first-green; the first rollout "
            "validates nothing until baselines are promoted with --promote",
            file=sys.stderr,
        )

    return errors


def _run_one(cmd: str, output_path: Path | None) -> bool:
    """command check 하나를 실행한다. {output}은 output_path에 binding된다.

    exit code 0이면 True를 반환한다. 실패하면 한 번 재시도한다.
    autoresearch command-eval semantics와 맞춘 동작이다.
    """
    if OUTPUT_PLACEHOLDER in cmd:
        if output_path is None:
            return False
        bound = cmd.replace(OUTPUT_PLACEHOLDER, shlex.quote(str(output_path)))
    else:
        bound = cmd
    for _ in range(2):
        proc = subprocess.run(bound, shell=True, capture_output=True)  # noqa: S602
        if proc.returncode == 0:
            return True
    return False


def run_command_checks(
    spec: dict,
    skill_dir: Path,
    output: Path | None = None,
    only_case: str | None = None,
) -> dict:
    """적용 가능한 각 golden case에 대해 모든 command criterion을 실행한다.

    기본값에서는 {output}이 각 case의 `expected` baseline file에 binding된다.
    `output` 인자가 주어지면 그 path에 binding되어 실제 run 결과를 채점한다.
    `only_case`를 사용하면 특정 case 하나만 채점한다.

    passed/failed count와 check별 detail을 담은 result dict를 반환한다.
    """
    evals_dir = skill_dir / "evals"
    command_criteria = [c for c in spec.get("criteria", []) if c.get("type") == "command"]
    results: list[dict] = []
    passed = failed = skipped = 0

    for case in spec.get("golden", []):
        case_id = case.get("id", "?")
        if only_case and case_id != only_case:
            continue
        if output is not None:
            bound_output: Path | None = output
        elif case.get("expected"):
            bound_output = evals_dir / case["expected"]
        else:
            bound_output = None  # pending-first-green: 아직 baseline이 없다.

        for crit in command_criteria:
            needs_output = OUTPUT_PLACEHOLDER in crit["cmd"]
            if needs_output and bound_output is None:
                skipped += 1
                results.append({"case": case_id, "criterion": crit["id"], "status": "skipped"})
                continue
            ok = _run_one(crit["cmd"], bound_output)
            passed += ok
            failed += not ok
            results.append(
                {"case": case_id, "criterion": crit["id"], "status": "pass" if ok else "fail"}
            )

    return {"passed": passed, "failed": failed, "skipped": skipped, "checks": results}


def _expected_baseline_path(evals_dir: Path, case: dict) -> Path:
    """promote된 baseline을 어디에 쓸지 결정한다.

    case에 `expected` path가 있으면 그 path를 사용한다. 없으면 관례적으로
    golden/<case-id>/expected.json을 사용한다.
    """
    expected = case.get("expected")
    if expected:
        return evals_dir / expected
    return evals_dir / "golden" / case.get("id", "case") / "expected.json"


def _run_skill(run_cmd: str, input_path: Path | None, output_path: Path, skill_dir: Path, timeout: int) -> bool:
    """case 하나에 대해 skill의 `run` command를 실행한다.

    {input}/{output} placeholder를 binding하고 skill root에서 실행한다.
    timeout 안에 exit code 0으로 끝날 때만 True를 반환한다. _run_one과 같은 shell
    실행 형태를 사용하고, 다른 script의 timeout 관례를 따른다.
    """
    bound = run_cmd.replace(OUTPUT_PLACEHOLDER, shlex.quote(str(output_path)))
    if INPUT_PLACEHOLDER in bound:
        if input_path is None:
            return False
        bound = bound.replace(INPUT_PLACEHOLDER, shlex.quote(str(input_path)))
    try:
        proc = subprocess.run(  # noqa: S602
            bound, shell=True, cwd=str(skill_dir), capture_output=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return False
    return proc.returncode == 0


def run_rollout(
    spec: dict,
    skill_dir: Path,
    *,
    promote: bool = False,
    only_case: str | None = None,
    timeout: int = DEFAULT_ROLLOUT_TIMEOUT,
) -> dict:
    """각 golden input으로 skill을 end-to-end 실행한 뒤 실제 output을 채점한다.

    각 golden case마다 spec의 `run` command가 temp file에 output을 만든다.
    그 output은 run_command_checks와 같은 command criteria로 채점된다.
    `promote`가 켜져 있으면 pending-first-green case 중 run과 check가 모두 통과한
    produced output을 `expected` baseline으로 저장한다.

    {passed, failed, errors, promoted, checks}를 반환한다. `errors`는 `run` command
    자체가 실패하거나 timeout된 case 수다. 그런 case의 check는 채점하지 않는다.
    """
    evals_dir = skill_dir / "evals"
    run_cmd = spec.get("run")
    passed = failed = errors = 0
    promoted: list[str] = []
    checks: list[dict] = []

    for case in spec.get("golden", []):
        case_id = case.get("id", "?")
        if only_case and case_id != only_case:
            continue

        inp = case.get("input")
        input_path = (evals_dir / inp) if inp else None

        with tempfile.TemporaryDirectory() as td:
            produced = Path(td) / "output"
            ok = _run_skill(run_cmd, input_path, produced, skill_dir, timeout)
            if not ok or not produced.exists():
                errors += 1
                checks.append({"case": case_id, "criterion": "<run>", "status": "error"})
                continue

            scored = run_command_checks(spec, skill_dir, output=produced, only_case=case_id)
            passed += scored["passed"]
            failed += scored["failed"]
            checks.extend(scored["checks"])

            is_pending = case.get("expected") is None and (
                case.get("expected_status") == "pending-first-green"
            )
            if promote and is_pending and scored["failed"] == 0 and scored["passed"] > 0:
                dest = _expected_baseline_path(evals_dir, case)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(produced, dest)
                promoted.append(case_id)

    return {
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "promoted": promoted,
        "checks": checks,
    }


def llm_judge_criteria(spec: dict) -> list[dict]:
    """LLM judge가 필요한 criteria를 반환한다. 이 script는 이를 실행하지 않는다."""
    return [c for c in spec.get("criteria", []) if c.get("type") == "llm-judge"]


def _default_skill_dir() -> Path:
    """이 파일이 있는 scripts/ directory의 parent를 skill root로 본다."""
    return Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="skill에 포함된 eval spec을 실행한다.")
    parser.add_argument(
        "skill_dir",
        nargs="?",
        default=None,
        help="Skill root. 기본값은 이 script directory의 parent다.",
    )
    parser.add_argument("--validate", action="store_true", help="spec 형식이 올바른지만 확인한다.")
    parser.add_argument("--output", default=None, help="채점할 produced output 경로. {output}에 binding된다.")
    parser.add_argument("--case", default=None, help="이 golden case id만 채점한다.")
    parser.add_argument(
        "--rollout",
        action="store_true",
        help="각 golden input에 대해 spec의 run command로 skill을 실행한 뒤 output을 채점한다.",
    )
    parser.add_argument(
        "--promote",
        action="store_true",
        help="--rollout과 함께 사용한다. pending-first-green case의 첫 passing output을 baseline으로 저장한다.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_ROLLOUT_TIMEOUT,
        help=f"--rollout에서 case별 실행 timeout 초 단위. 기본값 {DEFAULT_ROLLOUT_TIMEOUT}.",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable JSON을 출력한다.")
    args = parser.parse_args(argv)

    skill_dir = Path(args.skill_dir).resolve() if args.skill_dir else _default_skill_dir()

    spec_path = find_spec(skill_dir)
    if spec_path is None:
        msg = f"no evals/*.eval.md found under {skill_dir}"
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
            print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
        elif errors:
            print(f"INVALID {spec_path.name}:")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"VALID {spec_path.name}")
        return 1 if errors else 0

    if errors:
        # malformed spec은 정직하게 실행할 수 없으므로 먼저 --validate를 요구한다.
        head = f"ERROR: {spec_path.name} is malformed; run --validate"
        print(json.dumps({"error": head, "errors": errors}) if args.json else head, file=sys.stderr)
        return 1

    judges = llm_judge_criteria(spec)

    if args.rollout:
        if not spec.get("run"):
            msg = "rollout unavailable: spec has no 'run' command"
            print(json.dumps({"rollout": "unavailable", "reason": msg}) if args.json else msg)
            return 0
        result = run_rollout(
            spec, skill_dir, promote=args.promote, only_case=args.case, timeout=args.timeout
        )
        if args.json:
            print(json.dumps({**result, "llm_judge": [c["id"] for c in judges]}, indent=2))
        else:
            for check in result["checks"]:
                print(f"  [{check['status']:>7}] {check['case']} :: {check['criterion']}")
            print(
                f"\nrollout: {result['passed']} passed, {result['failed']} failed, "
                f"{result['errors']} errored"
            )
            if result["promoted"]:
                print(f"promoted baselines: {', '.join(result['promoted'])}")
            if judges:
                print("\nllm-judge checks (evaluate manually or via /autoresearch-universal):")
                for crit in judges:
                    print(f"  - {crit['id']}: {crit['text']}")
        return 1 if (result["failed"] or result["errors"]) else 0

    output = Path(args.output).resolve() if args.output else None
    result = run_command_checks(spec, skill_dir, output=output, only_case=args.case)

    if args.json:
        print(json.dumps({**result, "llm_judge": [c["id"] for c in judges]}, indent=2))
    else:
        for check in result["checks"]:
            print(f"  [{check['status']:>7}] {check['case']} :: {check['criterion']}")
        print(
            f"\ncommand checks: {result['passed']} passed, "
            f"{result['failed']} failed, {result['skipped']} skipped"
        )
        if judges:
            print("\nllm-judge checks (evaluate manually or via /autoresearch-universal):")
            for crit in judges:
                print(f"  - {crit['id']}: {crit['text']}")

    return 1 if result["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
