---
name: feedback-ai-logging-v2
description: AI 또는 agent 출력에 대한 불만족 사건을 raw feedback Markdown으로 기록해야 할 때 사용합니다. 현재 세션이나 지정된 과거 세션에서 기대/실제 차이, 근거, 후보 규칙을 사건 단위로 남기고 중복 기록을 피합니다.
version: 2.0.0
author: Agent
license: MIT
metadata:
  tags: [feedback, quality, logging, raw-data]
  related_skills: [llm-wiki, rubric-design]
---

# AI 피드백 로깅 v2

## 개요

이 스킬은 사용자가 AI 또는 agent 출력에 대한 불만족, 수정 요구, 재작업 사건을 나중에 분석 가능한 raw Markdown 로그로 남기고 싶을 때 사용한다. 목적은 즉시 가이드, 루브릭, 메모리를 고치는 것이 아니라 사건 당시의 기대, 실제 동작, 근거, 후보 규칙을 깨끗하게 보존하는 것이다.

피드백 로그는 raw data다. 사건 하나마다 Markdown 파일 하나를 만들고, raw log 안에는 승격 상태나 처리 상태를 쓰지 않는다. 반복 패턴을 규칙, 루브릭, 문서로 승격하는 일은 별도 workflow에서 다룬다.

## 사용 시점

- 사용자가 “이 실패 기록해”, “feedback으로 남겨”, “이번 세션에서 불만족했던 것 정리해”처럼 AI/agent 품질 사건 기록을 요청할 때.
- 사용자가 특정 날짜 범위, session id, thread, 파일, transcript에서 누락된 feedback 사건을 수확하라고 요청할 때.
- 사용자가 답변의 요구사항 누락, 검증 누락, 포맷 불일치, 맥락 오독, evidence gap을 재발 방지 데이터로 남기려 할 때.
- 사용자가 가벼운 planning correction도 나중에 반복되지 않게 raw feedback으로 남기려 할 때.

## 사용하지 말아야 할 때

- 사용자가 단순히 감정을 표현했지만 기록을 요청하지 않았을 때.
- 피드백이 AI/agent 출력이나 workflow 품질과 무관할 때.
- 사용자가 즉시 memory, rubric, concept page, guide를 업데이트하라고 요청했을 때.
- 기대 동작, 실제 동작, 차이, 근거, 재발 방지 후보 규칙을 식별할 수 없을 때.
- legal, financial, medical 판단을 대신 결정해야 할 때.

## 입력 변수

| 변수 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `INPUT_FEEDBACK_SCOPE` | required | 없음 | 기록할 범위다. `current_session`, `session_id`, `date_range`, `provided_transcript`, `provided_files` 중 무엇을 다루는지 명시한다. 이 값이 없으면 어떤 대화/자료를 수확해야 하는지 알 수 없으므로 중단한다. |
| `INPUT_FEEDBACK_SOURCE` | required | 없음 | 실제로 읽을 원본 위치 또는 현재 컨텍스트다. 예: 현재 대화, session id, thread link, transcript path, log directory. 추측하지 말고 접근 가능한 source만 사용한다. |
| `INPUT_OUTPUT_ROOT` | optional | `${FEEDBACK_WIKI_PATH:-${WIKI_PATH:-$HOME/wiki}}` | feedback log를 저장할 wiki/root directory다. 사용자가 명시하지 않으면 env var 우선순위를 따르고, domain routing 값은 feedback 목적지로 자동 간주하지 않는다. |
| `INPUT_OUTPUT_SUBDIR` | optional | `raw/feedback` | output root 아래 feedback raw log를 둘 상대 경로다. 보통 바꾸지 않는다. |
| `INPUT_TIMEZONE` | optional | system local timezone | `created_at`, 날짜 폴더, 파일명 `HHMMSS`를 만들 때 사용할 timezone이다. 현재 시스템 timezone을 확인해 기본값으로 쓴다. |
| `INPUT_SESSION_ID_POLICY` | optional | `discover_then_unknown` | session/conversation/thread id를 찾는 방식이다. 사용자가 명시한 id, source metadata, 안전한 환경값 순으로 찾고, 없으면 `unknown-session`을 쓴다. |
| `INPUT_IDEMPOTENCY_POLICY` | optional | `semantic_incident_key` | 중복 방지 방식이다. 같은 session/source의 기존 raw logs를 읽고 expected/actual/rule 의미가 같은 사건은 새 파일을 만들지 않는다. |
| `INPUT_MIN_SEVERITY` | optional | `low` | 기록할 최소 severity다. 기본값은 가벼운 planning correction도 보존하기 위해 `low`다. |
| `INPUT_CATEGORY_SET` | optional | built-in taxonomy | 사용할 failure category 집합이다. 특별한 이유가 없으면 이 스킬의 controlled taxonomy를 사용한다. |
| `INPUT_WRITE_APPROVAL` | required | 없음 | 새 Markdown 파일을 쓸 수 있다는 사용자 승인 범위다. 파일 쓰기 승인이 없으면 후보만 보고하고 중단한다. |
| `INPUT_VALIDATION_MODE` | optional | `script_then_readback` | 작성 후 검증 방식이다. 기본값은 deterministic validator 실행 후 대표 파일 read-back이다. |

## 출력 변수

| 변수 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `OUTPUT_CREATED_FILES` | required | `[]` | 새로 생성한 feedback Markdown 파일의 절대 경로 목록이다. 중복이나 제외만 발생하면 빈 배열을 보고한다. |
| `OUTPUT_SKIPPED_DUPLICATES` | required | `0` | 기존 raw log와 의미상 같은 사건이라 새 파일을 만들지 않은 후보 수다. |
| `OUTPUT_SKIPPED_NON_INCIDENTS` | required | `0` | 정상 요구사항 변경, 단순 확인, evidence 부족 등으로 제외한 후보 수다. |
| `OUTPUT_INCIDENT_SUMMARY` | required | `{}` | 생성한 사건별 slug, severity, categories, source_ref, session_id 요약이다. |
| `OUTPUT_VALIDATION_RESULT` | required | 없음 | validator, hash check, path check, read-back 결과다. 검증하지 못한 항목은 `unverified`로 명시한다. |
| `OUTPUT_OPEN_QUESTIONS` | optional | `[]` | source 접근 불가, ambiguous duplicate, taxonomy 판단 불확실성 등 남은 질문이다. |
| `OUTPUT_NEXT_ACTIONS` | optional | `[]` | 사용자가 원할 경우 다음에 할 수 있는 승격, rubric 설계, memory/skill patch 같은 후속 작업이다. |

## 필수 환경

| 환경 항목 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `ENV_FILESYSTEM_READ` | required | 현재 workspace 권한 | `INPUT_FEEDBACK_SOURCE`와 기존 `raw/feedback` 파일을 읽을 수 있어야 한다. 읽을 수 없으면 중복 검사와 evidence 확인이 불가능하다. |
| `ENV_FILESYSTEM_WRITE` | required | 현재 workspace 권한 | `INPUT_OUTPUT_ROOT/INPUT_OUTPUT_SUBDIR` 아래 새 Markdown 파일을 쓸 수 있어야 한다. 쓰기 권한이 없으면 후보 보고까지만 수행한다. |
| `ENV_TIME_COMMAND` | required | `date` 또는 표준 시간 API | local date/time과 timezone offset을 계산할 수 있어야 한다. |
| `ENV_HASH_COMMAND` | required | Python `hashlib` | body-only `sha256`을 계산할 수 있어야 한다. |
| `ENV_VALIDATOR_COMMAND` | required | `python3 scripts/validate-feedback-log.py` | 생성된 Markdown shape, taxonomy, path, hash를 deterministic하게 검증할 수 있어야 한다. |
| `ENV_SESSION_LOOKUP_TOOL` | optional | 현재 대화 context | 과거 세션이나 외부 transcript를 수확할 때 필요한 read-only lookup 도구다. 현재 세션만 수확하면 없어도 된다. |

## Hard Gates

- Metadata gate: `name`은 directory basename과 같고 1-64자 lowercase hyphen slug여야 한다. `description`은 1-1024자, 가능하면 약 100 words 이하로 유지한다.
- Body size gate: `SKILL.md` body는 5,000 words 이하로 유지하고 긴 taxonomy/예시는 references로 분리한다.
- Raw immutability gate: 기존 raw feedback file은 append, status update, promotion marker 추가를 하지 않는다.
- One incident one file gate: 파일 하나에는 독립된 feedback 사건 하나만 담는다.
- Evidence gate: expected behavior, actual behavior, mismatch, evidence excerpt, candidate rule이 모두 있어야 새 파일을 만든다.
- Idempotency gate: 쓰기 전에 기존 `raw/feedback/**`에서 같은 session/source와 의미상 같은 incident를 검색한다.
- Validation gate: 작성 후 body-only hash와 deterministic validator가 통과해야 완료로 보고한다.

## Fast Fail

- `INPUT_FEEDBACK_SCOPE` 또는 `INPUT_FEEDBACK_SOURCE`가 없어 수확 범위가 불명확하다.
- `INPUT_WRITE_APPROVAL`이 없어 새 파일 쓰기 승인이 없다.
- output root를 결정할 수 없고 사용자에게 물어볼 수도 없다.
- source를 읽을 수 없어 evidence를 확인할 수 없다.
- 기존 raw logs를 읽을 수 없어 중복 검사가 불가능하다.
- validator 또는 hash 계산을 실행할 수 없다.
- credential, secret, unrelated private state를 읽어야만 session id를 찾을 수 있다.

## Workflow

1. **입력 정리**
   - `INPUT_` 값을 표로 채운다.
   - required 값이 없으면 fast fail한다.
   - optional 값은 default를 명시하고, 실제로 사용한 값은 최종 보고에 남긴다.

2. **환경 확인**
   - `ENV_` 항목을 확인한다.
   - 이 섹션의 `ENV_`는 사용자가 제공하는 입력이 아니라 스킬 실행에 필요한 도구/권한/명령 조건이다.

3. **출력 경로 결정**
   - `INPUT_OUTPUT_ROOT`와 `INPUT_OUTPUT_SUBDIR`로 target directory를 계산한다.
   - 사용자가 feedback 목적지로 명시하지 않은 domain wiki routing을 기본값으로 쓰지 않는다.
   - 자세한 기준은 `references/output-routing.md`를 따른다.

4. **session/source 식별**
   - 명시된 session/thread/link/file id를 우선 사용한다.
   - 안전한 source metadata가 있으면 사용한다.
   - 없으면 `unknown-session`으로 fallback하고 `source_ref`에 이유를 남긴다.

5. **후보 사건 수집**
   - source에서 사용자 정정, 불만족, 재작업, 검증 누락, 포맷 불일치, scope mismatch, evidence gap, planning correction을 찾는다.
   - 날짜 범위나 여러 세션이면 `references/cross-session-harvest.md`를 따른다.

6. **사건 필터링과 분리**
   - expected behavior, actual behavior, mismatch, evidence, candidate rule이 있는 후보만 남긴다.
   - 정상 요구사항 변경과 단순 취향 변경은 제외한다.
   - planning correction 기준은 `references/incident-selection.md`를 따른다.

7. **중복 검사**
   - 기존 `raw/feedback/**` 파일을 검색한다.
   - filename만 보지 말고 Situation, Expected Behavior, Evidence, Candidate Agent Rule 의미를 비교한다.
   - 중복이면 새 파일을 만들지 않고 `OUTPUT_SKIPPED_DUPLICATES`에 반영한다.

8. **파일 작성**
   - 사건마다 Markdown body를 먼저 작성한다.
   - body-only `sha256`을 계산한다.
   - frontmatter와 body를 합쳐 `raw/feedback/YYYY-MM-DD/{HHMMSS}-{session_id}-{short-slug}.md`에 쓴다.
   - 파일명 규칙은 `references/file-format.md`를 따른다.

9. **검증**
   - `scripts/validate-feedback-log.py`를 실행한다.
   - 대표 파일 read-back으로 frontmatter, 제목, semantic sections를 확인한다.
   - 실패하면 completed로 보고하지 말고 blocked 또는 partial로 보고한다.

10. **보고**
    - `OUTPUT_` 값을 채워 생성, 중복 skip, 비사건 skip, 검증 결과, 남은 문제를 보고한다.

## Trigger Examples

### should_trigger

- “이번 세션에서 내가 고치라고 한 것들 raw feedback으로 남겨줘.”
- “어제 이후 대화에서 검증 안 하고 완료라고 한 사건들 feedback log로 만들어줘.”
- “방금 답변이 요구사항을 빼먹었으니까 이 실패를 기록해.”
- “이 스킬 설계에서 기본값/변수화 누락한 것도 피드백 사건으로 남겨.”

### should_not_trigger

- “이 답변을 더 짧게 다시 써줘.” 단순 재작성 요청이며 실패 기록 요청이 없다.
- “이 선호를 앞으로 기억해.” raw feedback log보다 memory 판단이 우선이다.
- “이 반복 패턴으로 rubric을 바로 업데이트해.” raw logging이 아니라 rubric workflow가 목적이다.
- “이 파일의 맞춤법만 고쳐줘.” AI/agent 품질 사건 기록이 아니다.

## Commit Pitfalls

- raw feedback log 생성과 derived guide/rubric update를 같은 작업으로 섞지 않는다.
- unrelated wiki files나 기존 raw logs를 수정하지 않는다.
- 중복 검사 없이 파일을 여러 개 만들지 않는다.
- 검증 실패 상태를 완료로 보고하지 않는다.
- generated raw log와 skill source 변경을 같은 commit에 넣을지 여부는 사용자의 승인 범위에 맞춘다.

## Verification Checklist

- [ ] `SKILL.md`가 존재하고 frontmatter 필수 key가 있다.
- [ ] `name`이 directory basename과 일치한다.
- [ ] `description`이 1024자 이하이며 trigger condition을 설명한다.
- [ ] `INPUT_`, `OUTPUT_`, `ENV_` 변수가 required/optional/default/설명을 포함한다.
- [ ] `ENV_`는 입력값이 아니라 필요한 도구/권한/명령 조건으로 설명된다.
- [ ] `Hard Gates`와 `Fast Fail`이 있다.
- [ ] `should_trigger` / `should_not_trigger` 예시가 있다.
- [ ] deterministic 검증은 `scripts/validate-feedback-log.py`로 분리되어 있다.
- [ ] 긴 세부 기준은 `references/`로 분리되어 있다.
- [ ] 생성된 feedback log가 있다면 validator가 통과한다.
- [ ] 최종 응답이 `OUTPUT_` 변수와 대응된다.

## Final Response Checklist

- `INPUT_` 값과 사용한 default.
- `OUTPUT_CREATED_FILES` 경로.
- 중복/비사건 skip 수.
- severity/categories 요약.
- validator와 read-back 검증 결과.
- 미확인 사항과 다음 단계.
