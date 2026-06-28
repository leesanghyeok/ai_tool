# 2026-06-28 upstream test import

## mode

modify

## 목표

`/Users/stark/practice/agent-skill-creator/scripts/tests`에서 `skill-creator-for-stark`에 필요한 runner/pipeline regression test를 가져와 skill package 내부에서 실행 가능하게 한다.

## 주요 변경

- `scripts/tests/test_run_evals.py`를 추가했다.
- `scripts/tests/test_check_pipeline.py`를 추가했다.
- `scripts/tests/__init__.py`를 추가했다.
- upstream test의 영어 주석과 docstring을 한국어로 번역했다.
- local package layout에 맞게 import root를 `SCRIPTS_DIR = Path(__file__).parent.parent`로 조정했다.
- local `check_pipeline.py`의 한국어 error message에 맞게 third-party dependency assertion token을 조정했다.
- `SKILL.md`에 `python3.11 -m unittest discover -s scripts/tests -v` 검증 절차를 추가했다.

## 검증 기준

- `python3.11 -m unittest discover -s scripts/tests -v`가 통과해야 한다.
- `python3.11 -m py_compile`로 가져온 test file과 대상 helper script가 compile되어야 한다.
- `python3 scripts/validate-skill-package.py .`가 통과해야 한다.
- `git diff --check -- skills/skill-creator-for-stark`가 통과해야 한다.

## 주의사항

- 기본 `/usr/bin/python3`는 Python 3.9.6이라 `Path | None` syntax를 포함한 helper/test 실행에 부적합하다.
- 테스트 command는 `python3.11`을 사용한다.
