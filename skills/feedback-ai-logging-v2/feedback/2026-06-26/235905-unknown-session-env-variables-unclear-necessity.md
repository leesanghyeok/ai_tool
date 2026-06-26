---
type: feedback-log
source_type: ai-dissatisfaction
source_platform: cli
source_ref: "current conversation; target=/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md"
session_id: "unknown-session"
ingested: 2026-06-26
created_at: 2026-06-26T23:59:03+09:00
task_type: planning
agent_or_model: "Hermes Agent"
severity: medium
categories: [actionability, specificity, context-misread]
sha256: "fddccb56c20d143dea8c305d4fed91c5b41752267aae14777b8638bd0d35036e"
---
# feedback-ai-logging-v2 ENV 변수 필요성이 불명확함

## 상황 (Situation)

사용자가 `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md`를 검토한 뒤, `/feedback-ai-logging-v2` 스킬로 해당 스킬 자체의 설계 불만족을 raw feedback log로 남기라고 요청했다. 사용자는 한 발언 안에서 입력 변수 과다, 출력 변수 과다, `ENV_` 변수 필요성 불명확이라는 세 가지 불만사항을 각각 제기했다.

## 불만족한 점 (Dissatisfaction)

`ENV_` 항목이 왜 필요한지 불명확하고, 사용자 입력 변수처럼 보여 혼란을 만든다. 파일시스템 권한, time command, hash command, validator command 같은 실행 전제가 입력 계약과 같은 수준으로 노출되어 있다.

## 기대한 동작 (Expected Behavior)

환경/도구 요구사항은 사용자가 채우는 변수가 아니라 실행 전제와 검증 단계로 짧게 설명해야 한다. 반드시 확인해야 하는 도구가 있다면 “필요 도구/검증 전제”로 분리하고, 사용자가 제공할 값처럼 보이지 않게 해야 한다.

## 근거 (Evidence)

사용자 발언 원문:

> 스킬을 보는데 입력이 너무 많아, 진자 결과에 영향을 크게주는 입력만 남기는게 좋겠어. 
> 기본값이 있고 자주 바뀌는 값들은 굳이 변수로 표시안해도 돼.
> 
> 출력도 불필요한게 너무 많아. 그냥 output template에 적을 내용을 변수로 뽑은거 같아.
> 
> env 변수는 대체 왜 필요한지도 모르겠어.

대상 파일: `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md`

## 실패 범주 (Failure Categories)

- `actionability`
- `specificity`
- `context-misread`

## 심각도 (Severity)

medium

스킬 실행 자체를 완전히 막지는 않지만, 스킬 사용자가 매번 불필요한 입력/출력/환경 해석 비용을 치르게 만들고 raw feedback 기록 품질을 떨어뜨릴 수 있다.

## 후보 Agent 규칙 (Candidate Agent Rule)

스킬 문서에서 환경 요구사항은 `INPUT_`과 혼동되지 않도록 별도 “필요 도구/전제” 섹션에 최소화하고, 실행 결과를 바꾸는 사용자 선택값처럼 표현하지 않는다.

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] `ENV_` 항목이 사용자 입력처럼 보이지 않는지 확인한다.
- [ ] 권한/명령/validator 요구사항은 실행 전제 또는 Verification에 둔다.
- [ ] 환경 항목이 필요한 이유와 실패 시 영향이 한 줄로 설명되는지 확인한다.
