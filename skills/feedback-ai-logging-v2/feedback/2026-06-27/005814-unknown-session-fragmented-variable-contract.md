---
type: feedback-log
source_type: skill-dissatisfaction
source_platform: cli
source_ref: "current conversation; skill=feedback-ai-logging-v2; target=SKILL.md"
session_id: "unknown-session"
ingested: 2026-06-27
created_at: 2026-06-27T00:58:14+09:00
task_type: skill-usage
agent_or_model: "Hermes Agent"
severity: medium
categories: [actionability, verbosity, specificity, skill-workflow]
sha256: "af3cf9d585f813f93366333f963ff9b03eff0375d5da621a817a7e3e88d81678"
---
# feedback-ai-logging-v2 변수 계약이 과분화되어 직관적이지 않음

## 상황 (Situation)

사용자가 `feedback-ai-logging-v2` 스킬을 호출한 뒤, 현재 스킬의 입력/출력 변수 설계가 불필요하게 복잡하다고 지적했다. 대상은 `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md`의 `INPUT_FEEDBACK_SCOPE`, `INPUT_FEEDBACK_SOURCE`, `INPUT_OUTPUT_*`, `INPUT_WRITE_APPROVAL` 계약이다.

## 불만족한 점 (Dissatisfaction)

스킬이 사용자가 직관적으로 제공할 수 있는 하나의 source/scope와 하나의 output path로 충분한 정보를 여러 변수로 쪼개고 있다. 특히 파일 쓰기 승인을 별도 `INPUT_WRITE_APPROVAL`로 요구하는 것은 반복적인 raw feedback logging workflow에서 불필요한 마찰로 느껴진다.

## 기대한 동작 (Expected Behavior)

입력 계약은 단순해야 한다. `INPUT_FEEDBACK_SCOPE`와 `INPUT_FEEDBACK_SOURCE`는 하나의 직관적 입력으로 합치고, `INPUT_OUTPUT_ROOT`, `INPUT_OUTPUT_SUBDIR`, `INPUT_OUTPUT_TARGET` 같은 output 관련 override도 `INPUT_OUTPUT_PATH` 하나로 줄이는 편이 낫다. 사용자가 스킬을 명시적으로 사용해 feedback log를 남기려는 경우에는 새 raw log 파일 작성 의도가 이미 분명하므로, `INPUT_WRITE_APPROVAL`을 별도 required 변수로 두지 않아야 한다.

## 실제 동작 (Actual Behavior)

현재 스킬 문서는 `INPUT_FEEDBACK_SCOPE`와 `INPUT_FEEDBACK_SOURCE`를 별도 required 입력으로 나누고, `INPUT_OUTPUT_TARGET`, `INPUT_OUTPUT_ROOT`, `INPUT_OUTPUT_SUBDIR`를 optional 입력으로 따로 노출한다. 또한 `INPUT_WRITE_APPROVAL`을 required 입력으로 두어, 스킬 사용자가 이미 raw feedback logging을 요청한 상황에서도 승인 변수 해석을 추가로 요구한다.

## 근거 (Evidence)

사용자 발화 원문 일부:

> input_feedback_scope, inputfeedbacksource 이거 두개 솔직히 하나여도 충분해. 입력은 정말 직관적이어야해. 이렇게 모호하게 여러개로 나누면 헷갈려.
>
> input_output-* 도 마찬가지야 3개나 있는데 이거 솔직히 하나만 있어도 돼. INPUT_OUTPUT_PATH 이거 하나면 충분해 불필요한 옵션을 막 넣어서 일부로 복잡하게 하지마. 심플하게 해야해.
>
> input_write_approval하.. 스킬을 사용하려고하면당연히 필요한건데 뭐하러 승인을 받냐... 이런거 반복적인거니까 넣지마.

대상 파일: `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md`

## 실패 범주 (Failure Categories)

- `actionability`
- `verbosity`
- `specificity`
- `skill-workflow`

## 심각도 (Severity)

medium

스킬 실행 자체를 막지는 않지만, 핵심 workflow가 “raw feedback을 빠르게 남긴다”인 스킬에서 사용자가 매번 변수 의미와 승인 조건을 해석하게 만들어 반복 사용성을 떨어뜨린다.

## 후보 Agent 규칙 (Candidate Agent Rule)

반복 사용 스킬의 입력 계약은 사용자가 실제로 고르는 최소 의미 단위로만 노출하고, source/scope처럼 함께 결정되는 값은 하나로 합치며, 명시적 스킬 호출 자체가 충분한 의도 표명인 경우 별도 approval 변수를 만들지 않는다.

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] `INPUT_FEEDBACK_SCOPE`와 `INPUT_FEEDBACK_SOURCE`를 하나의 source 입력으로 합칠 수 있는지 확인한다.
- [ ] output override는 `INPUT_OUTPUT_PATH` 하나로 표현하고 root/subdir/target 분기는 workflow 내부 정책으로 내린다.
- [ ] 스킬 호출 자체가 raw feedback file 작성 요청인 경우 `INPUT_WRITE_APPROVAL` 같은 반복 승인 변수를 제거한다.
- [ ] approval이 필요한 것은 destructive, external delivery, credential, production mutation처럼 별도 안전 경계가 있는 행동으로 제한한다.
