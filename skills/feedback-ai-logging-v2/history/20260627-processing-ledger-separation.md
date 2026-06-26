# 2026-06-27 processing ledger separation

## mode

modify

## 목표

raw feedback logging workflow에 처리 여부 추적을 섞지 않고, 최소 processing ledger 규칙으로 분리했다.

## 주요 결정

- raw feedback file에는 status, 처리 이력, 승격 여부를 쓰지 않는다.
- 처리 여부는 별도 ledger에서 `sha256 + consumer + filename`으로 판단한다.
- `consumer`는 초기 allowlist 4개만 사용한다.
  - `feedback-ai-logging-v2`
  - `skill-creator-for-stark`
  - `rubric-skill`
  - `memory`
- `status`는 `todo`, `done`, `skip`만 사용한다.
- `target_artifact`는 path 이동에 취약하므로 ledger key에서 제외한다.

## 변경 파일

- `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md`
- `/Users/stark/project/jarvis/ai_tool/skills/skill-creator-for-stark/references/skill-feedback-logging-rules.md`

## 검증

최종 검증은 세션의 tool output을 기준으로 보고한다.
