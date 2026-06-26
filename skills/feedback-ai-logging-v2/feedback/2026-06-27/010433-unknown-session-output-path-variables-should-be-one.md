---
type: feedback-log
source_type: skill-dissatisfaction
source_platform: cli
source_ref: "current conversation; skill=feedback-ai-logging-v2; target=SKILL.md"
session_id: "unknown-session"
ingested: 2026-06-27
created_at: 2026-06-27T01:04:33+09:00
task_type: skill-usage
agent_or_model: "Hermes Agent"
severity: medium
categories: [actionability, verbosity, specificity, skill-workflow]
sha256: "be06bc7954fc5966f8728af8fa5294c21022d0374afe6ee6106b4829dcb3436d"
---
# feedback-ai-logging-v2 output 관련 입력이 세 개로 과분화됨

## 상황 (Situation)

사용자가 `feedback-ai-logging-v2` 스킬 자체의 feedback 기록 방식을 검토하면서, 현재 스킬 문서와 직전 생성 로그가 너무 큰 단위로 묶이고 실제 스킬 원문 근거를 충분히 담지 못한다고 지적했다. 대상 스킬 파일은 `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md`다.

## 불만족한 점 (Dissatisfaction)

`INPUT_OUTPUT_TARGET`, `INPUT_OUTPUT_ROOT`, `INPUT_OUTPUT_SUBDIR`가 별도 옵션으로 노출되어 output 위치 지정이 실제 필요보다 복잡하다.

## 기대한 동작 (Expected Behavior)

output override는 `INPUT_OUTPUT_PATH` 하나로 충분해야 한다. 기본 저장 위치는 workflow 내부 규칙으로 정하고, 사용자가 바꾸고 싶을 때만 절대/상대 path 하나를 제공하게 해야 한다.

## 실제 동작 (Actual Behavior)

SKILL.md는 output 위치 결정을 target/root/subdir 세 변수로 나누고, 각 값 변화가 path/source_type/중복 검색 범위에 영향을 준다고 설명한다.

## 근거 (Evidence)

사용자 발화:

> input_output-* 도 마찬가지야 3개나 있는데 이거 솔직히 하나만 있어도 돼. INPUT_OUTPUT_PATH 이거 하나면 충분해 불필요한 옵션을 막 넣어서 일부로 복잡하게 하지마. 심플하게 해야해.

스킬 원문 근거:

SKILL.md line 51: `INPUT_OUTPUT_TARGET` optional — `global_raw_feedback`/`skill_local_feedback` 저장 대상을 따로 지정.
SKILL.md line 52: `INPUT_OUTPUT_ROOT` optional — global raw feedback root를 따로 지정.
SKILL.md line 53: `INPUT_OUTPUT_SUBDIR` optional — root 아래 상대 subdir를 따로 지정.
SKILL.md lines 108-111: output path는 root/subdir/skill-local 분기로 결정된다고 설명함.

## 실패 범주 (Failure Categories)

- `actionability`
- `verbosity`
- `specificity`
- `skill-workflow`

## 심각도 (Severity)

medium

## 후보 Agent 규칙 (Candidate Agent Rule)

출력 위치 override는 `INPUT_OUTPUT_PATH` 하나로 표현하고, global/skill-local routing의 기본값과 파생값은 내부 정책으로 처리한다.

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] output 관련 입력이 하나의 path로 대체 가능한지 확인한다.
- [ ] 기본 routing 규칙을 입력 변수로 노출하지 않는다.
