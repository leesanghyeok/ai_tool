---
name: feedback-ai-logging
description: AI/agent 출력에 대한 불만족을 LLM Wiki raw/feedback 트리 아래의 변경 불가 Markdown 피드백 로그로 기록하고, 원본 이력과 후보 개선 규칙을 함께 보존할 때 사용합니다.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feedback, llm-wiki, evals, quality, logging]
    related_skills: [llm-wiki, rubric-design]
---

# AI 피드백 로깅

## 개요

이 스킬은 사용자가 AI/agent 출력에 불만족했고 그 사건을 구조화된 Markdown 원본으로 LLM Wiki에 남기고 싶을 때 사용한다. 목적은 wiki의 개념 페이지나 루브릭을 즉시 고치는 것이 아니다. 목적은 나중에 실패 분류, agent 규칙, 루브릭, 품질 가이드로 일괄 분석할 수 있도록 깨끗한 역사 기록을 보존하는 것이다.

피드백 로그는 **raw data**다. 개별 사건은 `concepts/`, `comparisons/`, `queries/`가 아니라 `raw/feedback/` 아래에 둔다. 불만족 사건 하나마다 Markdown 파일 하나를 만든다.

로그는 다음 두 가지를 함께 담아야 한다.

1. 역사적 사건: 무엇이 일어났고, 왜 불만족스러웠고, 무엇을 기대했는지.
2. 후보 학습 자료: 나중에 별도 분석 단계에서 승격할 수 있는 후보 agent 규칙과 체크리스트 항목.

## 사용해야 할 때

다음 경우에 이 스킬을 사용한다.

- 사용자가 AI/agent 답변이 불만족스러웠다고 말하고 그 내용을 기록하길 원할 때.
- 사용자가 “log this”, “record this failure”, “save this feedback”, “이 실패를 기록해”, “피드백으로 남겨”처럼 말할 때.
- 작업 결과가 명시적 사용자 요구사항을 놓쳤고, 사용자가 그 패턴을 피드백 데이터로 기억하길 원할 때.
- 사용자가 미래 AI/agent 출력 품질 개선을 위한 feedback loop를 만들고 있을 때.
- 사용자가 불만족 로그를 일관된 Markdown 형식으로 LLM Wiki에 저장하길 원할 때.

다음 경우에는 이 스킬을 사용하지 않는다.

- 사용자가 단순히 불평하거나 감정을 표현했을 뿐, 사건 기록을 요청하지 않았을 때.
- 피드백이 AI/agent 출력이나 워크플로우 품질에 관한 것이 아닐 때.
- 사용자가 정제된 guide, rubric, taxonomy, concept page를 직접 업데이트하라고 요청했을 때. 이 경우 `llm-wiki` 및/또는 `rubric-design`를 사용한다.
- 사용자가 안정적인 개인 선호를 전역으로 저장하길 원할 때. 오래 지속될 사실이면 memory 사용 여부를 별도로 판단한다.

## 저장 경로

각 로그는 다음 경로에 Markdown 파일 하나로 저장한다.

```text
$WIKI/raw/feedback/YYYY-MM-DD/{HHMMSS}-{session_id}-{short-slug}.md
```

각 구성요소의 의미는 다음과 같다.

- `$WIKI`는 사용자가 다른 wiki 경로를 지정하지 않는 한 `${WIKI_PATH:-$HOME/wiki}`다.
- `YYYY-MM-DD`는 로그 생성 시점의 local date다.
- `session_id`는 현재 conversation/session/thread를 식별할 수 있는 최선의 값이다.
- `HHMMSS`는 local 24-hour time이다.
- `short-slug`는 실패 패턴을 요약하는 짧은 영어 lowercase slug이며, 단어는 hyphen으로 구분한다.

## 세션 식별자 발견 (Session Identifier Discovery)

식별자 규칙은 특정 런타임에 종속되지 않아야 한다. `session_id`는 이 스킬이 실행되는 환경에서 사용할 수 있는 최선의 conversation, session, thread 식별자여야 한다. Hermes, Codex, Claude CLI 또는 다른 특정 agent runtime을 가정하지 않는다. 먼저 식별자를 발견하고, 실제로 쓸 수 있는 후보가 없을 때만 `unknown-session`으로 fallback한다.

다음 우선순위를 사용한다.

1. **명시적 platform 또는 사용자 제공 식별자.** 피드백이 platform이나 링크된 artifact에서 온 경우 구체적인 source identifier를 우선한다. 예: Discord thread id, Telegram topic id, GitHub issue/PR/comment thread id, browser URL, chat permalink, 사용자가 직접 제공한 id.
2. **Runtime-provided session variables.** 현재 실행 환경에서 session처럼 보이는 환경변수를 확인한다. 알려진 이름이 있으면 `HERMES_SESSION_ID`, `CODEX_SESSION_ID`, `CLAUDE_SESSION_ID`를 확인하고, 일반 패턴인 `*_SESSION_ID`, `*_CONVERSATION_ID`, `*_THREAD_ID`, `*_CHAT_ID`도 확인한다. 현재 환경에 실제로 존재하는 값만 사용하며, 추측하거나 만들어내지 않는다.
3. **Runtime metadata 또는 status command.** 활성 CLI/runtime이 현재 session/conversation id를 노출하는 안전한 status command나 non-secret metadata file을 제공하면 사용한다. id를 찾기 위해 secrets, credentials, tokens 또는 관련 없는 private state를 읽지 않는다.
4. **Fallback.** 명시적 platform id, runtime environment value, safe runtime metadata value가 모두 없을 때만 `unknown-session`을 사용한다.

식별자를 발견하면 유용한 경우 `source_ref`에 출처를 기록한다. 예: `discord-thread:<id>`, `github-pr:<owner>/<repo>#<number>`, `cli-session:hermes:<id>`, `cli-session:codex:<id>`, `cli-session:claude:<id>`, `cli-session:env:<variable-name>`. 식별자를 발견하지 못했다면 빈칸으로 두지 말고 `cli:no-session-id-discovered`처럼 이유가 드러나는 source reference를 사용한다.

예시:

```text
raw/feedback/2026-06-01/143210-1517194335987306506-missing-published-dates.md
raw/feedback/2026-06-01/151002-1517194335987306506-no-test-verification.md
raw/feedback/2026-06-02/092015-unknown-session-missing-decision-criteria.md
```

## 원본 데이터 원칙 (Raw Data Principles)

`raw/feedback/` 아래의 피드백 로그는 raw source material이다. 다음 규칙을 따른다.

1. **사건 하나, 파일 하나.** 관련 없는 여러 피드백 사건을 한 파일에 이어 붙이지 않는다.
2. **이력을 보존한다.** 파일은 기록 시점에 무슨 일이 있었는지를 남긴다.
3. **Raw file에 처리 상태를 저장하지 않는다.** frontmatter나 본문에 `status`, `triage_status`, `derived_pages`, `converted_to_rule`, `converted_to_rubric` 같은 처리 상태 필드를 추가하지 않는다.
4. **Raw file에 승격 결정을 기록하지 않는다.** 이후 분석, triage, `concepts/`, `queries/`, rubric으로의 승격은 별도 관리/분석 문서에서 다룬다.
5. **후보 규칙은 허용된다.** `Candidate Agent Rule`과 `Candidate Checklist Items`는 기록 시점의 사건 해석에 포함되는 자료이지 처리 상태가 아니다. 유용하면 포함한다.
6. **개별 사건용 concept page를 만들지 않는다.** 개별 사건은 `raw/feedback/`에 남긴다. 반복 패턴만 나중에 승격할 수 있다.

## 필수 Frontmatter

모든 피드백 로그는 YAML frontmatter로 시작해야 한다.

```yaml
---
type: feedback-log
source_type: ai-dissatisfaction
source_platform: discord
source_ref: ""
session_id: ""
ingested: YYYY-MM-DD
created_at: YYYY-MM-DDTHH:MM:SS+09:00
task_type: research
agent_or_model: ""
severity: high
categories: [evidence, freshness]
sha256: "<body-sha256>"
---
```

### 필드 규칙 (Field Rules)

| Field | Required | Meaning |
|---|---:|---|
| `type` | yes | 항상 `feedback-log` |
| `source_type` | yes | 이 스킬에서는 항상 `ai-dissatisfaction` |
| `source_platform` | yes | 출처 surface. 예: `discord`, `cli`, `github`, `web`, `local`, `unknown` |
| `source_ref` | no | 사용 가능한 link, thread id, message reference, file path, runtime session source 또는 기타 source pointer |
| `session_id` | yes | 최선의 session/thread/conversation id. `unknown-session`을 쓰기 전에 Session Identifier Discovery를 실행한다 |
| `ingested` | yes | 로그가 wiki에 기록된 날짜 |
| `created_at` | yes | 로그의 정확한 local timestamp |
| `task_type` | yes | 아래 taxonomy 중 하나 |
| `agent_or_model` | no | 알려진 경우 관련 agent, model 또는 tool |
| `severity` | yes | `low`, `medium`, `high`, `critical` 중 하나 |
| `categories` | yes | failure category taxonomy에서 하나 이상 |
| `sha256` | yes | 닫는 frontmatter 뒤 Markdown body만 대상으로 계산한 SHA-256 hash |

## 작업 유형 분류 (Task Type Taxonomy)

`task_type`에는 다음 값 중 하나를 사용한다.

```text
research
coding
recommendation
summarization
planning
automation
review
translation
conversation
other
```

맞는 값이 없으면 `other`를 사용하고, `Situation` 섹션에서 실제 작업을 설명한다.

## 실패 범주 분류 (Failure Category Taxonomy)

`categories`에는 다음 값 중 하나 이상을 사용한다.

```text
requirement-miss       Explicit user requirement was missed
evidence               Sources, citations, or evidence were absent or weak
freshness              Publication date, update date, or currentness was missing or weak
verification           Execution, testing, validation, or tool-backed checking was missing
specificity            Output was too generic for the user's context
decision-criteria      Recommendation lacked explicit decision criteria
format                 Requested structure or output format was not followed
tone                   Tone, style, or language did not match the user's expectation
context-misread        User intent, context, or constraints were misunderstood
overconfidence         Uncertain information was stated too confidently
hallucination          Output contained false, fabricated, or unsupported claims
actionability          Output lacked concrete next steps or operational guidance
verbosity              Output was too long or buried the answer
insufficient-detail    Output was too short, shallow, or under-explained
```

새 category가 반복적으로 필요해지면 임의의 one-off label을 많이 만들지 말고, 나중에 taxonomy update에서 의도적으로 추가한다.

## 심각도 규칙 (Severity Rules)

사건을 정직하게 설명할 수 있는 가장 낮은 severity를 사용한다.

```text
low:
- 주로 preference, tone, wording, 사소한 구조 문제다.
- 출력은 사용할 수 있었지만 아쉬웠다.

medium:
- 중요한 요구사항 일부가 빠졌다.
- 출력은 수정이 필요했지만 근본적으로 신뢰 불가능한 수준은 아니었다.
- decision criteria, specificity, actionability가 약했다.

high:
- 핵심 요구사항을 놓쳤다.
- 중요한 evidence, freshness, verification이 없었다.
- 의도한 결정에 사용하려면 상당한 재작업이 필요해 신뢰하기 어려웠다.
- 같은 실패 유형이 기록하지 않으면 재발할 가능성이 크다.

critical:
- fabricated source, fabricated tool result 또는 심각한 hallucination이 있었다.
- 위험한 실행, 무단 변경, 데이터 손실, 보안/프라이버시/비용 위험이 있었다.
- 사용자가 따르면 실제 피해가 발생할 수 있는 오류였다.
```

## Markdown 본문 템플릿 (Markdown Body Template)

Frontmatter 뒤에는 이 body를 사용한다. 나중에 분석이 가능하도록 섹션의 의미를 안정적으로 유지한다. 한국어 대화에서는 섹션명을 한국어로 써도 되지만, 가능하면 괄호에 English semantic label을 함께 둔다.

````markdown
# Feedback Log: {Title}

## 상황 (Situation)

- Task type: {task_type}
- User wanted: {what the user expected or requested}
- Agent actually did: {what the AI/agent output or workflow did}

## 불만족한 점 (Dissatisfaction)

{Describe what was unsatisfactory. Be concrete.}

## 기대한 동작 (Expected Behavior)

{Describe what should have happened instead.}

## 근거 (Evidence)

{Quote or summarize the relevant user request, agent response, command result, or artifact. Use short excerpts rather than whole transcripts unless necessary.}

```text
{optional excerpt}
```

## 실패 범주 (Failure Categories)

- {category-1}
- {category-2}

## 심각도 (Severity)

{low | medium | high | critical}

Reason:
- {Why this severity is appropriate.}

## 후보 Agent 규칙 (Candidate Agent Rule)

{A concise candidate rule that could prevent this failure in future. This is not a processing status and does not mean the rule has been promoted.}

> {one-sentence rule}

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] {Observable check item 1}
- [ ] {Observable check item 2}
````

## 파일명 Slug 규칙 (Filename Slug Rules)

`short-slug`는 다음 규칙으로 만든다.

1. 영어 lowercase 단어를 사용한다.
2. 가능하면 3~6개 단어를 사용한다.
3. 단어는 hyphen으로 구분한다.
4. domain보다 failure pattern을 우선한다.
5. personally identifying details를 피한다.

좋은 slug:

```text
missing-published-dates
no-test-verification
missing-decision-criteria
overconfident-unsupported-claim
ignored-output-format
```

나쁜 slug:

```text
bad-answer
user-was-annoyed
that-discord-thing
failure
```

## 해시 규칙 (Hashing Rule)

`sha256` field는 Markdown body만 대상으로 계산한다. 즉 closing frontmatter delimiter 뒤의 모든 내용을 그대로 hash한다.

권장 절차:

1. 먼저 body를 작성한다.
2. 정확한 body string에 대해 SHA-256을 계산한다.
3. hash를 frontmatter에 삽입한다.
4. 파일을 쓴다.

이 방식은 LLM Wiki raw-source pattern을 따른다. frontmatter는 source를 설명하고, hash는 raw body content를 검증한다.

## 언어 정책 (Language Policy)

- 한국어 대화에서는 사람이 읽는 feedback log body를 기본적으로 한국어로 작성한다.
- Machine/tool-facing frontmatter key, controlled enum value, category label, slug, file path, hash는 필요한 영어 형식을 유지한다.
- 본문 섹션명은 한국어로 쓸 수 있지만, 나중에 파싱할 수 있도록 같은 semantic section을 보존한다.

## 작업 절차 (Workflow)

1. **Wiki path 식별.** 사용자가 경로를 지정하지 않으면 `${WIKI_PATH:-$HOME/wiki}`를 사용한다.
2. **Date directory 생성.** `raw/feedback/YYYY-MM-DD/`가 있는지 확인하고 없으면 만든다.
3. **Identifier 발견.** `session_id`, `HHMMSS`, `short-slug`를 정한다. `session_id`는 `unknown-session`으로 fallback하기 전에 runtime-agnostic Session Identifier Discovery 절차를 실행한다.
4. **가볍게 분류.** Controlled taxonomy에서 `task_type`, `severity`, `categories`를 고른다.
5. **Incident body 작성.** Situation, dissatisfaction, expected behavior, evidence에 집중한다.
6. **후보 학습 내용 추가.** 예방 가능한 패턴이 분명하면 candidate agent rule과 checklist items를 포함한다.
7. **`sha256` 계산.** Body만 hash한다.
8. **Markdown 파일 하나 작성.** 사용자가 별도로 promotion 또는 analysis를 요청하지 않는 한 concept/rubric page를 업데이트하지 않는다.
9. **생성 경로 보고.** 사용자에게 저장된 경로와 categories/severity 요약을 알려준다.

## 예시 (Example)

Path:

```text
raw/feedback/2026-06-01/143210-1517194335987306506-missing-published-dates.md
```

Content:

````markdown
---
type: feedback-log
source_type: ai-dissatisfaction
source_platform: discord
source_ref: "discord-thread"
session_id: "1517194335987306506"
ingested: 2026-06-01
created_at: 2026-06-01T14:32:10+09:00
task_type: research
agent_or_model: "hermes"
severity: high
categories: [evidence, freshness]
sha256: "8f1f0f2adf3b6d4f0bbf6e9c35d2d4a4100d1dcf3c39d7d8752f0a2a00000000"
---
# Feedback Log: Research Answer Missing Published Dates

## 상황 (Situation)

- Task type: research
- User wanted: AI 품질 feedback loop에 대한 research summary를 근거 링크와 발행 시간까지 포함해 받기를 원했다.
- Agent actually did: 방법론 요약과 링크는 제공했지만, 핵심 source마다 publication date를 일관되게 붙이지 않았다.

## 불만족한 점 (Dissatisfaction)

답변이 evidence link와 publication time을 함께 달라는 명시적 요구사항을 일관되게 만족하지 못했다.

## 기대한 동작 (Expected Behavior)

각 핵심 source에는 title, link, publication 또는 update date, 그리고 어떤 claim을 뒷받침하는지에 대한 짧은 설명이 포함되어야 했다.

## 근거 (Evidence)

```text
User request included: "근거 링크와, 해당 내용의 발행시간들도 같이 적어주고"
```

## 실패 범주 (Failure Categories)

- evidence
- freshness

## 심각도 (Severity)

high

Reason:
- Publication date 누락은 명시적 요구사항을 놓친 것이며 research trustworthiness에 직접 영향을 준다.

## 후보 Agent 규칙 (Candidate Agent Rule)

> 연구 답변에서 사용자가 근거 링크와 발행 시간을 요청하면, 모든 핵심 source에 link와 publication/update date를 함께 포함해야 한다.

## 후보 체크리스트 항목 (Candidate Checklist Items)

- [ ] 모든 핵심 source에 URL이 있다.
- [ ] 모든 핵심 source에 publication/update date가 있거나, 찾을 수 없음을 명시했다.
- [ ] 각 source가 어떤 claim을 뒷받침하는지 연결되어 있다.
````

## 흔한 실수 (Common Pitfalls)

1. **Raw incident를 `concepts/`에 넣기.** 개별 불만족 사건은 `raw/feedback/` 아래에 둔다. 반복 패턴만 나중에 concept page나 rubric이 될 수 있다.
2. **Raw file에 processing state 추가하기.** Frontmatter에 status, triage, derived-page, promotion field를 추가하지 않는다.
3. **`session_id.md`만 사용하기.** 같은 session에서 여러 feedback log가 생기면 충돌한다. 파일명은 time으로 시작하고 session id와 slug를 포함한다.
4. **모호한 category 사용하기.** 나중에 집계할 수 있도록 controlled category label을 우선한다.
5. **Expected behavior 생략하기.** 원하는 동작이 없는 complaint는 유용한 rule로 바꾸기 어렵다.
6. **Candidate rule/checklist 생략하기.** 예방 가능한 패턴이 분명하면 맥락이 신선할 때 기록한다.
7. **파일 전체를 hash하기.** Frontmatter가 아니라 body만 hash한다.
8. **기본적으로 즉시 promotion하기.** Logging과 promotion은 별도 workflow다. 사용자가 analysis 또는 guide/rubric update를 요청할 때만 승격한다.
9. **한 agent runtime에 session id 규칙을 hard-code하기.** 이 스킬은 Hermes, Codex, Claude CLI, 기타 환경에서 공유된다. 특정 runtime-specific variable 하나를 가정해서 `unknown-session` 문제를 고치지 않는다. Generic `session_id` 규칙을 보존하고, platform id, runtime env vars, safe metadata를 확인하는 discovery procedure를 추가/실행한다.

## 검증 체크리스트 (Verification Checklist)

완료를 보고하기 전에 다음을 확인한다.

- [ ] File path가 `raw/feedback/YYYY-MM-DD/{HHMMSS}-{session_id}-{short-slug}.md`와 일치한다.
- [ ] Frontmatter가 byte 0에서 시작하며 모든 required fields를 포함한다.
- [ ] Processing-status 또는 promotion field가 없다.
- [ ] `task_type`이 task type taxonomy에 있는 값이다.
- [ ] `severity`가 `low`, `medium`, `high`, `critical` 중 하나다.
- [ ] `categories`가 failure category taxonomy에 있는 값이다.
- [ ] Body가 Situation, Dissatisfaction, Expected Behavior, Evidence, Failure Categories, Severity, Candidate Agent Rule, Candidate Checklist Items에 해당하는 semantic sections를 포함한다.
- [ ] `sha256`이 body만 대상으로 계산되었다.
- [ ] 특정 runtime을 가정하지 않고 Session Identifier Discovery 절차로 `session_id`를 선택했다.
- [ ] `unknown-session`을 사용했다면 explicit platform ids, runtime environment variables, safe runtime metadata/status sources를 먼저 확인했다.
- [ ] `source_ref`가 발견한 id source를 기록하거나, id를 발견하지 못한 이유를 기록한다.
- [ ] 최종 응답이 생성된 경로와 severity/categories 한 줄 요약을 제공한다.
