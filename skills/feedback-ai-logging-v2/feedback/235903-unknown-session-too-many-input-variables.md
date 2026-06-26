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
categories: [specificity, actionability, verbosity]
sha256: "3ad0c90642656d463f3806b5cf61f3b9b16007275b24ec69649637e1b1b1d58a"
---
# feedback-ai-logging-v2 입력 변수가 과다함

## 상황 (Situation)

사용자가 `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md`를 검토한 뒤, `/feedback-ai-logging-v2` 스킬로 해당 스킬 자체의 설계 불만족을 raw feedback log로 남기라고 요청했다. 사용자는 한 발언 안에서 입력 변수 과다, 출력 변수 과다, `ENV_` 변수 필요성 불명확이라는 세 가지 불만사항을 각각 제기했다.

## 불만족한 점 (Dissatisfaction)

스킬 문서가 실제 결과에 크게 영향을 주는 입력만 요구하지 않고, 기본값이 있거나 자주 바뀌지 않는 값까지 입력 변수로 과하게 노출한다. 실행자가 매번 무엇을 채워야 하는지 불필요하게 커진다.

## 기대한 동작 (Expected Behavior)

입력 변수는 기록 범위, source, 쓰기 승인, 예외적인 output 위치처럼 사건 결과에 실질적으로 영향을 주고 사용자가 직접 결정해야 하는 값만 남겨야 한다. 안정적인 기본값이 있는 경로, timezone, 중복 정책, validation mode 같은 항목은 workflow 내부 기본 동작으로 내려야 한다.

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

- `specificity`
- `actionability`
- `verbosity`

## 심각도 (Severity)

medium

스킬 실행 자체를 완전히 막지는 않지만, 스킬 사용자가 매번 불필요한 입력/출력/환경 해석 비용을 치르게 만들고 raw feedback 기록 품질을 떨어뜨릴 수 있다.

## 후보 Agent 규칙 (Candidate Agent Rule)

스킬의 `INPUT_` 계약은 결과에 큰 영향을 주며 사용자가 매번 결정해야 하는 값만 포함하고, 안정적 기본값이나 내부 정책은 입력 표로 승격하지 않는다.

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] `INPUT_` 항목마다 사용자가 실제로 제공해야 하는지 확인한다.
- [ ] 기본값이 안정적인 timezone, 중복 정책, validation mode는 workflow 설명으로 이동한다.
- [ ] 입력 표를 읽었을 때 최소 필수값과 예외 override만 남아 있는지 확인한다.
