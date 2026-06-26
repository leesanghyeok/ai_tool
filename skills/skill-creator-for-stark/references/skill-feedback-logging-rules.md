# 스킬 피드백 로깅 규칙

## 목적

생성되는 모든 스킬은 사용 중 발생한 불만족 사건을 해당 스킬 디렉터리 내부의 `feedback/` 아래에 raw log로 남길 수 있어야 한다. 목표는 개별 스킬의 실패 사례를 누적해 다음 개선 때 evidence로 사용하고, 여러 스킬에 공통으로 반복되는 문제는 `skill-creator-for-stark` 자체의 template, rules, validator 개선 후보로 승격하는 것이다.

## 생성되는 스킬에 포함할 기본 정책

새 스킬 또는 의미 있는 수정 대상 스킬에는 다음 정책을 포함한다.

- 사용자가 “이 스킬이 기대대로 안 됐다”, “이 스킬 사용 경험을 피드백으로 남겨”, “이번 실패를 스킬 피드백에 기록해”처럼 말하면 skill feedback incident로 본다.
- feedback log는 대상 스킬 디렉터리 내부 `feedback/YYYY-MM-DD/{HHMMSS}-{session_id}-{short-slug}.md`에 새 파일로 남긴다.
- 포맷은 `feedback-ai-logging-v2/references/file-format.md`를 기반으로 한다.
- 가능한 경우 `feedback-ai-logging-v2` 스킬을 함께 사용해 사건 선정, 중복 검사, body-only `sha256`, validator 절차를 따른다.
- 대상 스킬 자체 개선과 raw feedback logging을 한 파일에 섞지 않는다. raw log는 사건 데이터이고, 개선 반영은 별도 skill patch 또는 creator 개선 workflow에서 수행한다.

## 디렉터리와 파일 포맷

경로 규칙:

```text
<SKILL_DIR>/feedback/YYYY-MM-DD/{HHMMSS}-{session_id}-{short-slug}.md
```

frontmatter와 body section은 `feedback-ai-logging-v2/references/file-format.md`와 호환되게 작성한다. 단, 스킬 내부 feedback임을 분명히 하기 위해 다음 값을 우선 사용한다.

```yaml
type: feedback-log
source_type: skill-dissatisfaction
source_platform: cli
source_ref: "<skill-name>"
session_id: "unknown-session"
task_type: skill-usage
categories: [skill-workflow]
```

본문에는 최소한 다음 section을 둔다.

- `## 상황 (Situation)` — 어떤 스킬을 어떤 목적으로 사용했는지.
- `## 불만족한 점 (Dissatisfaction)` — 사용자가 무엇을 기대와 다르다고 느꼈는지.
- `## 기대한 동작 (Expected Behavior)` — 스킬이 했어야 하는 절차, 산출물, 검증, 경계.
- `## 근거 (Evidence)` — 사용자 발화, tool output, file path, 검증 실패 등 확인 가능한 근거.
- `## 실패 범주 (Failure Categories)` — controlled taxonomy 또는 임시 category.
- `## 심각도 (Severity)` — `low`, `medium`, `high`, `critical` 중 하나.
- `## 후보 Agent 규칙 (Candidate Agent Rule)` — 재발 방지를 위해 스킬 또는 creator에 넣을 수 있는 후보 규칙.
- `## 후보 체크리스트 항목 (Candidate Checklist Items)` — verification/final response checklist 후보.

`sha256`은 closing frontmatter delimiter 뒤의 Markdown body만 대상으로 계산한다.

## 작업 절차에 넣을 내용

생성되는 스킬의 `Workflow` 또는 `Final Response Checklist` 주변에 다음 절차를 반영한다.

1. 스킬 사용 중 사용자의 불만족, 정정, 재작업 요구가 나오면 feedback logging 필요성을 감지한다.
2. 현재 요청이 즉시 수정인지, raw feedback log 저장까지 승인한 것인지 구분한다. 사용자가 “남겨/기록해/로그로 저장해”라고 명시한 경우 해당 스킬 디렉터리 내부 `feedback/` 쓰기를 승인한 것으로 처리한다.
3. `feedback-ai-logging-v2`가 사용 가능하면 로드해 사건 선정, 중복 검사, 포맷, 검증 절차를 따른다.
4. 기존 `feedback/**`에서 같은 session/source와 의미상 같은 incident가 있는지 확인한다.
5. 중복이 아니면 새 feedback log를 작성하고 body-only `sha256`을 계산한다.
6. 가능하면 `feedback-ai-logging-v2/scripts/validate-feedback-log.py` 또는 동등한 parser로 검증하고, 최소한 read-back으로 frontmatter와 필수 section을 확인한다.
7. 개별 스킬 개선 후보와 `skill-creator-for-stark` 개선 후보를 분리해 보고한다.


## 템플릿과 reference 분리

feedback log처럼 스킬이 직접 생성하는 Markdown 파일의 skeleton은 `templates/`에 둔다. `references/`에는 형식 설명, 사건 선정 기준, routing, 중복 판단, taxonomy, migration runbook만 둔다.

- 좋은 배치: `templates/feedback-log.template.md` — frontmatter/body skeleton, 작성자가 복사해 채울 구조.
- 좋은 배치: `references/file-format.md` — field 의미, hash 기준, validator 규칙 설명.
- 나쁜 배치: 생성 산출물 skeleton을 `references/`에만 두고 workflow에서 그 파일을 복사 기준으로 사용하게 하는 것.

개별 스킬 feedback에서 산출물 skeleton 위치 문제가 발견되면, 해당 스킬 수정 후보와 `skill-creator-for-stark` template/rules/validator 개선 후보를 분리해 보고한다.

## Creator 환류 기준

다음은 개별 스킬만 고치는 대신 `skill-creator-for-stark` 개선 후보로 보고한다.

- 여러 스킬에서 같은 feedback category가 반복된다.
- template에 빠진 section, variable, hard gate, validation step 때문에 실패했다.
- 생성된 스킬들이 공통으로 feedback logging 절차를 누락하거나, `feedback/` 디렉터리를 validator가 거부한다.
- 사용자 고정 규칙과 충돌하는 문구가 여러 스킬에 반복 삽입된다.
- 검증 스크립트가 잡아야 할 구조 누락을 놓쳤다.

## 주의사항

- raw feedback log에는 처리 상태, 승격 여부, TODO 진행 상황을 쓰지 않는다.
- secret, token, private URL, credential 원문을 feedback log에 저장하지 않는다.
- 사용자가 단순히 답변을 다시 쓰라고 한 경우에는 feedback log를 만들지 않는다. 불만족 사건과 저장 의도가 있어야 한다.
- 외부 wiki나 전역 feedback root로 라우팅하지 않는다. 이 정책은 “스킬 사용 경험”을 해당 스킬 디렉터리 내부에 남기는 절차다.
