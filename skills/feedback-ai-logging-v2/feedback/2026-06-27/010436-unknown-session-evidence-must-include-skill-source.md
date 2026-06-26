---
type: feedback-log
source_type: skill-dissatisfaction
source_platform: cli
source_ref: "current conversation; skill=feedback-ai-logging-v2; target=SKILL.md"
session_id: "unknown-session"
ingested: 2026-06-27
created_at: 2026-06-27T01:04:36+09:00
task_type: skill-usage
agent_or_model: "Hermes Agent"
severity: medium
categories: [evidence, verification, skill-workflow]
sha256: "7d79c6b375f54d3dd3c6a374cf089c3a862f3d3b9ad41a3116ac07bb2ea7e977"
---
# feedback 근거에 사용자 발화만 있고 스킬 원문 근거가 부족함

## 상황 (Situation)

사용자가 `feedback-ai-logging-v2` 스킬 자체의 feedback 기록 방식을 검토하면서, 현재 스킬 문서와 직전 생성 로그가 너무 큰 단위로 묶이고 실제 스킬 원문 근거를 충분히 담지 못한다고 지적했다. 대상 스킬 파일은 `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md`다.

## 불만족한 점 (Dissatisfaction)

이전 feedback log의 Evidence가 사용자 발화 중심으로만 구성되어, 실제 SKILL.md에 어떤 변수와 규칙이 어떻게 적혀 있었는지 함께 보존하지 못했다.

## 기대한 동작 (Expected Behavior)

스킬 자체에 대한 불만족을 기록할 때는 사용자 발화뿐 아니라 SKILL.md의 관련 section, 변수명, line 또는 excerpt를 함께 남겨야 한다. 그래야 나중에 어떤 문서 내용이 문제였는지 재현할 수 있다.

## 실제 동작 (Actual Behavior)

이전 로그는 사용자 발화 원문과 대상 파일 path는 담았지만, `SKILL.md`의 입력 변수 표, 필수 환경 표, hard gate 등 실제 문서 내용 excerpt를 충분히 담지 않았다.

## 근거 (Evidence)

사용자 발화:

> 근거 내용보니까 내 내용만 적어두고 있는데 스킬 읽어서 스킬에 어떻게 기록되어있는지도 담아서 기록해줘.

스킬 원문 근거:

SKILL.md line 80: Evidence completeness gate는 expected behavior, actual behavior, mismatch, evidence excerpt, candidate rule을 요구함.
SKILL.md lines 128-130: 중복 검사는 filename이 아니라 Situation, Expected Behavior, Evidence, Candidate Agent Rule 의미를 비교하라고 함.
SKILL.md lines 139-141: 작성 후 validator와 read-back을 요구함.

## 실패 범주 (Failure Categories)

- `evidence`
- `verification`
- `skill-workflow`

## 심각도 (Severity)

medium

## 후보 Agent 규칙 (Candidate Agent Rule)

스킬 문서 품질 feedback의 Evidence에는 사용자 발화 excerpt와 함께 대상 스킬 파일의 관련 원문 excerpt 또는 line reference를 반드시 포함한다.

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] Evidence에 사용자 발화와 대상 스킬 원문이 모두 있는지 확인한다.
- [ ] 대상 스킬 원문은 변수명/section/line reference 수준으로 재현 가능하게 남긴다.
