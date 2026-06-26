---
type: feedback-log
source_type: ai-dissatisfaction
source_platform: cli
source_ref: "current conversation; target=/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/feedback"
session_id: "unknown-session"
ingested: 2026-06-27
created_at: 2026-06-27T00:11:32+09:00
task_type: planning
agent_or_model: "Hermes Agent"
severity: medium
categories: [context-misread, requirement-miss, actionability]
sha256: "80b92de47bf512c0b5af97b0370bbef7c50f460f716683be2d7d1255dd78951b"
---
# feedback-ai-logging-v2가 명시 output directory 아래에 임의 하위 경로를 추가함

## 상황 (Situation)

사용자가 feedback log 저장 위치로 `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/feedback`를 명시했는데, 이전 실행에서 agent가 해당 디렉터리 바로 아래가 아니라 `feedback/raw/feedback/...` 하위 경로를 만들어 저장했다. 사용자는 명시된 output directory를 그대로 존중해야 한다고 추가 불만을 제기했다.

## 불만족한 점 (Dissatisfaction)

사용자가 저장 디렉터리를 명시했는데도 스킬/agent가 자체 기본 경로 규칙을 덧붙여 `raw/feedback` 하위 디렉터리를 만들었다. 이는 사용자의 명시 경로를 output root로 재해석하고 내부 subdir 규칙을 추가한 것으로, 요청한 저장 위치와 실제 저장 위치가 달라진다.

## 기대한 동작 (Expected Behavior)

사용자가 `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/feedback`처럼 구체적인 저장 디렉터리를 지정하면, 새 feedback log 파일은 그 디렉터리 바로 아래에 생성해야 한다. 별도 승인이 없으면 `raw/feedback`, 날짜 폴더, domain wiki routing 등 agent 고유의 하위 경로 규칙을 추가하지 않는다. 경로 validator가 기본 `raw/feedback`만 허용한다면 validator를 이유로 경로를 바꾸지 말고, 사용자 지정 경로에 맞는 검증을 수행하거나 스킬/validator 개선 필요성을 보고해야 한다.

## 근거 (Evidence)

사용자 발언 원문:

> 또 있어 /Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/feedback 에 저장하라고 했더니 feedback/raw/feedback/ 이렇게 하위 디렉토리를 만들더라??? 내가 요청한 디렉토리가 /Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/feedback 라면 여기에 바로 만들어야지 자기만에 디렉토리를 왜 또 지정해 이러면안돼

이전 잘못된 생성 경로:

`/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/feedback/raw/feedback/2026-06-26/235603-unknown-session-skill-interface-overparameterized.md`

사용자가 명시한 저장 디렉터리:

`/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/feedback`

## 실패 범주 (Failure Categories)

- `context-misread`
- `requirement-miss`
- `actionability`

## 심각도 (Severity)

medium

사용자가 명시한 파일 위치를 어기면 산출물 발견성과 후속 처리 경로가 달라지고, 스킬의 기본 routing 규칙이 사용자 지시보다 우선되는 문제가 생긴다.

## 후보 Agent 규칙 (Candidate Agent Rule)

사용자가 output directory를 명시하면 그 경로를 최종 저장 디렉터리로 취급하고, 별도 승인 없이 내부 기본 subdir이나 날짜 폴더를 추가하지 않는다. validator나 스킬 기본 경로가 사용자 지정 경로와 충돌하면 경로를 임의 변경하지 말고 충돌을 명시하고 사용자 지정 경로 기준으로 검증한다.

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] 사용자가 지정한 경로가 output root인지 최종 directory인지 문맥상 확인한다.
- [ ] “여기에 저장”, “아래에 바로”, 구체 directory path가 있으면 파일을 해당 directory 바로 아래에 만든다.
- [ ] 기본 `raw/feedback` routing은 사용자가 경로를 지정하지 않았을 때만 적용한다.
- [ ] validator path convention이 사용자 지시와 충돌하면 validator 결과를 절대 경로 변경 근거로 삼지 않는다.
