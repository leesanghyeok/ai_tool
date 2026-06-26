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
categories: [context-misread, specificity, actionability]
sha256: "3d56981deb2ee9399ab71ac98a45c7518b5a9f7aeb7ae19d6ad32eafa56bfbd9"
---
# feedback-ai-logging-v2 Hard Gates가 스킬 고유 기준이 아님

## 상황 (Situation)

사용자가 `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md`를 검토하며 추가 불만사항을 제시했다. 이번 불만은 Hard Gates 섹션이 스킬 고유 기준이 아니라 범용 skill creator 기준처럼 작성된 점과, trigger 판단 섹션이 중복된 점에 관한 것이다.

## 불만족한 점 (Dissatisfaction)

Hard Gates 섹션이 `feedback-ai-logging-v2`의 raw feedback 기록 품질을 직접 보장하는 기준보다, 범용 skill creator가 SKILL.md를 작성할 때 지켜야 하는 메타 규칙을 포함하고 있다. `Metadata gate`, `Body size gate`처럼 스킬 패키지 형식 검증에 가까운 항목이 섞여 있어 이 스킬 실행자가 무엇을 반드시 지켜야 하는지 흐린다.

## 기대한 동작 (Expected Behavior)

Hard Gates는 이 스킬이 수행하는 “AI/agent 불만족 사건을 raw feedback Markdown으로 남기는 작업”에 직접 필요한 불변 조건만 담아야 한다. 예를 들어 one incident one file, evidence completeness, idempotency, raw immutability, validation처럼 feedback log 생성 결과를 좌우하는 기준은 유지하되, 범용 skill metadata/body-size 규칙은 별도 skill-authoring 검증이나 패키지 품질 기준으로 이동해야 한다.

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

- `context-misread`
- `specificity`
- `actionability`

## 심각도 (Severity)

medium

스킬 실행을 즉시 차단하지는 않지만, 스킬 문서가 범용 작성 규칙과 실제 실행 규칙을 섞거나 trigger 판단을 중복해 실행자의 판단 비용을 높인다.

## 후보 Agent 규칙 (Candidate Agent Rule)

스킬별 Hard Gates에는 해당 스킬의 실행 결과와 안전성에 직접 영향을 주는 domain-specific gate만 둔다. 범용 SKILL.md 작성 규칙이나 skill creator 품질 기준을 개별 스킬의 Hard Gates로 복사하지 않는다.

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] Hard Gates 각 항목이 이 스킬의 산출물 품질/안전성에 직접 영향을 주는지 확인한다.
- [ ] `Metadata gate`, `Body size gate` 같은 범용 패키지 규칙은 skill-authoring 또는 validation checklist로 이동한다.
- [ ] feedback log 생성에 필요한 evidence, idempotency, immutability, validation 기준은 구체화해서 유지한다.
