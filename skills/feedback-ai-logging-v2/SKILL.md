---
name: feedback-ai-logging-v2
description: AI 또는 agent 출력·workflow 불만족 사건을 raw feedback Markdown으로 남겨야 할 때 사용합니다. 현재/과거 세션, transcript, 파일에서 기대와 실제 차이, 근거, 후보 규칙을 사건 단위로 기록하고 중복·hash·path 검증을 수행합니다.
version: 2.2.0
author: Agent
license: MIT
metadata:
  tags: [feedback, quality, logging, raw-data]
  related_skills: [llm-wiki, rubric-design, skill-creator-for-stark]
---

# AI 피드백 로깅 v2

## 개요

이 스킬은 사용자가 AI 또는 agent 출력, workflow, 스킬 사용 경험에 대한 불만족·정정·재작업 사건을 나중에 분석 가능한 raw Markdown 로그로 남기고 싶을 때 사용한다. 목표는 즉시 guide, rubric, memory, skill을 고치는 것이 아니라 사건 당시의 기대 동작, 실제 동작, 차이, 근거, 후보 규칙을 깨끗하게 보존하는 것이다.

피드백 로그는 raw data다. 사건 하나마다 Markdown 파일 하나를 만들고, raw log 안에는 승격 상태, 처리 상태, TODO 진행 상황을 쓰지 않는다. 반복 패턴을 규칙, 루브릭, 문서, 스킬 patch로 승격하는 일은 별도 workflow에서 다룬다.

이미 처리한 feedback인지 판단해야 할 때도 raw log를 수정하지 않는다. 처리 여부는 별도 processing ledger에서 `sha256 + consumer + filename`으로 추적한다. 기본 `consumer`는 `feedback-ai-logging-v2`, `skill-creator-for-stark`, `rubric-skill`, `memory` 네 가지만 사용하고, `status`는 `todo`, `done`, `skip`만 사용한다.

## 사용 판단

사용한다:

- 사용자가 “이 실패 기록해”, “feedback으로 남겨”, “이번 세션에서 불만족했던 것 정리해”처럼 AI/agent 품질 사건 기록을 요청할 때.
- 사용자가 특정 날짜 범위, session id, thread, 파일, transcript에서 누락된 feedback 사건을 수확하라고 요청할 때.
- 사용자가 답변의 요구사항 누락, 검증 누락, 포맷 불일치, 맥락 오독, evidence gap을 재발 방지 데이터로 남기려 할 때.
- 사용자가 가벼운 planning correction도 나중에 반복되지 않게 raw feedback으로 남기려 할 때.
- 특정 스킬 사용 중 발생한 불만족을 해당 스킬 디렉터리 내부 `feedback/`에 남기라고 명시할 때.

사용하지 않는다:

- 사용자가 단순히 감정을 표현했지만 기록을 요청하지 않았을 때.
- 피드백이 AI/agent 출력이나 workflow 품질과 무관할 때.
- 사용자가 즉시 memory, rubric, concept page, guide, skill patch를 업데이트하라고만 요청했고 raw 기록 저장 의도가 없을 때.
- 기대 동작, 실제 동작, 차이, 근거, 재발 방지 후보 규칙을 식별할 수 없을 때.
- legal, financial, medical 판단을 대신 결정해야 할 때.

짧은 예시:

- should_trigger: “방금 답변이 요구사항을 빼먹었으니까 이 실패를 기록해.”
- should_trigger: “어제 이후 대화에서 검증 안 하고 완료라고 한 사건들 feedback log로 만들어줘.”
- should_not_trigger: “이 답변을 더 짧게 다시 써줘.” — 단순 재작성 요청이며 실패 기록 요청이 없다.
- should_not_trigger: “이 반복 패턴으로 rubric을 바로 업데이트해.” — raw logging이 아니라 derived artifact 수정이 목적이다.

## 입력 변수

| 변수 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `INPUT_FEEDBACK_SCOPE` | required | 없음 | 기록할 범위다. `current_session`, `session_id`, `date_range`, `provided_transcript`, `provided_files` 중 무엇을 다루는지 명시한다. 없으면 어떤 대화/자료를 수확해야 하는지 알 수 없으므로 중단한다. |
| `INPUT_FEEDBACK_SOURCE` | required | 없음 | 실제로 읽을 원본 위치 또는 현재 컨텍스트다. 예: 현재 대화, session id, thread link, transcript path, log directory. 추측하지 말고 접근 가능한 source만 사용한다. |
| `INPUT_OUTPUT_TARGET` | optional | `global_raw_feedback` | 저장 대상이다. 기본은 feedback wiki의 `raw/feedback`이며, 스킬 사용 불만족을 해당 스킬 안에 저장하라고 명시하면 `skill_local_feedback`으로 처리한다. 값이 바뀌면 path, `source_type`, 중복 검색 범위가 달라진다. |
| `INPUT_OUTPUT_ROOT` | optional | `${FEEDBACK_WIKI_PATH:-${WIKI_PATH:-$HOME/wiki}}` | global raw feedback을 저장할 wiki/root directory다. 사용자가 명시하지 않으면 env var 우선순위를 따르고, domain routing 값은 feedback 목적지로 자동 간주하지 않는다. `skill_local_feedback`에서는 대상 `SKILL_DIR`가 root다. |
| `INPUT_OUTPUT_SUBDIR` | optional | `raw/feedback` | output root 아래 feedback raw log를 둘 상대 경로다. `skill_local_feedback`에서는 `feedback`을 사용한다. 특별한 routing 요구가 없으면 바꾸지 않는다. |
| `INPUT_WRITE_APPROVAL` | required | 없음 | 새 Markdown 파일을 쓸 수 있다는 사용자 승인 범위다. 파일 쓰기 승인이 없으면 후보만 보고하고 중단한다. |

## 출력 변수

| 변수 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `OUTPUT_CREATED_FILES` | required | `[]` | 새로 생성한 feedback Markdown 파일의 절대 경로 목록이다. 중복이나 제외만 발생하면 빈 배열을 보고한다. |
| `OUTPUT_SKIPPED_COUNTS` | required | `{duplicates: 0, non_incidents: 0}` | 기존 raw log와 의미상 같은 사건이라 skip한 수와 evidence 부족·비사건으로 제외한 수다. 중복성과 scope 판단 결과를 후속 검토할 수 있게 한다. |
| `OUTPUT_INCIDENT_SUMMARY` | required | `{}` | 생성한 사건별 slug, severity, categories, source_ref, session_id 요약이다. raw log를 열지 않고도 무엇이 기록됐는지 확인하는 최소 요약이다. |
| `OUTPUT_VALIDATION_RESULT` | required | 없음 | validator, hash check, path check, read-back 결과다. 검증하지 못한 항목은 `unverified`로 명시한다. |
| `OUTPUT_OPEN_QUESTIONS` | optional | `[]` | source 접근 불가, ambiguous duplicate, taxonomy 판단 불확실성 등 남은 질문이다. |
| `OUTPUT_NEXT_ACTIONS` | optional | `[]` | 사용자가 원할 경우 다음에 할 수 있는 승격, rubric 설계, memory/skill patch 같은 후속 작업이다. |

## 필수 환경

| 환경 항목 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `ENV_FILESYSTEM_READ` | required | 현재 workspace 권한 | `INPUT_FEEDBACK_SOURCE`와 기존 feedback 파일을 읽을 수 있어야 한다. 읽을 수 없으면 중복 검사와 evidence 확인이 불가능하다. |
| `ENV_FILESYSTEM_WRITE` | required | 현재 workspace 권한 | 승인된 target 아래 새 Markdown 파일을 쓸 수 있어야 한다. 쓰기 권한이 없으면 후보 보고까지만 수행한다. |
| `ENV_HASH_RUNTIME` | required | Python `hashlib` | closing frontmatter delimiter 뒤의 Markdown body만 대상으로 `sha256`을 계산할 수 있어야 한다. |
| `ENV_VALIDATOR_COMMAND` | required | `python3 scripts/validate-feedback-log.py` | 생성된 Markdown shape, taxonomy, path, hash를 deterministic하게 검증할 수 있어야 한다. |

## 하드 게이트 (Hard Gates)

- Raw immutability gate: 기존 raw feedback file은 append, status update, promotion marker 추가를 하지 않는다.
- One incident one file gate: 파일 하나에는 독립된 feedback 사건 하나만 담는다.
- Evidence completeness gate: expected behavior, actual behavior, mismatch, evidence excerpt, candidate rule이 모두 있어야 새 파일을 만든다.
- Idempotency gate: 쓰기 전에 target 전체에서 같은 session/source와 의미상 같은 incident를 검색한다.
- Routing gate: global feedback은 `raw/feedback/YYYY-MM-DD/`에, skill 사용 불만족은 해당 스킬의 `feedback/YYYY-MM-DD/`에 저장한다. 사용자가 명시한 output directory를 domain wiki default보다 우선한다.
- Hash validation gate: 작성 후 body-only hash와 deterministic validator가 통과해야 completed로 보고한다.
- Raw/derived separation gate: raw log 안에는 처리 상태, 승격 여부, guide/rubric/skill patch 내용을 섞지 않는다.
- Processing ledger gate: 처리 여부 추적이 필요하면 raw log가 아니라 별도 ledger를 사용한다. ledger identity는 `sha256 + consumer + filename`이고 `status`는 `todo`, `done`, `skip`만 허용한다.
- Feedback-derived update ledger gate: raw feedback을 guide, rubric, memory, skill patch 같은 derived artifact 개선에 사용했다면 같은 승인 범위 안에서 해당 `consumer`의 processing ledger entry를 `done` 또는 `skip`으로 기록해야 completed로 보고할 수 있다. ledger를 쓸 수 없으면 `partial` 또는 `blocked`로 보고한다.

## 빠른 중단 조건 (Fast Fail)

- `INPUT_FEEDBACK_SCOPE` 또는 `INPUT_FEEDBACK_SOURCE`가 없어 수확 범위가 불명확하다.
- `INPUT_WRITE_APPROVAL`이 없어 새 파일 쓰기 승인이 없다.
- output root 또는 skill-local target directory를 결정할 수 없고 사용자에게 물어볼 수도 없다.
- source를 읽을 수 없어 evidence를 확인할 수 없다.
- 기존 target feedback files를 읽을 수 없어 중복 검사가 불가능하다.
- validator 또는 hash 계산을 실행할 수 없다.
- credential, secret, unrelated private state를 읽어야만 session id를 찾을 수 있다.
- 사용자가 raw log와 derived guide/rubric/skill patch를 같은 파일에 섞으라고 요구한다.

## 작업 절차 (Workflow)

1. **입력 정리와 승인 확인**
   - `INPUT_` 값을 채우고 `확인됨`, `추정`, `미확인`으로 구분한다.
   - 파일 쓰기, 외부 delivery, credential 사용, destructive action은 별도 승인 없이는 하지 않는다.
   - 단순 read-only source inspection, 기존 log 중복 검색, validator availability check는 불필요하게 묻지 말고 수행한다.

2. **환경 확인**
   - `ENV_` 항목과 `scripts/validate-feedback-log.py` 실행 가능 여부를 확인한다.
   - target이 `global_raw_feedback`인지 `skill_local_feedback`인지 확정한다.

3. **출력 경로 결정**
   - `global_raw_feedback`: `INPUT_OUTPUT_ROOT/INPUT_OUTPUT_SUBDIR/YYYY-MM-DD/`를 사용한다. 자세한 기준은 `references/output-routing.md`를 따른다.
   - `skill_local_feedback`: 대상 skill directory 내부 `feedback/YYYY-MM-DD/`를 사용한다.
   - 생성 파일 skeleton은 `templates/feedback-log.template.md`, field 의미와 hash 기준은 `references/file-format.md`를 따른다.

4. **session/source 식별**
   - 명시된 session/thread/link/file id를 우선 사용한다.
   - 안전한 source metadata가 있으면 사용한다.
   - 없으면 `unknown-session`으로 fallback하고 `source_ref`에 이유를 남긴다.

5. **후보 사건 수집**
   - source에서 사용자 정정, 불만족, 재작업, 검증 누락, 포맷 불일치, scope mismatch, evidence gap, planning correction을 찾는다.
   - 날짜 범위나 여러 세션이면 `references/cross-session-harvest.md`를 따른다.
   - 후보가 많으면 session/date shard로 나누어 subagent가 candidate JSON만 반환하게 하고, parent가 최종 판단한다.

6. **사건 필터링과 분리**
   - expected behavior, actual behavior, mismatch, evidence, candidate rule이 있는 후보만 남긴다.
   - 정상 요구사항 변경과 단순 취향 변경은 제외한다.
   - planning correction 기준은 `references/incident-selection.md`를 따른다.

7. **중복 검사**
   - target 전체의 기존 `feedback/**` 또는 `raw/feedback/**` 파일을 검색한다.
   - filename만 보지 말고 Situation, Expected Behavior, Evidence, Candidate Agent Rule 의미를 비교한다.
   - 중복이면 새 파일을 만들지 않고 `OUTPUT_SKIPPED_COUNTS.duplicates`에 반영한다.

8. **파일 작성**
   - 사건마다 Markdown body를 먼저 작성한다.
   - body-only `sha256`을 계산한다.
   - frontmatter와 body를 합쳐 `{HHMMSS}-{session_id}-{short-slug}.md`로 쓴다.
   - `source_type`은 일반 AI/agent 불만족이면 `ai-dissatisfaction`, skill-local 사건이면 `skill-dissatisfaction`을 사용한다.

9. **검증**
   - `python3 scripts/validate-feedback-log.py <created-files>`를 실행한다.
   - 대표 파일 read-back으로 frontmatter, 제목, semantic sections, hash 기준을 확인한다.
   - 실패하면 completed로 보고하지 말고 blocked 또는 partial로 보고한다.

10. **보고와 후속 분리**
    - `OUTPUT_` 값을 채워 생성, 중복 skip, 비사건 skip, 검증 결과, 남은 문제를 보고한다.
    - raw log 생성과 derived rule/rubric/skill patch는 다음 단계로 분리한다.

11. **processing ledger 분리**
    - raw feedback의 처리 여부를 추적해야 하면 feedback 파일을 수정하지 않고 별도 ledger를 사용한다.
    - skill-local feedback은 `<SKILL_DIR>/history/feedback-processing-ledger.jsonl`을 기본 위치로 둔다.
    - global raw feedback은 feedback wiki의 `output/feedback-processing-ledger.jsonl`을 기본 위치로 둔다.
    - ledger entry의 최소 key는 `sha256 + consumer + filename`이다. `target_artifact`는 경로 이동에 취약하므로 넣지 않는다.
    - `consumer`는 처음에는 `feedback-ai-logging-v2`, `skill-creator-for-stark`, `rubric-skill`, `memory`만 사용한다.
    - `status`는 `todo`, `done`, `skip`만 사용한다. `done`에는 가능하면 evidence를, `skip`에는 decision 이유를 남긴다.
    - raw feedback을 derived artifact 개선에 사용했다면 artifact write와 ledger write를 같은 작업 단위로 검증한다. 예: 루브릭 개선에 사용한 feedback은 `consumer=rubric-skill`, memory 반영은 `consumer=memory`, skill 개선은 해당 skill consumer로 기록한다.
    - ledger write를 못 했으면 raw feedback 처리를 완료로 보고하지 않고, 실패 command/path와 복구 행동을 분리해 보고한다.

12. **스킬 사용 불만족 feedback 처리**
    - 이 스킬 자체 또는 다른 스킬 사용 중 사용자가 “스킬 피드백에 남겨”라고 명시하면 해당 스킬의 `feedback/` 아래에 raw log를 저장한다.
    - 중복 검사, body-only `sha256`, `read-back`, validator 검증을 동일하게 적용한다.
    - 개별 스킬 개선 후보와 `skill-creator-for-stark` 개선 후보를 raw log 본문에 처리 상태로 쓰지 않고 최종 보고의 `OUTPUT_NEXT_ACTIONS`에만 분리한다.

## Subagent 병렬화

- 여러 session, 긴 transcript, 많은 후보 파일을 수확할 때는 범위별 shard를 subagent에 맡길 수 있다.
- subagent는 파일을 쓰지 않고 candidate incident JSON만 반환한다.
- parent는 source read-back, taxonomy 정규화, 중복 판단, 파일 작성, hash/validator 검증을 직접 수행한다.
- 작은 현재 세션 feedback 1–3건은 subagent 없이 처리한다.

## 출력 템플릿

최종 보고는 아래 구조를 따른다.

```text
상태: completed | partial | blocked | unverified
OUTPUT_CREATED_FILES: [...]
OUTPUT_SKIPPED_COUNTS: {duplicates: N, non_incidents: N}
OUTPUT_INCIDENT_SUMMARY: <slug/severity/categories/source_ref/session_id>
OUTPUT_VALIDATION_RESULT: <validator/hash/read-back 실제 결과>
실패 보고: {failed_command_or_tool, likely_cause, impact, recovery_action}
OUTPUT_OPEN_QUESTIONS: [...]
OUTPUT_NEXT_ACTIONS: [...]
```

## 보안과 프라이버시

- API key, token, cookie, password, private URL, credential은 raw evidence에 그대로 저장하지 않는다.
- source excerpt는 재현에 필요한 최소 범위만 남긴다.
- 외부 delivery, production mutation, credential 사용은 이 스킬의 기본 workflow가 아니다.
- raw log에는 처리 상태, 승격 여부, TODO 진행 상태를 쓰지 않는다.
- 처리 상태가 필요하면 raw log를 수정하지 않고 processing ledger에만 기록한다.

## 커밋 주의사항 (Commit Pitfalls)

- raw feedback log 생성과 derived guide/rubric/skill update를 같은 작업으로 섞지 않는다.
- unrelated wiki files나 기존 raw logs를 수정하지 않는다.
- 중복 검사 없이 파일을 여러 개 만들지 않는다.
- 검증 실패 상태를 완료로 보고하지 않는다.
- generated raw log와 skill source 변경을 같은 commit에 넣을지 여부는 사용자의 승인 범위에 맞춘다.
- skill-local feedback 경로와 global `raw/feedback` 경로를 혼동하지 않는다.
- processing ledger를 쓰더라도 raw feedback file에 status field를 추가하지 않는다.

## 검증 체크리스트 (Verification Checklist)

- [ ] `SKILL.md`가 존재하고 frontmatter 필수 key가 있다.
- [ ] `name`이 directory basename과 일치한다.
- [ ] `description`이 1024자 이하이며 trigger condition을 설명한다.
- [ ] `INPUT_`, `OUTPUT_`, `ENV_` 변수가 required/optional/default/설명을 포함한다.
- [ ] `ENV_`는 입력값이 아니라 필요한 도구/권한/명령 조건으로 설명된다.
- [ ] `Hard Gates`와 `Fast Fail`이 domain-specific raw feedback logging 조건만 다룬다.
- [ ] trigger 판단이 `사용 판단` 한 섹션에 통합되어 있다.
- [ ] deterministic 검증은 `scripts/validate-feedback-log.py`로 분리되어 있다.
- [ ] 긴 세부 기준은 `references/`로 분리되어 있다.
- [ ] 생성 파일 skeleton은 `templates/feedback-log.template.md`에 있고, format 설명은 `references/file-format.md`에 있다.
- [ ] 스킬 사용 불만족을 해당 스킬 `feedback/`에 raw log로 남기는 절차가 포함되어 있다.
- [ ] 생성된 feedback log가 있다면 validator, hash check, read-back이 통과한다.
- [ ] 처리 여부를 추적해야 한다면 raw log가 아니라 processing ledger를 사용하며, identity가 `sha256 + consumer + filename`이다.
- [ ] validator가 `references/file-format.md`와 `templates/feedback-log.template.md`의 필수 frontmatter field와 body section을 모두 검증한다.
- [ ] 실패 보고가 필요한 경우 failed command, likely cause, impact, recovery action을 분리한다.
- [ ] 최종 응답이 `OUTPUT_` 변수와 대응된다.

## 최종 응답 체크리스트 (Final Response Checklist)

- `INPUT_` 값과 사용한 default.
- `OUTPUT_CREATED_FILES` 경로.
- `OUTPUT_SKIPPED_COUNTS`와 제외 사유.
- severity/categories 요약.
- validator, hash, read-back 검증 결과.
- skill-local feedback을 사용했다면 대상 `feedback/` 저장 기준.
- processing ledger를 사용했다면 `consumer`, `status`, identity 기준.
- 미확인 사항과 다음 단계.
