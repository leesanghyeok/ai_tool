# 2026-06-28 self eval cases restore

## mode

modify

## 목표

이전 롤백으로 제거된 `skill-creator-for-stark` 자체 eval case를 다시 추가해 creator 자체도 eval contract를 갖게 한다.

## 주요 변경

- `evals/skill-creator-for-stark.eval.md`를 추가했다.
- `evals/golden/create-new-skill/input.json`을 추가했다.
- `evals/golden/modify-existing-skill/input.json`을 추가했다.
- `evals/golden/quality-review-only/input.json`을 추가했다.
- `scripts/run_evals.py`를 `scripts/run_evals_template.py` 복사본으로 추가했다.
- `SKILL.md`에 자체 eval case 운영 절차와 검증 command를 연결했다.

## 검증 기준

- `python3 scripts/run_evals.py --validate`가 통과해야 한다.
- `python3 scripts/run_evals.py --json`이 command criteria를 통과해야 한다.
- `python3.11 -m unittest discover -s scripts/tests -v`가 통과해야 한다.
- `python3 scripts/validate-skill-package.py .`가 통과해야 한다.
- `git diff --check -- skills/skill-creator-for-stark`가 통과해야 한다.

## 주의사항

- `creator-workflow-contract`는 `llm-judge` criterion이므로 자동 채점 완료로 보고하지 않는다.
- 현재 golden cases는 `pending-first-green` baseline 상태다. `--promote`는 expected baseline 파일을 쓰므로 별도 승인 전에는 실행하지 않는다.
