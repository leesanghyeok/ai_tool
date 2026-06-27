# 2026-06-27 agent-skill-creator eval 모델 반영

## mode

modify

## 목표

`/Users/stark/practice/agent-skill-creator`의 eval model을 `/skill-creator-for-stark`에 반영한다. spec, 절차, directory 구조는 agent-skill-creator 방식을 우선한다.

## 주요 변경

- `references/skill-eval-authoring-rules.md` 추가.
- `templates/eval-spec.template.md` 추가.
- `scripts/run_evals_template.py`와 `scripts/check_pipeline.py` 추가.
- `scripts/validate-skill-package.py`가 `evals/` directory와 `evals/*.eval.md` JSON spec을 검증하도록 확장.
- `SKILL.md`에 eval criteria definition, eval emission, `run_pipeline.py`, `run_evals.py --validate`/`--rollout` 절차를 추가.
- `references/deterministic-workflow-rules.md`에 pipeline orchestration과 eval 연결 규칙 추가.

## llm-judge 정책

`llm-judge`는 현재 자동 채점하지 않고 checklist로 유지한다. 자동 judge adapter는 추후 개선으로 남겼다.

## 검증 예정

- RED: 기존 validator가 `evals/`를 unsupported support directory로 실패하는 것 확인.
- GREEN: eval fixture가 validator를 통과하는지 확인.
- script compile, source example rollout, skill package validator, `git diff --check`, ad-hoc verification 실행.
