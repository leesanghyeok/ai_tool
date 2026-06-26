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
categories: [specificity, verbosity, format]
sha256: "fbd40d2512e9184589199d1494399d65b1c39ab83b81ebea983512654da0ca6d"
---
# feedback-ai-logging-v2 출력 변수가 템플릿 내용을 중복함

## 상황 (Situation)

사용자가 `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md`를 검토한 뒤, `/feedback-ai-logging-v2` 스킬로 해당 스킬 자체의 설계 불만족을 raw feedback log로 남기라고 요청했다. 사용자는 한 발언 안에서 입력 변수 과다, 출력 변수 과다, `ENV_` 변수 필요성 불명확이라는 세 가지 불만사항을 각각 제기했다.

## 불만족한 점 (Dissatisfaction)

출력 변수가 최종 output template에 적을 내용을 거의 그대로 변수화한 것처럼 보인다. 결과 확인에 필요한 핵심 정보와 보고 문장 구성 요소가 분리되지 않아 불필요하게 장황하다.

## 기대한 동작 (Expected Behavior)

출력 계약은 생성 파일 경로, 중복/비사건 skip 수, 검증 결과, 남은 blocker처럼 사용자가 실제로 확인해야 하는 핵심 결과만 담아야 한다. 최종 보고 문장이나 template에 자연스럽게 들어갈 세부 설명은 변수 표에서 제거해야 한다.

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
- `verbosity`
- `format`

## 심각도 (Severity)

medium

스킬 실행 자체를 완전히 막지는 않지만, 스킬 사용자가 매번 불필요한 입력/출력/환경 해석 비용을 치르게 만들고 raw feedback 기록 품질을 떨어뜨릴 수 있다.

## 후보 Agent 규칙 (Candidate Agent Rule)

스킬의 `OUTPUT_` 계약은 최종 보고서 템플릿 전체를 변수화하지 말고, 상태 판단과 후속 행동에 필요한 최소 결과값만 포함한다.

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] `OUTPUT_` 항목이 사용자 판단에 필요한 결과값인지 확인한다.
- [ ] template 문장 구성 요소에 불과한 항목은 출력 변수에서 제거한다.
- [ ] 최종 응답은 변수 표가 아니라 짧은 상태/파일/검증/미확인 항목으로 구성한다.
