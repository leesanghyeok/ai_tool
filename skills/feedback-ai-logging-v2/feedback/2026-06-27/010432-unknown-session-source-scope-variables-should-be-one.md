---
type: feedback-log
source_type: skill-dissatisfaction
source_platform: cli
source_ref: "current conversation; skill=feedback-ai-logging-v2; target=SKILL.md"
session_id: "unknown-session"
ingested: 2026-06-27
created_at: 2026-06-27T01:04:32+09:00
task_type: skill-usage
agent_or_model: "Hermes Agent"
severity: medium
categories: [actionability, verbosity, specificity, skill-workflow]
sha256: "b00ffd4b6311e8baf55ee4814c64143403ceef0ec3fb90aa8efae88f85290ba4"
---
# feedback-ai-logging-v2 source와 scope 입력이 과분화됨

## 상황 (Situation)

사용자가 `feedback-ai-logging-v2` 스킬 자체의 feedback 기록 방식을 검토하면서, 현재 스킬 문서와 직전 생성 로그가 너무 큰 단위로 묶이고 실제 스킬 원문 근거를 충분히 담지 못한다고 지적했다. 대상 스킬 파일은 `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md`다.

## 불만족한 점 (Dissatisfaction)

`INPUT_FEEDBACK_SCOPE`와 `INPUT_FEEDBACK_SOURCE`가 별도 required 변수로 나뉘어 있어, 사용자가 하나의 직관적 원본/범위 입력으로 이해할 수 있는 내용을 불필요하게 두 번 결정해야 한다.

## 기대한 동작 (Expected Behavior)

source/scope는 하나의 입력으로 합쳐야 한다. 예: `INPUT_FEEDBACK_SOURCE` 또는 더 단순한 `INPUT_SOURCE` 하나가 현재 대화, session id, date range, transcript path, file path를 모두 표현하게 하고, 구체 타입 판별은 workflow 내부에서 처리한다.

## 실제 동작 (Actual Behavior)

SKILL.md는 `INPUT_FEEDBACK_SCOPE`와 `INPUT_FEEDBACK_SOURCE`를 모두 required로 요구한다.

## 근거 (Evidence)

사용자 발화:

> input_feedback_scope, inputfeedbacksource 이거 두개 솔직히 하나여도 충분해. 입력은 정말 직관적이어야해. 이렇게 모호하게 여러개로 나누면 헷갈려.

스킬 원문 근거:

SKILL.md line 49: `INPUT_FEEDBACK_SCOPE` required — 기록할 범위(`current_session`, `session_id`, `date_range`, `provided_transcript`, `provided_files`)를 명시하라고 함.
SKILL.md line 50: `INPUT_FEEDBACK_SOURCE` required — 실제로 읽을 원본 위치 또는 현재 컨텍스트를 별도로 요구함.

## 실패 범주 (Failure Categories)

- `actionability`
- `verbosity`
- `specificity`
- `skill-workflow`

## 심각도 (Severity)

medium

## 후보 Agent 규칙 (Candidate Agent Rule)

피드백 로깅 스킬의 source/scope 계약은 사용자가 한 번에 제공하는 원본 참조 하나로 유지하고, source type 분류는 내부 workflow가 판별한다.

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] source와 scope가 함께 결정되는 값인지 확인한다.
- [ ] 하나의 source 입력으로 충분한 경우 required 변수를 쪼개지 않는다.
