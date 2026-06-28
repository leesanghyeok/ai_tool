---
type: "feedback-log"
source_type: "ai-dissatisfaction"
source_platform: "session-db"
source_ref: "session-search"
session_id: "unknown-session"
ingested: "2026-06-27"
created_at: "2026-06-27T09:10:00+09:00"
task_type: "planning"
agent_or_model: ""
severity: "low"
categories: [specificity]
sha256: "efa648d32f55f9cfc47ee2c1d69fe86d853b63e494830d75cea0e45b4dad1bac"
---
# 중복 후보 제외 사건

## 상황 (Situation)

여러 session에서 비슷한 feedback 후보를 수확하는 중 같은 사건이 반복 발견됐다.

## 불만족한 점 (Dissatisfaction)

파일명만 보고 중복을 판단하면 의미상 같은 사건을 다시 만들 위험이 있었다.

## 기대한 동작 (Expected Behavior)

Situation, Expected Behavior, Evidence, Candidate Agent Rule의 의미를 비교해 중복을 제외해야 했다.

## 실제 동작 (Actual Behavior)

agent가 filename 중심으로만 중복 검사를 수행할 가능성이 있었다.

## 근거 (Evidence)

- 같은 session/source에서 같은 expected/actual/rule을 가진 후보가 반복됐다.

## 실패 범주 (Failure Categories)

- categories: [specificity]
- task_type: planning

## 심각도 (Severity)

low

## 후보 Agent 규칙 (Candidate Agent Rule)

Feedback 중복 검사는 filename이 아니라 source와 사건 의미를 함께 비교한다.

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] 기존 feedback files에서 의미상 같은 incident가 있는지 검색했는가?
