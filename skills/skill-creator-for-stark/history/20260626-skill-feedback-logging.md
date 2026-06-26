# 2026-06-26 스킬 feedback logging 절차 추가

## 작업 모드 (Mode)

`modify`

## 목표

생성되는 모든 스킬이 사용 중 발생한 불만족 사건을 자기 스킬 디렉터리 내부 `feedback/` 아래에 raw Markdown log로 남길 수 있게 `skill-creator-for-stark` workflow, template, validator를 보강한다.

## 주요 변경

- `references/skill-feedback-logging-rules.md` 추가.
- `SKILL.md`에 `INPUT_SKILL_FEEDBACK_LOGGING_POLICY`, `OUTPUT_SKILL_FEEDBACK_LOGGING_GUIDE`, `ENV_FEEDBACK_LOG_FORMAT_REFERENCE`와 feedback logging gate/workflow 추가.
- `templates/SKILL.template.md`에 `## 피드백 로깅 (Feedback Logging)` section 추가.
- `scripts/validate-skill-package.py`가 `feedback/` support directory를 허용하고 feedback guidance 누락을 감지하도록 변경.
- `templates/skill-output-template.md`에 feedback logging 산출물 보고 항목 추가.

## 검증

작업 후 validator, Python compile, `git diff --check`로 확인한다.
