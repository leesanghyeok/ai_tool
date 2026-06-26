---
type: feedback-log
source_type: ai-dissatisfaction
source_platform: cli
source_ref: "current conversation; target=/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md"
session_id: "unknown-session"
ingested: 2026-06-27
created_at: 2026-06-27T00:05:08+09:00
task_type: planning
agent_or_model: "Hermes Agent"
severity: medium
categories: [verbosity, format, specificity]
sha256: "f8bf455a92dadbd3ddd83f3c58ead303e0a3230db8fdb61f8b71fc1581b06640"
---
# feedback-ai-logging-v2 사용 시점과 Trigger Examples가 중복됨

## 상황 (Situation)

사용자가 `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md`를 검토하며 추가 불만사항을 제시했다. 이번 불만은 Hard Gates 섹션이 스킬 고유 기준이 아니라 범용 skill creator 기준처럼 작성된 점과, trigger 판단 섹션이 중복된 점에 관한 것이다.

## 불만족한 점 (Dissatisfaction)

`사용 시점`, `사용하지 말아야 할 때`, `Trigger Examples`가 사실상 같은 trigger 판단을 반복한다. 같은 의미의 섹션이 분리되어 있어 문서가 길어지고, 스킬 사용자가 어느 섹션을 기준으로 trigger 여부를 판단해야 하는지 불필요하게 헷갈린다.

## 기대한 동작 (Expected Behavior)

trigger 판단은 하나의 섹션으로 통합해야 한다. 예를 들어 `사용 시점` 섹션 안에 `사용한다` / `사용하지 않는다` / 필요한 경우 짧은 예시를 함께 두고, 별도 `Trigger Examples` 섹션은 제거한다. 같은 판단 기준을 두 곳에서 유지하지 않아야 한다.

## 근거 (Evidence)

사용자 발언 원문:

> Hard Gates
> Metadata gate: name은 directory basename과 같고 1-64자 lowercase hyphen slug여야 한다. description은 1-1024자, 가능하면 약 100 words 이하로 유지한다.
> Body size gate: SKILL.md body는 5,000 words 이하로 유지하고 긴 taxonomy/예시는 references로 분리한다.
> Raw immutability gate: 기존 raw feedback file은 append, status update, promotion marker 추가를 하지 않는다.
> One incident one file gate: 파일 하나에는 독립된 feedback 사건 하나만 담는다.
> Evidence gate: expected behavior, actual behavior, mismatch, evidence excerpt, candidate rule이 모두 있어야 새 파일을 만든다.
> Idempotency gate: 쓰기 전에 기존 raw/feedback/**에서 같은 session/source와 의미상 같은 incident를 검색한다.
> Validation gate: 작성 후 body-only hash와 deterministic validator가 통과해야 완료로 보고한다.
>
> 하드게이트 섹션이 잇는데 이 스킬에 대한 내용이 아니라 그냥 스킬 creator가 지켜야하는 하드게이트야. 이 스킬에 대한 내용이 있어야지,
>
> 그리고 사용시점, 사용하지 않는 시점 섹션이 있는데 trigger 섹션이 왜 또 따로있는거야 ???
> 둘 다 같은 의미니까 하나만 있도록 해야해

대상 파일: `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md`

## 실패 범주 (Failure Categories)

- `verbosity`
- `format`
- `specificity`

## 심각도 (Severity)

medium

스킬 실행을 즉시 차단하지는 않지만, 스킬 문서가 범용 작성 규칙과 실제 실행 규칙을 섞거나 trigger 판단을 중복해 실행자의 판단 비용을 높인다.

## 후보 Agent 규칙 (Candidate Agent Rule)

스킬 문서에서 같은 의사결정을 설명하는 섹션을 중복 유지하지 않는다. trigger/use-case 판단은 하나의 canonical 섹션으로 합치고, 예시는 그 안에 최소한으로 포함한다.

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] `사용 시점`, `사용하지 말아야 할 때`, `Trigger Examples`가 같은 판단을 중복하는지 확인한다.
- [ ] 중복되면 하나의 trigger/use-case 섹션으로 병합한다.
- [ ] 예시는 별도 대형 섹션보다 canonical trigger 섹션 안의 짧은 항목으로 둔다.
