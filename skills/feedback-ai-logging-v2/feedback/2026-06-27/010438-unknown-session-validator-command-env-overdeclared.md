---
type: feedback-log
source_type: skill-dissatisfaction
source_platform: cli
source_ref: "current conversation; skill=feedback-ai-logging-v2; target=SKILL.md"
session_id: "unknown-session"
ingested: 2026-06-27
created_at: 2026-06-27T01:04:38+09:00
task_type: skill-usage
agent_or_model: "Hermes Agent"
severity: medium
categories: [specificity, context-misread, skill-workflow]
sha256: "f2a6f30127240e546e79aa436cb8314d8e3bf92d9224ea88bae6ab1bca157bdb"
---
# feedback-ai-logging-v2가 내장 validator를 필수 환경으로 오분류함

## 상황 (Situation)

사용자가 `feedback-ai-logging-v2` 스킬 자체의 feedback 기록 방식을 검토하면서, 현재 스킬 문서와 직전 생성 로그가 너무 큰 단위로 묶이고 실제 스킬 원문 근거를 충분히 담지 못한다고 지적했다. 대상 스킬 파일은 `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/SKILL.md`다.

## 불만족한 점 (Dissatisfaction)

`ENV_VALIDATOR_COMMAND`는 스킬 패키지가 가지고 있는 validator script를 실행하는 절차이지, 사용자가 별도로 갖춰야 할 필수 환경으로 보기 어렵다.

## 기대한 동작 (Expected Behavior)

스킬이 제대로 설치되어 있으면 `scripts/validate-feedback-log.py`는 skill directory 내부에 있어야 한다. 따라서 validator command는 workflow의 검증 단계 또는 bundled script로 설명하고, 필수 환경 변수에서 제거해야 한다.

## 실제 동작 (Actual Behavior)

SKILL.md는 `ENV_VALIDATOR_COMMAND`를 required 필수 환경으로 두고 `python3 scripts/validate-feedback-log.py`를 기본값으로 적는다. workflow에서도 validator availability check를 환경 확인처럼 다룬다.

## 근거 (Evidence)

사용자 발화:

> ENV_VALIDATOR_COMMAND이건 스킬에서 가지고 있는건데 제대로 스킬 설치햇으면 당연히 있는거잖아 이런건 필수환경 대상이 아니야.

스킬 원문 근거:

SKILL.md line 74: `ENV_VALIDATOR_COMMAND` required — `python3 scripts/validate-feedback-log.py`를 필수 환경으로 명시.
SKILL.md line 105: `ENV_` 항목과 `scripts/validate-feedback-log.py` 실행 가능 여부를 확인한다고 설명.
SKILL.md line 140: 검증 단계에서 `python3 scripts/validate-feedback-log.py <created-files>`를 실행한다고 설명.

## 실패 범주 (Failure Categories)

- `specificity`
- `context-misread`
- `skill-workflow`

## 심각도 (Severity)

medium

## 후보 Agent 규칙 (Candidate Agent Rule)

스킬에 bundled된 validator/script는 `ENV_` 필수 환경이 아니라 검증 절차의 도구로 설명한다.

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] validator가 skill package 내부 파일인지 확인한다.
- [ ] bundled script를 사용자가 제공할 환경 변수처럼 표현하지 않는다.
