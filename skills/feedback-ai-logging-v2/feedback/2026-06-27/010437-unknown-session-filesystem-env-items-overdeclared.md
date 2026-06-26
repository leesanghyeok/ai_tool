---
type: feedback-log
source_type: skill-dissatisfaction
source_platform: cli
source_ref: "current conversation; skill=feedback-ai-logging-v2; target=SKILL.md"
session_id: "unknown-session"
ingested: 2026-06-27
created_at: 2026-06-27T01:04:37+09:00
task_type: skill-usage
agent_or_model: "Hermes Agent"
severity: medium
categories: [specificity, verbosity, skill-workflow]
sha256: "5f7ec295743ea285f18feac464ff929120b35c67a20f346c59edac0d17041bda"
---
# feedback-ai-logging-v2가 파일 읽기 쓰기를 필수 환경으로 과도하게 명시함

## 상황 (Situation)

사용자가 `feedback-ai-logging-v2` 스킬 자체의 feedback 기록 방식을 검토하면서, 현재 스킬 문서와 직전 생성 로그가 너무 큰 단위로 묶이고 실제 스킬 원문 근거를 충분히 담지 못한다고 지적했다. 대상 스킬 파일은 `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md`다.

## 불만족한 점 (Dissatisfaction)

`ENV_FILESYSTEM_READ`와 `ENV_FILESYSTEM_WRITE`는 feedback log를 읽고 쓰는 스킬에서 당연한 전제인데, 필수 환경 변수처럼 명시되어 스킬 고유 요구사항을 흐린다.

## 기대한 동작 (Expected Behavior)

필수 환경에는 이 스킬에서 특별히 구분해야 하는 도구/런타임만 남겨야 한다. 일반적인 filesystem read/write 권한은 workflow 전제나 실패 시 보고로 처리하고, `ENV_` 계약으로 노출하지 않는다.

## 실제 동작 (Actual Behavior)

SKILL.md의 필수 환경 표는 `ENV_FILESYSTEM_READ`와 `ENV_FILESYSTEM_WRITE`를 required 항목으로 둔다.

## 근거 (Evidence)

사용자 발화:

> ENV_FILESYSTEM_READ ENV_FILESYSTEM_WRITE 이것도 당연한 거잖아 뭐하러 명시해. 이 스킬에서만 필요한 내용을 정의해야지.

스킬 원문 근거:

SKILL.md line 67: `## 필수 환경` 섹션 시작.
SKILL.md line 71: `ENV_FILESYSTEM_READ` required — source와 기존 feedback 파일을 읽을 수 있어야 한다고 명시.
SKILL.md line 72: `ENV_FILESYSTEM_WRITE` required — target 아래 새 Markdown 파일을 쓸 수 있어야 한다고 명시.

## 실패 범주 (Failure Categories)

- `specificity`
- `verbosity`
- `skill-workflow`

## 심각도 (Severity)

medium

## 후보 Agent 규칙 (Candidate Agent Rule)

스킬의 `ENV_` 항목에는 해당 스킬의 특수 런타임/검증 요구만 남기고, 일반 파일 읽기/쓰기 권한처럼 모든 파일 작업에 당연한 전제는 변수화하지 않는다.

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] ENV 항목이 이 스킬에 특수한 요구인지 확인한다.
- [ ] 일반 권한/파일 I/O 전제는 필수 환경 표에서 제거한다.
