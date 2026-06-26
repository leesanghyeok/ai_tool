---
type: feedback-log
source_type: skill-dissatisfaction
source_platform: cli
source_ref: "<skill-name or skill-path>"
session_id: "unknown-session"
ingested: <YYYY-MM-DD>
created_at: <YYYY-MM-DDTHH:MM:SS+TZ>
task_type: skill-usage
agent_or_model: "<agent-or-model>"
severity: medium
categories: [skill-workflow]
sha256: "<body-only-sha256>"
---
# <짧은 불만족 제목>

## 상황 (Situation)

<어떤 스킬을 어떤 목적으로 사용했는지 적는다.>

## 불만족한 점 (Dissatisfaction)

<기대와 다르게 동작한 점을 사건 단위로 적는다.>

## 기대한 동작 (Expected Behavior)

<스킬이 했어야 하는 절차, 산출물, 검증, 경계를 적는다.>

## 근거 (Evidence)

<사용자 발화, tool output, file path, 검증 실패 등 확인 가능한 근거를 적는다.>

## 실패 범주 (Failure Categories)

- `<category>`

## 심각도 (Severity)

medium

## 후보 Agent 규칙 (Candidate Agent Rule)

<재발 방지를 위해 스킬 또는 creator에 넣을 수 있는 후보 규칙을 적는다.>

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] <검증 또는 최종 응답 checklist 후보>
