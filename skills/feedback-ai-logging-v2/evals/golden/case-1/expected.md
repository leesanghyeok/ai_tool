---
type: "feedback-log"
source_type: "ai-dissatisfaction"
source_platform: "cli"
source_ref: "current-session"
session_id: "unknown-session"
ingested: "2026-06-27"
created_at: "2026-06-27T09:00:00+09:00"
task_type: "review"
agent_or_model: ""
severity: "high"
categories: [verification, evidence]
sha256: "b500e788810cbcf075120b931d52a7c568351c89c940a643bf3bf69d9213aa0a"
---
# 검증 없이 완료 보고한 사건

## 상황 (Situation)

사용자가 agent workflow 결과를 완료로 보고받았지만 실제 validator 출력은 제공되지 않았다.

## 불만족한 점 (Dissatisfaction)

완료 주장에 필요한 read-back 또는 validator evidence가 없었다.

## 기대한 동작 (Expected Behavior)

완료 전 실제 command output, file read-back, 실패 여부를 확인하고 보고해야 했다.

## 실제 동작 (Actual Behavior)

agent가 검증 evidence 없이 완료처럼 요약했다.

## 근거 (Evidence)

- 사용자 발화: "검증 없이 완료라고 하지 마."
- 확인된 source: current_session excerpt.

## 실패 범주 (Failure Categories)

- categories: [verification, evidence]
- task_type: review

## 심각도 (Severity)

high

## 후보 Agent 규칙 (Candidate Agent Rule)

완료를 주장하기 전에 실제 validator 또는 read-back output을 확보하고, 없으면 unverified로 보고한다.

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] 완료 보고 직전에 실제 검증 output이 있는가?
