# 2026-06-27 feedback processing ledger 최소화

## mode

modify

## 목표

스킬별 `feedback/` raw log를 반복해서 사용할 때 이미 처리한 feedback인지 구분하기 위한 최소 processing ledger 규칙을 추가했다.

## 주요 결정

- raw feedback file은 계속 immutable raw incident로 둔다.
- 처리 여부는 raw log가 아니라 별도 processing ledger에 기록한다.
- ledger identity는 `sha256 + consumer + filename`으로 한다.
- `target_artifact`는 path 이동에 취약하므로 key에서 제외한다.
- `consumer`는 초기에는 `feedback-ai-logging-v2`, `skill-creator-for-stark`, `rubric-skill`, `memory` 네 가지만 허용한다.
- `status`는 `todo`, `done`, `skip` 세 가지만 사용한다.

## 변경 파일

- `/Users/stark/project/jarvis/ai_tool/skills/skill-creator-for-stark/references/skill-feedback-logging-rules.md`
- `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md`

## 검증

최종 검증은 세션의 tool output을 기준으로 보고한다.
