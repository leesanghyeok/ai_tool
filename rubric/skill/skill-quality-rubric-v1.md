# 에이전트 스킬 품질 루브릭 v1

## 1. 평가 목적

이 루브릭은 agent skill이 반복 작업에서 실제 행동 품질을 개선하는 재사용 가능한 절차 기억으로 신뢰해도 되는지를 평가한다.

이 루브릭은 ad-hoc skill review를 막기 위해 다음을 고정한다.

- 고정 100점 채점 모델
- hard gate 요구사항
- 가능한 경우 deterministic check
- 정성 판단이 필요한 경우 judge-only check
- clean/parallel judging 실행 방식
- 안정적인 JSON scorecard 형식

특정 skill repository, source family, local collection은 최고의 기준이 아니다. 이들은 calibration sample일 뿐이며, 점수는 이름값이 아니라 workflow의 명시성, 실행성, 검증 가능성, 재사용성으로만 부여한다.

## 2. 평가 대상

단일 agent skill 또는 skill package. 최소한 다음 중 평가 가능한 artifact를 포함한다.

- main skill document
- 선택적으로 reference/template/script 파일
- skill이 요구하는 input/output artifact 설명
- skill이 사용하는 command, API, file path, schema, tool type 설명
- skill의 trigger, scope, non-scope, approval boundary, verification rule

한국어 사용자용 skill에서는 human-facing prose가 한국어를 기본 문장 언어로 삼아야 한다. 한글 문자가 존재한다는 사실만으로는 충분하지 않다. JSON key, enum 값, file path, command, API name, schema field, proper noun은 원문을 유지해도 되지만, heading, label, 설명문, 절차 동사는 번역 가능한 영어 prose에 의존하면 감점한다.

## 3. 통과 기준

기본 통과 점수(`baseline_passing_score`): **90 / 100**.

skill은 다음 두 조건을 모두 만족할 때만 통과한다.

1. `certification_score >= 90`
2. 모든 hard-gated dimension이 통과 기준 이상이어야 한다.
   - D1 Trigger & Scope Precision: 13 / 15 이상
   - D2 Operational Workflow Explicitness: 17 / 20 이상
   - D3 Safety, Approval & Boundary Alignment: 13 / 15 이상
   - D4 Verification & Evidence Discipline: 13 / 15 이상
   - D5 Reusability, Generality & Language Fit: 9 / 10 이상

D1-D5 중 하나라도 hard-gate threshold 미만이면, numeric total이 90점 이상이어도 skill은 **통과하면 안 된다**.

하드 게이트 상한 규칙(`hard-gate cap rule`):

- D1-D5 중 하나라도 threshold 미만이면 `pass = false`이고 `certification_score_cap = 89`다.
- 진단을 위해 `raw_total_score`는 표시할 수 있지만, certification 결과는 실패다.

## 4. 차원 요약

| ID | 차원 | 점수 | Gate Type | 평가 초점 |
|---|---:|---:|---|---|
| D1 | 사용 조건과 범위 정밀도 | 15 | Hard gate | 언제 로드하고 어디까지 적용할지 |
| D2 | 운영 workflow 명시성 | 20 | Hard gate | 암시적이지 않은 실행 절차와 작업 시퀀스 |
| D3 | 안전, 승인, 경계 정합성 | 15 | Hard gate | 위험 행동 승인 경계와 사용자 운영 취향 |
| D4 | 검증과 근거 규율 | 15 | Hard gate | 완료 주장 전 실제 출력 검증 |
| D5 | 재사용성, 범용성, 언어 적합성 | 10 | Hard gate | 한국어 우선 강도, 범용성, 제품명 과종속 방지 |
| D6 | 실패 처리와 복구 | 10 | Quality | 실패 보고, 원인, 영향, 복구 경로 |
| D7 | 구조, 일관성, 인지 부담 | 8 | Quality | 모순/모호함 없는 직관적 구조 |
| D8 | 병렬화, 컨텍스트 관리, 결정론적 자동화 | 7 | Quality | 병렬 처리, 컨텍스트 관리, 결정론적 자동화 분리 |
| **합계** |  | **100** |  |  |

## 5. 세부 채점 기준

### D1. 사용 조건과 범위 정밀도 — 15점 — 하드 게이트

| 기준 | 점수 | 인정 기준 | Deterministic? |
|---|---:|---|---|
| Trigger가 task/action 중심으로 구체적임 | 4 | skill을 언제 로드해야 하는지 작업 유형, 입력 신호, 상황 기준으로 명확히 설명한다 | Judge |
| Non-scope 또는 사용 금지 조건이 있음 | 3 | skill을 쓰지 말아야 할 경우, 다른 skill로 넘겨야 할 경우, 적용 제외 범위가 있다 | Judge |
| 평가/작업 대상 artifact가 명확함 | 3 | input, output, 생성/수정 대상, 기대 산출물이 구체적이다 | Mostly yes |
| Scope creep 방지 규칙이 있음 | 3 | 승인된 범위 밖 확장, 부수 작업, 위험한 follow-up을 제한한다 | Judge |
| 관련 skill 또는 선행/후행 workflow 관계가 있음 | 2 | 관련 skill, 대체 skill, 선행 discovery, 후속 verification 관계를 설명한다 | Judge |

Local cap(차원 내 상한):

- trigger가 한 문장 이하로 모호하면 D1은 최대 8점이다.
- 거의 모든 작업에 적용될 만큼 trigger가 넓으면 D1은 최대 10점이다.
- non-scope가 전혀 없고 workflow가 위험 행동을 포함하면 D1은 최대 11점이다.
- D1 점수가 13점 미만이면 hard gate 실패다.

### D2. 운영 workflow 명시성 — 20점 — 하드 게이트

| 기준 | 점수 | 인정 기준 | Deterministic? |
|---|---:|---|---|
| 작업 시퀀스가 순서대로 명시됨 | 4 | discovery, plan, execution, verification, report 순서가 혼동 없이 제시된다 | Judge |
| 실행 가능한 command/API/path/schema 예시가 있음 | 4 | 실제 command, API, file path, JSON schema, output shape가 제공된다 | Mostly yes |
| prerequisite discovery가 있음 | 3 | repo 상태, config, credential 필요성, 기존 convention, 입력 파일을 먼저 확인한다 | Judge |
| 단계 간 의존성과 병렬 가능성이 구분됨 | 3 | 순차 의존 단계와 동시 처리 가능한 독립 작업을 구분한다 | Judge |
| workflow가 암시적이지 않음 | 3 | evaluator가 절차를 추론하지 않아도 agent가 그대로 따를 수 있다 | Judge |
| output/report 형식이 있음 | 3 | 수행 결과, 검증 결과, 파일 경로, 남은 이슈를 보고하는 형식이 있다 | Mostly yes |

Local cap(차원 내 상한):

- 실행 가능한 step이 없으면 D2는 최대 8점이다.
- command/path/schema/tool 예시가 전혀 없으면 D2는 최대 12점이다.
- 핵심 workflow가 암시적이라 evaluator가 절차를 추론해야 하면 D2는 최대 14점이다.
- 작업 단계가 섞여 agent가 다시 설계해야 하면 D2는 최대 15점이다.
- D2 점수가 17점 미만이면 hard gate 실패다.

### D3. 안전, 승인, 경계 정합성 — 15점 — 하드 게이트

| 기준 | 점수 | 인정 기준 | Deterministic? |
|---|---:|---|---|
| 위험 행동 승인 게이트가 명확함 | 4 | destructive, external delivery, credential, production, persistent state 변경 전 explicit approval을 요구한다 | Judge |
| 저위험 작업은 불필요하게 묻지 않음 | 3 | read-only discovery, file inspection, log/status check, parsing, low-risk verification은 바로 수행하도록 구분한다 | Judge |
| 사용자/프로젝트 convention 반영 | 3 | 언어, 보고 형식, evidence-first, scope 유지 등 운영 취향을 반영할 수 있다 | Judge |
| scope와 execution approval을 분리함 | 2 | plan feedback, partial agreement, execution approval을 혼동하지 않는다 | Judge |
| security/privacy boundary가 있음 | 2 | secret, private URL, credential, raw evidence 저장 위험을 다룬다 | Judge |
| 불확실성 라벨이 있음 | 1 | 확인됨/추정/미확인 또는 equivalent labeling을 요구한다 | Judge |

Local cap(차원 내 상한):

- 위험 행동을 다루는데 approval gate가 없으면 D3은 최대 7점이다.
- credential/secret handling이 필요한데 언급이 없으면 D3은 최대 10점이다.
- 사용자 선호와 정면 충돌하는 지시가 있으면 D3은 최대 8점이다.
- D3 점수가 13점 미만이면 hard gate 실패다.

### D4. 검증과 근거 규율 — 15점 — 하드 게이트

| 기준 | 점수 | 인정 기준 | Deterministic? |
|---|---:|---|---|
| 완료 조건이 명확함 | 3 | 어떤 output, state, response, file diff, test result가 완료인지 정의한다 | Judge |
| 실제 검증 방법이 있음 | 4 | read-back, parse, lint, test, API response, UI confirmation, git diff/status, health check 중 적절한 검증을 명시한다 | Mostly yes |
| deterministic check를 우선함 | 2 | 계산, parsing, schema validation, count, hash, bounds check는 script/checker로 검증한다 | Mostly yes |
| subagent/tool self-report를 재검증함 | 2 | subagent self-report를 그대로 믿지 않고 parent가 artifact/output을 확인한다 | Judge |
| 기계 검증 가능한 artifact가 있음 | 2 | JSON schema, fixed field, scorecard, deterministic report 등 parseable artifact를 사용한다 | Mostly yes |
| verification 실패 보고가 있음 | 2 | blocked/unverified 상태, 실패 command/API/tool, 영향, recovery를 보고한다 | Judge |

Local cap(차원 내 상한):

- verification이 전혀 없으면 D4는 최대 5점이다.
- 검증이 “확인한다” 같은 추상 표현뿐이면 D4는 최대 8점이다.
- tool을 실행한 척하거나 evidence 없는 완료 보고를 허용하면 D4는 최대 6점이며 global cap도 적용한다.
- D4 점수가 13점 미만이면 hard gate 실패다.

### D5. 재사용성, 범용성, 언어 적합성 — 10점 — 하드 게이트

| 기준 | 점수 | 인정 기준 | Deterministic? |
|---|---:|---|---|
| stable procedure와 one-off artifact가 분리됨 | 2 | 특정 사건 로그와 반복 사용 절차가 분리되어 있다 | Judge |
| 한국어 우선 human-facing prose | 2 | 한국어 사용자용 skill의 heading, 설명, 절차, 보고 형식, 판단 기준이 한국어를 기본 문장 언어로 사용한다. 영어는 machine identifier, 고유명사, command/path/API/schema/enum 또는 처음 정의한 technical term 보조 표기에 한정된다 | Mostly yes |
| machine identifier는 원문 유지 | 1 | JSON key, path, command, API, enum, proper noun을 불필요하게 번역하지 않는다 | Mostly yes |
| 특정 제품명/에이전트명 과종속 없음 | 2 | 범용 agent skill로 재사용 가능하며, platform-specific 절차는 분리되어 있다 | Judge |
| 환경 의존성이 명시됨 | 2 | OS, CLI, package, credential, repo layout 등 전제 조건을 명시한다 | Mostly yes |
| version/update 기준이 있음 | 1 | stale instruction, skill patch, calibration update 기준이 있다 | Judge |

Local cap(차원 내 상한):

- human-facing prose가 한국어-first가 아니면 D5는 최대 7점이다.
- 한국어 문장이 존재하지만 heading, label, 절차 문장, 판단 기준에 자연어 영어 표현이 반복되어 독자가 영어 prose를 계속 해석해야 하면 D5는 최대 8점이다.
- machine identifier 예외를 제외한 영어 prose token 비율이 10%를 넘으면 D5는 최대 8점, 20%를 넘으면 D5는 최대 7점, 35%를 넘으면 D5는 최대 5점이다.
- 주요 heading의 20% 이상이 영어-only이거나, section label이 `Workflow`, `Output`, `Validation`, `Notes`처럼 번역 가능한 영어 label 위주이면 D5는 최대 8점이다.
- 특정 제품명/에이전트명에 불필요하게 종속되면 D5는 최대 6점이다.
- 특정 사건/PR/날짜에 과적합되어 있으면 D5는 최대 5점이다.
- D5 점수가 9점 미만이면 hard gate 실패다.

한국어 우선 강도 규칙:

- `한국어 우선`은 한글 문자가 포함되어 있다는 뜻이 아니다. 사람이 읽는 prose의 기본 문장, heading, checklist label, 보고 template label, action verb가 한국어여야 한다.
- 허용되는 영어: JSON/YAML key, enum, command, file path, API name, package/tool/model/product proper noun, quoted source title, code identifier, CLI flag, URL, schema field, 이미 한국어로 설명한 technical term의 괄호 병기.
- 감점해야 하는 영어: `workflow`, `output`, `validation`, `source`, `briefing`, `delivery`, `status`, `pattern`, `item`, `parent`, `thread`처럼 자연스러운 한국어 대체어가 있는데 heading/label/절차 문장에 반복되는 단어.
- Deterministic checker는 code fence, inline code, URL, path, JSON/YAML key, enum, proper noun allowlist를 제외한 뒤 human-facing prose의 영어 token 비율, 영어-only heading 수, 영어 label 반복 수를 계산해야 한다. Checker 결과는 D5와 global cap 판단의 근거로 scorecard에 포함한다.

### D6. 실패 처리와 복구 — 10점 — 품질 차원

| 기준 | 점수 | 인정 기준 | Deterministic? |
|---|---:|---|---|
| 실패한 command/API/tool과 error 보고 | 2 | 실패 단위와 핵심 error를 숨기지 않는다 | Judge |
| likely cause / impact / recovery 구분 | 2 | 원인 추정, 영향, 다음 복구 행동을 분리한다 | Judge |
| retry/alternative path 기준 있음 | 2 | 재시도 조건과 다른 접근으로 전환할 조건이 있다 | Judge |
| partial/blocked/unverified 상태 구분 | 2 | 일부 완료, 차단, 미검증 상태를 구분한다 | Judge |
| skill 자체 patch 기준 있음 | 2 | skill이 틀렸거나 누락된 경우 수정/보강 기준이 있다 | Judge |

Local cap(차원 내 상한):

- 실패를 일반적인 “문제가 있었다” 수준으로만 다루면 D6은 최대 5점이다.
- 실패를 숨기거나 성공처럼 보고하게 만드는 지침이 있으면 D6은 최대 4점이며 global cap도 적용한다.

### D7. 구조, 일관성, 인지 부담 — 8점 — 품질 차원

| 기준 | 점수 | 인정 기준 | Deterministic? |
|---|---:|---|---|
| heading과 섹션 흐름이 탐색 가능함 | 2 | agent가 trigger, 절차, 검증, 보고, 예외를 빠르게 찾을 수 있다 | Mostly yes |
| 핵심 절차가 numbered/bulleted steps로 압축됨 | 2 | 긴 산문보다 실행 순서가 눈에 띈다 | Mostly yes |
| 모순되거나 충돌하는 지시가 없음 | 2 | approval, execution, verification, reporting 규칙이 충돌하지 않는다 | Judge |
| 모호한 표현이 기준 없이 남발되지 않음 | 1 | “적절히”, “필요시” 같은 표현에 판단 기준이 붙어 있다 | Judge |
| 최종 보고 template이 있음 | 1 | 작업 완료 후 보고 형식이 있다 | Mostly yes |

Local cap(차원 내 상한):

- 길지만 구조가 없어 agent가 다시 요약해야 하면 D7은 최대 4점이다.
- 모순되거나 충돌하는 지시가 있으면 D7은 최대 4점이다.
- 과도한 배경 설명이 절차를 가리면 D7은 최대 6점이다.

### D8. 병렬화, 컨텍스트 관리, 결정론적 자동화 — 7점 — 품질 차원

| 기준 | 점수 | 인정 기준 | Deterministic? |
|---|---:|---|---|
| 병렬 처리 가능성 판단 기준 있음 | 1 | 독립 작업과 순차 의존 작업을 구분한다 | Judge |
| 동시 처리 가능한 작업을 병렬화함 | 1 | subagent/parallel review를 사용해 작업 속도를 높이고 결과를 중앙에서 종합한다 | Judge |
| 큰 컨텍스트 작업의 shard 기준 있음 | 1 | 큰 로그/문서/코드베이스/후보 비교를 shard로 나누어 컨텍스트 오염을 줄인다 | Judge |
| 결정론적/비결정론적 작업 분리 | 2 | parsing, 집계, 정규화, schema 검증은 script로 처리하고 판단/해석/우선순위화는 agent reasoning에 맡긴다 | Judge |
| 공통 재사용 스크립트 설계 기준 있음 | 1 | 단계마다 일회성 script를 만들지 않고 여러 단계/샘플에 반복 가능한 script를 만든다 | Judge |
| 중간 artifact가 parseable함 | 1 | JSON/schema/fixed field/path 기반 artifact로 token 사용과 컨텍스트 오염을 줄인다 | Mostly yes |

Local cap(차원 내 상한):

- 큰 컨텍스트 작업인데 분할/subagent/중간 artifact 전략이 없으면 D8은 최대 3점이다.
- 동시 처리가 가능한 독립 작업인데 순차 처리만 지시하면 D8은 최대 4점이다.
- 결정론적 작업을 script화하지 않고 agent reasoning에 맡기면 D8은 최대 4점이다.
- 단계별 일회성 script만 만들고 공통 script 설계가 없으면 D8은 최대 5점이다.

## 6. 전역 상한 및 인증 규칙

먼저 checklist 채점을 적용하고, 그다음 local cap, global cap, certification rule 순서로 적용한다.

전체 상한(`global cap`):

- 대상이 agent skill 또는 skill package가 아니면 total score는 최대 40점이다.
- 실제 절차가 없고 개념 설명만 있으면 total score는 최대 60점이다.
- destructive/external/credential/production/persistent state action을 다루면서 approval boundary가 없으면 total score는 최대 55점이다.
- verification discipline이 전혀 없으면 total score는 최대 70점이다.
- fabricated output, tool 실행한 척하기, evidence 없는 완료 보고를 허용하면 total score는 최대 50점이다.
- 한국어 사용자용 skill인데 human-facing prose가 대부분 한국어가 아니면 total score는 최대 65점이다.
- 한국어 문장이 일부 있어도 사람-facing heading/label/절차 문장에 번역 가능한 영어 prose가 반복되어 영어 해석 부담이 크면 total score는 최대 85점이다.
- machine identifier 예외를 제외한 영어 prose token 비율이 20%를 넘으면 total score는 최대 80점, 35%를 넘으면 total score는 최대 65점이다.
- 주요 heading 또는 보고 template label의 20% 이상이 영어-only이면 total score는 최대 85점이다.
- 특정 제품명/에이전트명에 불필요하게 종속되어 범용 재사용이 어렵다면 total score는 최대 75점이다.
- trigger가 너무 넓어 거의 모든 작업에 로드될 수준이면 total score는 최대 75점이다.
- 본문이 특정 1회성 사건 로그에 가까우면 total score는 최대 70점이다.
- 핵심 workflow가 암시적이어서 evaluator가 절차를 추론해야 하면 total score는 최대 70점이다.
- 큰 컨텍스트 작업을 다루면서 subagent/parallel review/intermediate artifact 전략이 전혀 없으면 total score는 최대 80점이다.
- 결정론적 반복 처리와 비결정론적 추론을 구분하지 않아 모든 작업을 agent reasoning에 맡기면 total score는 최대 75점이다.
- 단계마다 일회성 script를 남발하고 공통 재사용 가능한 자동화로 정리하지 않으면 total score는 최대 80점이다.
- security/privacy 위험을 부추기면 total score는 최대 50점이다.

인증 규칙(`certification rule`):

- `pass = certification_score >= 90 AND D1 >= 13 AND D2 >= 17 AND D3 >= 13 AND D4 >= 13 AND D5 >= 9`.
- hard-gated dimension 중 하나라도 threshold 미만이면 `raw_total_score >= 90`이어도 `pass = false`다.
- cap이 적용되면 `raw_total_score`와 `certification_score`를 모두 보고한다.

## 7. 점수 해석

| 점수 | 해석 |
|---:|---|
| 90–100 및 모든 hard gate 통과 | Production-quality skill. 반복 작업에 사용할 수 있음 |
| 80–89 | 강하지만 통과 기준은 아님. hard gate 또는 quality gap 개선 필요 |
| 70–79 | 부분적으로 사용 가능. 운영 안정성과 검증성이 부족함 |
| 60–69 | 약한 skill. 상당한 재작성 필요 |
| 0–59 | skill로 신뢰하기 어려움. 구조와 절차를 먼저 재구축해야 함 |

## 8. 채점 절차

1. target skill path와 read-only mode를 확인한다.
2. main skill document와 reference/template/script 파일을 읽는다.
3. D1-D5 hard-gated dimension을 먼저 채점한다.
4. deterministic check가 가능한 기준은 script 또는 parseable check로 검증한다.
5. 비결정론적 기준은 clean judge가 packet evidence만 사용해 채점한다.
6. checklist item을 독립적으로 채점한다.
7. local cap을 적용한다.
8. global cap을 적용한다.
9. hard-gate certification rule을 적용한다.
10. JSON scorecard와 짧은 human summary를 생성한다.

## 9. 판정 실행 모드

기본 판정 모드는 clean context다. judge는 현재 대화, memory, 구현 메모, 작성자 self-report를 evidence로 사용하면 안 된다.

판정 모드:

- `clean_subagent`: 기본 모드. self-contained evaluation packet만 받은 단일 judge가 전체 rubric을 평가한다.
- `parallel_clean_subagents`: multi-dimension, long skill package, high-stakes 평가에서 사용한다. parent가 D1-D8 shard를 나누고 clean subagent가 병렬 평가한다.
- `same_context_exception`: low-stakes quick check 또는 clean subagent unavailable인 경우만 허용한다. scorecard에 context contamination risk를 기록해야 한다.

병렬 clean-subagent 판정 workflow:

1. parent가 evaluation packet을 만든다: target skill, included files, rubric, allowed evidence, cap rules, JSON schema.
2. parent가 D1-D8 dimension 또는 checklist group을 중복 없이 shard로 나눈다.
3. shard judge는 배정된 shard만 평가하고 최종 총점, 최종 grade, 최종 global cap을 확정하지 않는다.
4. parent가 shard JSON을 parse하고 score bounds, missing/duplicate criteria, evidence grounding, contradiction을 검증한다.
5. parent가 local cap을 병합하고 global cap을 중앙에서 한 번 적용한다.
6. parent가 최종 scorecard와 사람이 읽는 요약을 생성한다.

## 10. 판정자 지침

LLM 또는 human reviewer가 비결정론적 기준을 평가할 때 다음 지침을 사용한다.

1. clean context에서 평가한다. 현재 대화, memory, 구현 메모, 작성자 self-report를 사용하지 않는다.
2. evaluation packet에 포함된 skill file, included files, deterministic checker output, rubric만 근거로 사용한다.
3. 특정 repository/source family/local collection을 최고 기준로 취급하지 않는다.
4. 총점을 결정하기 전에 checklist item을 먼저 채점한다.
5. skill에 명시되지 않은 의도, 관행, 선의의 추정을 점수로 보상하지 않는다.
6. 모든 issue에 대해 구체적인 path와 근거를 보고한다.
7. 길이 자체, 전문 용어 자체, 멋진 표현 자체를 보상하지 않는다.
8. workflow가 암시적이면 낮게 채점한다.
9. 병렬화는 컨텍스트 오염 방지만 아니라 동시 처리 가능한 task의 속도 개선도 본다.
10. 결정론적 부분을 agent reasoning에 맡기면 감점한다.
11. 단계별 일회성 script 남발을 감점하고 공통 재사용 script 설계를 보상한다.
12. criterion을 검증할 수 없으면 `unverified`로 표시하고 partial 또는 zero credit만 준다.
13. shard judge는 자기 shard만 평가하고 최종 총점을 계산하지 않는다.

## 11. JSON Scorecard 스키마

```json
{
  "skill_path": "string",
  "evaluated_at": "YYYY-MM-DDTHH:mm:ssZ",
  "read_only": true,
  "rubric_version": "agent-skill-quality-v1",
  "judging_context": "clean_subagent | parallel_clean_subagents | same_context_exception",
  "context_contamination_notes": "string",
  "baseline_passing_score": 90,
  "raw_total_score": 0,
  "certification_score": 0,
  "max_score": 100,
  "pass": false,
  "grade": "excellent | strong_not_passing | adequate | weak | unacceptable",
  "hard_gates": [
    {
      "dimension_id": "D1",
      "required_score": 13,
      "actual_score": 0,
      "passed": false,
      "blocking_issues": ["string"]
    }
  ],
  "global_caps_applied": [
    {
      "rule_id": "string",
      "cap": 0,
      "reason": "string",
      "evidence": ["string"]
    }
  ],
  "dimension_scores": [
    {
      "dimension_id": "D1",
      "dimension": "Trigger & Scope Precision",
      "score": 0,
      "max_score": 15,
      "gate_type": "hard | quality",
      "checklist": [
        {
          "criterion_id": "string",
          "score": 0,
          "max_score": 0,
          "deterministic": true,
          "evidence": ["string"],
          "paths": ["string"],
          "comment": "string"
        }
      ],
      "local_caps_applied": [],
      "summary": "string",
      "recommended_fixes": [
        {
          "priority": "high | medium | low",
          "path": "string",
          "action": "string"
        }
      ]
    }
  ],
  "counts": {
    "included_files": 0,
    "reference_files": 0,
    "template_files": 0,
    "script_files": 0,
    "checklist_items": 0,
    "deterministic_items": 0,
    "judge_only_items": 0
  },
  "issues": [
    {
      "id": "string",
      "severity": "critical | high | medium | low | info",
      "dimension_id": "string",
      "rule": "string",
      "path": "string",
      "evidence": "string",
      "recommendation": "string"
    }
  ],
  "unverified": [
    {
      "area": "string",
      "reason": "string"
    }
  ],
  "next_actions": [
    {
      "priority": "high | medium | low",
      "action": "string",
      "paths": ["string"]
    }
  ]
}
```

## 12. 보정 노트

Calibration에서는 source family를 최고 기준로 취급하지 않는다. 다음 sample을 최소 포함한다.

1. 실제로 agent 행동을 개선한 강한 skill.
2. 평균적이지만 사용 가능한 skill.
3. 길고 그럴듯하지만 실행성이 낮은 skill.
4. approval boundary 또는 verification이 빠진 skill.
5. trigger가 너무 넓거나 너무 좁은 skill.
6. 특정 제품명/에이전트명에 과하게 묶인 skill.
7. 큰 context 작업인데 parallel/subagent/intermediate artifact 전략이 없는 skill.
8. 결정론적 처리와 비결정론적 추론을 구분하지 못하는 skill.
9. 단계마다 일회성 script를 만드는 과잉 자동화 skill.

Calibration 질문:

- 강한 skill이 높은 점수를 받는가?
- 장황하지만 non-operational한 skill이 cap으로 잡히는가?
- approval/verification 누락이 hard gate에서 잡히는가?
- source family 이름값이 점수에 영향을 주지 않는가?
- 동시 처리가 가능한 task를 순차 처리하도록 만든 skill이 감점되는가?
- 결정론적 처리와 비결정론적 추론의 분리 실패가 감점되는가?
- 일회성 script 남발 대신 공통 재사용 script를 요구하는가?
- judge 간 score variance가 5–8점 안에 들어오는가?

## origin/main 병합 보강: 실행/보정 원칙

이 루브릭은 `origin/main`의 clean/parallel judging 원칙을 함께 따른다.

- 판정 근거는 packet 내부 자료, canonical rubric, score schema, deterministic checker output으로 제한한다.
- Local collection, source family, 유명 작성자, 자주 쓰였다는 사실은 점수 보상 근거가 아니다.
- 플랫폼-specific skill은 플랫폼 고유 절차와 범용 절차를 분리했는지 본다.
- 병렬화 항목은 context 오염 방지뿐 아니라 독립 작업 병렬화에 따른 wall-clock speed 개선 가능성도 평가한다.
- Deterministic work(JSON parse, schema validation, aggregation, cap consistency)는 reusable script/checker로 처리되어야 한다.
- Nondeterministic judgment(evidence 해석, 우선순위 판단, 모순 reconciliation)은 evidence-backed reasoning으로 남긴다.
- Parallel shard 결과는 parent가 중앙에서 D1-D8 누락/중복, score bounds, hard gate, global cap, contradiction을 reconcile한다.
