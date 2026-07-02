# Case-based eval suite migration

## 날짜

2026-06-28

## mode

modify

## 목표

`skill-creator-for-stark`의 eval contract를 기존 `evals/*.eval.md` + global `criteria` + `golden` 중심에서, 사용자가 요청한 독립 case 운용 방식으로 전환했다.

## 주요 변경

- `evals/skill-creator-for-stark.eval.yaml`을 suite manifest/source of truth로 추가했다.
- `evals/07-validate-package/case.yaml`, `08-runner-regression/case.yaml`, `06-eval-contract/case.yaml`을 추가했다.
- `scripts/run_evals_template.py`와 `scripts/run_evals.py`를 case-based runner로 교체했다.
- `scripts/tests/test_run_evals.py`를 case-based runner regression test로 교체했다.
- `references/skill-eval-authoring-rules.md`, `templates/eval-spec.template.md`, `SKILL.md`, `README.md`, `references/deterministic-workflow-rules.md`를 새 계약에 맞게 갱신했다.
- `scripts/validate-skill-package.py`가 `evals/*.eval.yaml`과 `scripts/run_evals.py --validate`를 검증하도록 갱신했다.
- `scripts/check_eval_contract_docs.py`를 추가해 reference/template/SKILL 문서가 case-based eval 핵심 토큰을 유지하는지 검증한다.

## 새 계약 요약

- `eval.yaml`에는 `title`, `test_policy`, declared `cases`만 둔다.
- top-level `run.command`, `global_assertions`, `description`은 금지한다.
- runner는 `eval.yaml`에 선언된 case만 실행한다.
- assertion type은 `command`, `llm-judge`만 사용한다.
- `expected`가 있으면 자동 equality 비교를 수행한다.
- `--promote`는 expected를 생성하거나 overwrite한다.
- `llm-judge`는 `run_llm_judge.py` subprocess contract로 JSON verdict/evidence를 검증한다.

## 검증

- `python3 scripts/run_evals.py --validate` → 통과.
- `python3 scripts/run_evals.py --json` → 3 cases passed, 0 failed.
- `python3 scripts/validate-skill-package.py .` → PASS.
- `python3.11 -m unittest scripts.tests.test_run_evals -v` → 10 tests OK.
- `python3.11 -m unittest discover -s scripts/tests -v` → 20 tests OK.
- `git -C /Users/stark/project/jarvis/ai_tool diff --check -- skills/skill-creator-for-stark` → 통과.

## 추가 정리

사용자 승인 후 기존 legacy Markdown eval manifest와 golden fixture directory를 제거했다. 현재 실행 source of truth는 `evals/skill-creator-for-stark.eval.yaml`과 declared `evals/*/case.yaml`이다.
