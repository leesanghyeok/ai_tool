---
type: feedback-log
source_type: ai-dissatisfaction
source_platform: cli
source_ref: "current conversation; target=/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/"
session_id: "unknown-session"
ingested: 2026-06-27
created_at: 2026-06-27T00:06:32+09:00
task_type: planning
agent_or_model: "Hermes Agent"
severity: medium
categories: [format, actionability, specificity]
sha256: "35b798615e8fe013dd81b1a1dde19d927fb5edf46169b7233d6cc6b58cae958c"
---
# feedback-ai-logging-v2 로그 템플릿이 templates/가 아니라 references/에 있음

## 상황 (Situation)

사용자가 `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md`와 관련 파일 구조를 검토하며 추가 불만사항을 제기했다. 이 스킬의 핵심 산출물은 feedback log Markdown 파일이고, 해당 산출물의 형식/템플릿이 존재하지만 `templates/`가 아니라 `references/` 아래에 배치되어 있다는 지적이다.

## 불만족한 점 (Dissatisfaction)

스킬이 생성하려는 직접 산출물이 로그 파일인데, 그 로그 파일의 템플릿 역할을 하는 문서가 `templates/`에 있지 않고 `references/`에 들어가 있다. 이 때문에 산출물 템플릿과 참고 설명 문서의 경계가 흐려지고, 실행자가 실제로 복사/작성 기준으로 삼아야 할 파일을 찾기 어렵다.

## 기대한 동작 (Expected Behavior)

산출물의 구조를 직접 정의하는 파일은 `templates/` 아래에 두어야 한다. `references/`에는 판단 기준, 라우팅 규칙, cross-session 수확 방식, incident selection 같은 배경 규칙을 두고, 실제 feedback log Markdown 골격이나 frontmatter/body 섹션 템플릿은 `templates/feedback-log.template.md` 같은 이름으로 분리해야 한다.

## 근거 (Evidence)

사용자 발언 원문:

> 또, 이 스킬에서 바라보고 있는산출물이 로그 파일이고 로그 템플릿이 잇는데 templates/ 에 없고 references/에 들어가있네 ???

대상 스킬 디렉터리: `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/`

## 실패 범주 (Failure Categories)

- `format`
- `actionability`
- `specificity`

## 심각도 (Severity)

medium

스킬 실행 자체를 막지는 않지만, 산출물 템플릿의 위치가 직관적이지 않아 스킬 유지보수와 실행 일관성을 떨어뜨린다.

## 후보 Agent 규칙 (Candidate Agent Rule)

스킬이 특정 파일 산출물을 생성한다면, 실제 산출물 골격과 작성 템플릿은 `templates/`에 두고, `references/`에는 판단 기준과 설명 문서만 둔다. 산출물 템플릿을 reference 문서로 숨기지 않는다.

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] 이 스킬의 직접 산출물이 무엇인지 확인한다.
- [ ] 산출물 골격/복사용 양식은 `templates/` 아래에 둔다.
- [ ] `references/`에는 배경 규칙, 라우팅, 선택 기준, 마이그레이션 설명만 둔다.
- [ ] SKILL.md workflow가 실제 템플릿 경로를 명시하는지 확인한다.
