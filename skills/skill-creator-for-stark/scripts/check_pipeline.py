#!/usr/bin/env python3
"""
생성된 skill의 pipeline orchestration을 검증한다.

skill은 agent가 해석하는 prose이므로, 여러 script를 올바른 순서로 실행하도록
agent에게 맡기면 불안정하다. 해결책은 실행 순서를 code로 옮기는 것이다.
즉 `scripts/run_pipeline.py` 하나를 entrypoint로 두고, 그 안에서 각 step을
정해진 순서로 호출한다. 이 verifier는 그 계약의 기계적 조건을 확인한다.

1. compile  - scripts/와 shared/ 아래 모든 Python 파일이 SyntaxError 없이
              compile되는지 확인한다. 깨진 script는 agent 실행 실패의 흔한 원인이다.
2. deps     - third-party module을 import하면 requirements.txt가 있고 비어 있지
              않은지 확인한다. 실제 package별 완전 매핑이 아니라 dependency 선언
              존재 여부만 본다. import name과 distribution name 차이로 인한
              false positive를 피하기 위한 절충이다.
3. entry    - runnable step script가 2개 이상이면 `run_pipeline.py` orchestrator가
              있는지 warning으로 확인한다. 목적은 agent가 여러 command를 prose에서
              재구성하지 않고 한 command만 실행하게 만드는 것이다.

사용법:
    python3 scripts/check_pipeline.py <skill-dir>
    python3 scripts/check_pipeline.py <skill-dir> --json

Exit code:
    0 - error 없음. warning은 허용한다.
    1 - script compile 실패 또는 third-party import 선언 누락.
    2 - skill directory를 찾지 못함.
"""

from __future__ import annotations

import argparse
import ast
import json
import py_compile
import subprocess
import sys
from pathlib import Path

_ENTRY = "run_pipeline.py"
_TOOLING = {"run_pipeline.py", "run_evals.py"}
_SKIP_DIR_PARTS = {"__pycache__", "tests"}


def python_files(skill_dir: Path) -> list[Path]:
    """skill의 scripts/와 shared/ tree 아래에 있는 모든 .py 파일을 반환한다."""
    out: list[Path] = []
    for sub in ("scripts", "shared"):
        root = skill_dir / sub
        if root.is_dir():
            out += [
                p for p in root.rglob("*.py")
                if not (_SKIP_DIR_PARTS & set(p.parts))
            ]
    return sorted(out)


def compile_failures(files: list[Path]) -> list[str]:
    """compile에 실패한 파일마다 'path: message' 형식의 문자열을 반환한다."""
    failures: list[str] = []
    for f in files:
        try:
            py_compile.compile(str(f), doraise=True)
        except py_compile.PyCompileError as exc:
            failures.append(f"{f}: {exc.msg}")
    return failures


def _local_module_names(skill_dir: Path, files: list[Path]) -> set[str]:
    names = {p.stem for p in files}
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        for child in scripts_dir.iterdir():
            if child.is_dir() and child.name not in _SKIP_DIR_PARTS:
                names.add(child.name)
    return names


def _top_level_imports(file: Path) -> set[str]:
    try:
        tree = ast.parse(file.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()  # SyntaxError는 compile_failures에서 별도로 보고한다.
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            mods.add(node.module.split(".")[0])
    return mods


def third_party_imports(skill_dir: Path, files: list[Path]) -> list[str]:
    """stdlib도 local module도 아닌 top-level import module 목록을 반환한다."""
    local = _local_module_names(skill_dir, files)
    stdlib = getattr(sys, "stdlib_module_names", set(sys.builtin_module_names) | {
        "__future__", "argparse", "ast", "csv", "datetime", "hashlib", "io", "json", "math",
        "os", "pathlib", "py_compile", "re", "shlex", "shutil", "subprocess",
        "sys", "tempfile", "textwrap", "typing", "unittest",
    })
    third: set[str] = set()
    for f in files:
        for mod in _top_level_imports(f):
            if mod and mod not in local and mod not in stdlib:
                third.add(mod)
    return sorted(third)


def requirements_declared(skill_dir: Path) -> bool:
    """requirements.txt가 있고 comment가 아닌 항목이 하나 이상 있으면 True를 반환한다."""
    req = skill_dir / "requirements.txt"
    if not req.exists():
        return False
    for line in req.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return True
    return False


def step_scripts(skill_dir: Path, files: list[Path]) -> list[Path]:
    """runnable pipeline step처럼 보이는 script를 반환한다.

    기준은 `__main__` guard 존재 여부다. orchestrator, eval runner, utility/test module은 제외한다.
    """
    steps: list[Path] = []
    for f in files:
        if f.name in _TOOLING or "utils" in f.parts:
            continue
        text = f.read_text(encoding="utf-8")
        if "if __name__" in text and "__main__" in text:
            steps.append(f)
    return steps


def has_orchestrator(skill_dir: Path) -> bool:
    return (skill_dir / "scripts" / _ENTRY).exists()


def pipeline_smoke_failures(skill_dir: Path) -> list[str]:
    entry = skill_dir / "scripts" / _ENTRY
    if not entry.exists():
        return []
    proc = subprocess.run(  # noqa: S603
        [sys.executable, str(entry), "--help"],
        cwd=str(skill_dir),
        capture_output=True,
        text=True,
        timeout=10,
    )
    if proc.returncode == 0:
        return []
    return [f"scripts/{_ENTRY} smoke --help failed: exit {proc.returncode}: {(proc.stderr or proc.stdout)[-500:]}"]


def check(skill_dir: Path) -> dict:
    """모든 check를 실행하고 {errors: [...], warnings: [...]}를 반환한다."""
    files = python_files(skill_dir)
    errors: list[str] = []
    warnings: list[str] = []

    errors += [f"does not compile -> {fail}" for fail in compile_failures(files)]

    third = third_party_imports(skill_dir, files)
    if third and not requirements_declared(skill_dir):
        errors.append(
            "third-party import가 선언되지 않았다: 다음 module을 제공하는 package를 requirements.txt에 추가해야 한다: "
            f"the package(s) behind {', '.join(third)}"
        )

    steps = step_scripts(skill_dir, files)
    if len(steps) >= 2 and not has_orchestrator(skill_dir):
        warnings.append(
            f"{len(steps)} runnable step scripts but no scripts/{_ENTRY} — the agent "
            "prose를 보고 순서를 재구성해야 한다. single orchestrator entrypoint를 추가하라."
        )
    errors += pipeline_smoke_failures(skill_dir)

    return {"errors": errors, "warnings": warnings}


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="생성된 skill의 pipeline wiring을 검증한다.")
    parser.add_argument("skill_dir", help="skill directory 경로.")
    parser.add_argument("--json", action="store_true", help="machine-readable JSON을 출력한다.")
    return parser.parse_args(argv)


def _print_missing_dir(skill_dir: Path, *, as_json: bool) -> None:
    msg = f"not a directory: {skill_dir}"
    print(json.dumps({"error": msg}) if as_json else f"ERROR: {msg}", file=sys.stderr)


def _emit_result(result: dict, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, indent=2))
        return
    for err in result["errors"]:
        print(f"  [ERROR] {err}")
    for warn in result["warnings"]:
        print(f"  [WARN]  {warn}")
    if not result["errors"] and not result["warnings"]:
        print("pipeline OK")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    skill_dir = Path(args.skill_dir).resolve()
    if not skill_dir.is_dir():
        _print_missing_dir(skill_dir, as_json=args.json)
        return 2
    result = check(skill_dir)
    _emit_result(result, as_json=args.json)
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
