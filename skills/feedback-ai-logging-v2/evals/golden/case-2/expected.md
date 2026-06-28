---
type: "feedback-log"
source_type: "skill-dissatisfaction"
source_platform: "cli"
source_ref: "feedback-ai-logging-v2"
session_id: "unknown-session"
ingested: "2026-06-27"
created_at: "2026-06-27T09:05:00+09:00"
task_type: "skill-usage"
agent_or_model: ""
severity: "medium"
categories: [skill-workflow]
sha256: "f86629aaa6b5a7cfa30b77c686a89a6a82e384a33c2ef3dd90c584774f684167"
---
# 스킬 사용 불만족 로컬 기록

## 상황 (Situation)

사용자가 특정 스킬을 사용해 문서를 수정했지만 스킬의 승인 경계가 모호했다.

## 불만족한 점 (Dissatisfaction)

스킬 사용 중 발생한 실패를 전역 wiki가 아니라 해당 스킬 내부 feedback으로 남겨야 했다.

## 기대한 동작 (Expected Behavior)

대상 스킬의 `feedback/YYYY-MM-DD/` 아래에 one incident one file로 저장해야 했다.

## 실제 동작 (Actual Behavior)

agent가 skill-local routing 기준을 명시하지 못했다.

## 근거 (Evidence)

- 대상 skill: feedback-ai-logging-v2
- 사용자가 skill-local feedback 저장 기준을 요구했다.

## 실패 범주 (Failure Categories)

- categories: [skill-workflow]
- task_type: skill-usage

## 심각도 (Severity)

medium

## 후보 Agent 규칙 (Candidate Agent Rule)

스킬 사용 불만족은 사용자가 명시한 경우 해당 스킬 디렉터리 내부 `feedback/`에 저장한다.

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] skill-local feedback이면 `source_type: skill-dissatisfaction`과 `feedback/YYYY-MM-DD/` 경로를 사용했는가?
