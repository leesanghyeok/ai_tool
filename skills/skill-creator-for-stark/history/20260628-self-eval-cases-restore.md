# 2026-06-28 self eval cases restore

## mode

modify

## 목표

이전 롤백으로 제거된 `skill-creator-for-stark` 자체 eval case를 다시 추가해 creator 자체도 eval contract를 갖게 한다.

## 주요 변경

- 당시에는 legacy Markdown eval manifest와 golden input fixtures를 추가했다.
- 이후 case-based eval suite로 전환하면서 legacy manifest와 golden fixtures는 제거했다.
- `scripts/run_evals.py`를 `scripts/run_evals_template.py` 복사본으로 추가했다.
- `SKILL.md`에 자체 eval case 운영 절차와 검증 command를 연결했다.

## 검증 기준

- `python3 scripts/run_evals.py --validate`가 통과해야 한다.
- `python3 scripts/run_evals.py --json`이 command criteria를 통과해야 한다.
- `python3.11 -m unittest discover -s scripts/tests -v`가 통과해야 한다.
- `python3 scripts/validate-skill-package.py .`가 통과해야 한다.
- `git diff --check -- skills/skill-creator-for-stark`가 통과해야 한다.

## 주의사항

- 당시 `creator-workflow-contract`는 `llm-judge` criterion으로 자동 채점 완료로 보고하지 않았다.
- 이후 case-based eval suite에서는 `llm-judge`를 `run_llm_judge.py` subprocess contract로 검증한다.
