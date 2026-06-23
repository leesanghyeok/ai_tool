# Skill Quality Rubric v1

## 1. Evaluation Purpose

이 루브릭은 agent skill의 품질을 평가하기 위한 100점 기준이다. 목표는 skill이 단순히 잘 쓰인 문서인지가 아니라, agent가 반복 작업에서 더 정확하고 안전하고 검증 가능한 행동을 하도록 만드는지를 평가하는 것이다.

특정 repository, 프레임워크, 에이전트 제품명은 최고의 기준이 아니다. 좋은 skill은 출처나 이름값이 아니라, 작업 workflow가 암시적으로 숨지 않고 직관적이고 명시적으로 잘 동작하는지로 판단한다.

이 루브릭은 특히 다음 유형의 skill에 적용한다.

- 로컬 agent skill
- 외부 skill repository의 agent workflow skill
- coding-agent, research-agent, devops-agent playbook
- command/API/tool 기반 operational procedure
- 사용자 선호, 승인 경계, 검증 기준을 agent 행동으로 변환하는 문서

## 2. Evaluation Target

평가 대상은 하나의 skill 문서 또는 skill package이다. package형 skill의 경우 `SKILL.md`와 참조 파일, 스크립트, 템플릿까지 함께 평가할 수 있다.

## 3. Total Score

100 points.

## 4. Dimension Summary

| Dimension | Points | Evaluation Focus |
|---|---:|---|
| A. Trigger & Scope Precision | 15 | 언제 로드하고 어디까지 적용할지 |
| B. Operational Procedure Quality | 20 | 실제 실행 가능한 절차 품질 |
| C. User Preference / Boundary Alignment | 15 | 사용자 승인 경계와 작업 취향 반영 |
| D. Verification & Evidence Discipline | 15 | 완료 주장 전 실제 검증 유도 |
| E. Failure Handling & Recovery | 10 | 실패 보고, 원인, 복구 경로 |
| F. Reusability & Portability | 10 | 반복 사용성과 환경 이식성 |
| G. Structure, Consistency, and Cognitive Load | 8 | 모순/모호함 없이 직관적으로 따를 수 있는 구조 |
| H. Parallelization, Context Management & Deterministic Automation | 7 | 병렬 처리 가능성 판단, 컨텍스트 관리, 결정론적 자동화 분리 |
| **Total** | **100** | |

## 5. Detailed Scoring Criteria

### A. Trigger & Scope Precision — 15 points

| Checklist Criterion | Points | Recognition Standard |
|---|---:|---|
| 사용 조건이 task/action 중심으로 구체적임 | 4 | skill을 언제 로드해야 하는지 동사, 작업 유형, 상황 기준으로 명확히 설명한다. |
| 비사용 조건 또는 경계가 있음 | 3 | skill을 쓰지 말아야 할 경우나 다른 skill로 넘겨야 할 경우를 설명한다. |
| 입력/출력/대상 artifact가 명확함 | 3 | 필요한 입력, 생성/수정할 artifact, 기대 출력이 구체적이다. |
| scope creep를 막는 지침이 있음 | 3 | 승인된 범위 밖으로 확장하지 않도록 제한 규칙이 있다. |
| 유사 skill과의 관계가 설명됨 | 2 | 관련 skill, 대체 skill, 선행 skill과의 관계를 설명한다. |

Local caps:

- 사용 조건이 한 문장 이하로 모호하면 A는 최대 8/15.
- 거의 모든 작업에 적용될 만큼 trigger가 넓으면 A는 최대 10/15이며 global cap도 검토한다.

### B. Operational Procedure Quality — 20 points

| Checklist Criterion | Points | Recognition Standard |
|---|---:|---|
| 단계가 실행 순서대로 정리됨 | 4 | discovery, plan, execution, verification 등 단계 순서가 명확하다. |
| 명령/API/file path/output 예시가 구체적임 | 4 | 실제 command, API, file path, schema, output 예시가 있다. |
| prerequisite discovery가 포함됨 | 3 | 실행 전 확인해야 할 repo 상태, config, credentials, environment, existing convention 등을 확인한다. |
| plan/execution/verification 단계가 분리됨 | 3 | 계획, 실행, 검증, 보고가 혼동되지 않는다. |
| 반복 가능한 workflow로 구성됨 | 3 | 다른 세션과 유사 작업에서도 다시 쓸 수 있는 절차다. |
| actionable instruction이 많음 | 3 | 일반론보다 agent가 바로 수행할 수 있는 구체 지시가 많다. |

Local caps:

- 실행 가능한 step이 없으면 B는 최대 8/20.
- command/path/tool 예시가 전혀 없으면 B는 최대 12/20.
- 순서가 뒤섞여 agent가 실행 계획을 재구성해야 하면 B는 최대 15/20.
- 핵심 workflow가 암시적이라 evaluator가 절차를 추론해야 하면 B는 최대 14/20이며 global cap도 검토한다.

### C. User Preference / Boundary Alignment — 15 points

| Checklist Criterion | Points | Recognition Standard |
|---|---:|---|
| approval gate가 명확함 | 4 | destructive, external post, credential, production, persistent config/memory/skill/cron 변경 전에 explicit approval을 요구한다. |
| low-risk action은 불필요하게 묻지 않음 | 3 | read-only discovery, file inspection, log/status check, parsing, low-risk verification은 바로 수행하도록 구분한다. |
| evidence-first 보고 형식 반영 | 3 | 변경 사항, 검증 결과, 파일 경로, 남은 문제, 승인 필요 사항을 간결하게 보고하도록 한다. |
| scope를 좁고 명시적으로 유지 | 2 | 사용자가 승인한 범위만 수행하고 broad scope expansion을 피한다. |
| project/user convention 반영 가능 | 2 | Korean-first, machine identifier 보존, repo convention 등 사용자별 기준을 적용할 수 있다. |
| uncertainty handling 있음 | 1 | 확인됨/추정/미확인 또는 assumption labeling을 요구한다. |

Local caps:

- approval gate가 필요한 도메인인데 언급이 없으면 C는 최대 7/15.
- 사용자 선호와 정면 충돌하는 지시가 있으면 C는 최대 8/15이며 global cap도 검토한다.

### D. Verification & Evidence Discipline — 15 points

| Checklist Criterion | Points | Recognition Standard |
|---|---:|---|
| 완료 조건이 명확함 | 3 | 어떤 output 또는 state가 있으면 완료인지 정의한다. |
| 실제 검증 방법 명시 | 4 | file read-back, parse/lint/test, API response, UI confirmation, git diff/status, health check 등 검증 방법이 있다. |
| 서브에이전트/tool 결과 재검증 | 2 | 서브에이전트 self-report를 그대로 믿지 않고 parent가 artifact나 output을 확인하게 한다. |
| machine-checkable artifact 사용 | 2 | JSON schema, fixed field, deterministic checker, parseable scorecard 등을 사용한다. |
| verification 실패 보고 | 2 | 검증이 막힌 경우 blocked/unverified 상태와 이유를 보고한다. |
| fabricated output 금지 | 2 | tool을 실행한 척하거나 evidence 없는 완료 보고를 하지 않도록 명시한다. |

Local caps:

- verification이 전혀 없으면 D는 최대 5/15이며 global cap을 적용한다.
- 검증이 “확인한다” 수준의 추상 표현뿐이면 D는 최대 8/15.

### E. Failure Handling & Recovery — 10 points

| Checklist Criterion | Points | Recognition Standard |
|---|---:|---|
| 실패 command/API/tool과 error 보고 | 2 | 실패한 실행 단위와 핵심 error를 숨기지 않는다. |
| likely cause / impact / recovery 구분 | 2 | 원인 추정, 영향, 다음 복구 행동을 분리해 보고한다. |
| retry 또는 alternative path 기준 | 2 | 재시도할 조건과 다른 접근으로 전환할 조건이 있다. |
| partial/blocked/unverified 상태 구분 | 2 | 일부 완료, 차단, 미검증 상태를 명확히 구분한다. |
| skill patch/update 기준 | 2 | skill 자체가 틀렸거나 누락된 경우 패치해야 하는 기준이 있다. |

Local caps:

- 실패를 일반적인 “문제가 있었다” 수준으로만 다루면 E는 최대 5/10.
- 실패를 숨기거나 성공처럼 보고하게 만드는 지침이 있으면 global cap을 적용한다.

### F. Reusability & Portability — 10 points

| Checklist Criterion | Points | Recognition Standard |
|---|---:|---|
| stable procedure와 task artifact 분리 | 2 | 재사용할 절차와 특정 실행 결과/로그를 구분한다. |
| 환경 의존성 명시 | 2 | OS, CLI, credential, API, repo structure 등 전제 조건을 명시한다. |
| project-specific 경로와 일반 원칙 구분 | 2 | 고정 경로가 필요한 경우와 이식 가능한 절차를 구분한다. |
| versioning/update 기준 | 2 | skill 변경, stale instruction, calibration update 기준이 있다. |
| calibration/example이 rule을 오염시키지 않음 | 2 | 예시는 참고용이며 canonical rule과 분리된다. |

Local caps:

- 특정 사건/PR/날짜에 과적합되어 있으면 F는 최대 5/10.
- 현재 환경에서만 암묵적으로 작동하고 의존성을 설명하지 않으면 F는 최대 7/10.
- 특정 제품명/에이전트명에 불필요하게 종속되어 범용 재사용성이 낮으면 F는 최대 6/10이며 global cap도 검토한다.

### G. Structure, Consistency, and Cognitive Load — 8 points

| Checklist Criterion | Points | Recognition Standard |
|---|---:|---|
| headings가 명확하고 탐색 가능함 | 2 | agent가 필요한 섹션을 빠르게 찾을 수 있다. |
| 핵심 절차가 bullet/numbered steps로 압축됨 | 2 | 긴 산문보다 실행 순서가 눈에 띈다. |
| 모순되거나 충돌하는 지시가 없음 | 2 | approval, execution, verification, reporting 규칙이 서로 충돌하지 않는다. |
| 모호한 표현이 적고 결정 흐름이 직관적임 | 1 | “적절히”, “필요시” 같은 표현이 기준 없이 남발되지 않는다. |
| final report template이 있음 | 1 | 작업 후 보고 형식이 있다. |

Local caps:

- 길지만 구조가 없어 agent가 다시 요약해야 하면 G는 최대 4/8.
- 과도한 배경 설명이 절차를 가리면 G는 최대 6/8.
- 모순되거나 충돌하는 지시가 있으면 G는 최대 4/8.

### H. Parallelization, Context Management & Deterministic Automation — 7 points

| Checklist Criterion | Points | Recognition Standard |
|---|---:|---|
| 병렬 처리 가능성 판단 기준 있음 | 1 | 독립적으로 처리 가능한 작업과 순차 의존성이 있는 작업을 구분한다. |
| 서브에이전트/병렬 검토 활용 기준 있음 | 1 | 동시 처리가 가능한 작업은 병렬로 수행해 작업 속도를 높이고, 결과를 중앙에서 종합한다. |
| 큰 컨텍스트 작업의 분할 기준 있음 | 1 | 큰 로그/문서/코드베이스/복수 후보 비교를 shard로 나누어 컨텍스트 오염을 줄인다. |
| 결정론적/비결정론적 작업 분리 기준 있음 | 2 | 파싱, 집계, 정규화, schema 검증처럼 결정론적인 부분은 스크립트로 처리하고, 판단/해석/우선순위화처럼 비결정론적인 부분만 agent reasoning에 맡긴다. |
| 공통 재사용 스크립트 설계 기준 있음 | 1 | 단계마다 일회성 스크립트를 만들지 않고, 여러 단계/샘플에 반복 적용 가능한 공통 스크립트를 설계한다. |
| 컨텍스트 오염 방지 artifact 규칙 있음 | 1 | 중간 산출물을 JSON/schema/fixed field/path로 저장해 parent context와 토큰 사용량을 줄인다. |

Local caps:

- tool 사용이 모두 일반론이면 H는 최대 4/7.
- 큰 컨텍스트 작업인데 분할/서브에이전트/중간 artifact 전략이 없으면 H는 최대 3/7.
- 동시 처리가 가능한 독립 작업인데 순차 처리만 지시하면 H는 최대 4/7.
- 결정론적 작업을 스크립트화하지 않고 agent reasoning에 맡기면 H는 최대 4/7.
- 각 단계별 일회성 스크립트만 만들고 공통 스크립트 설계가 없으면 H는 최대 5/7.
- 특정 실행 환경에만 맞는 tool name에 과도하게 묶여 범용성이 낮으면 H는 최대 5/7.

## 6. Global Caps and Penalties

체크리스트 총점을 먼저 계산한 뒤 아래 cap을 적용한다. 여러 cap이 적용되면 가장 낮은 cap을 사용한다.

- 한국어로 작성되어 있지 않으면 총점 80점 cap. 대부분이 외국어이고 한국어 사용자용 skill로 보기 어려우면 총점 65점 cap.
- 특정 제품명/에이전트명에 불필요하게 종속되어 범용 skill로 재사용하기 어렵다면 총점 75점 cap. 특정 플랫폼 연동 skill은 예외지만, 범용 절차와 플랫폼 고유 절차를 분리해야 한다.
- 실제 절차가 없고 개념 설명만 있으면 총점 60점 cap.
- approval boundary가 없는데 destructive/external/credential/production 액션을 다루면 총점 55점 cap.
- verification이 전혀 없으면 총점 70점 cap.
- fabricated output, 실행한 척하는 지침, evidence 없는 완료 보고를 허용하면 총점 50점 cap.
- 사용자 선호나 프로젝트 convention과 정면 충돌하면 총점 65점 cap.
- trigger가 너무 넓어 거의 모든 작업에 로드될 수준이면 총점 75점 cap.
- 스킬 본문이 특정 1회성 사건 로그에 가까우면 총점 70점 cap.
- 보안/프라이버시 위험을 부추기면 총점 50점 cap.
- 핵심 workflow가 암시적이어서 evaluator가 절차를 추론해야 하면 총점 70점 cap.
- 큰 컨텍스트 작업을 다루면서 서브에이전트/병렬 검토/중간 artifact 분리 전략이 전혀 없으면 총점 80점 cap.
- 결정론적 반복 처리와 비결정론적 추론을 구분하지 않아 모든 작업을 agent reasoning에 맡기면 총점 75점 cap.
- 단계마다 일회성 스크립트를 남발하고 공통 재사용 가능한 자동화로 정리하지 않으면 총점 80점 cap.

## 7. Score Interpretation

| Total Score | Interpretation |
|---:|---|
| 90–100 | Excellent. 반복 사용 가능한 고품질 skill. 작은 보완만 필요. |
| 80–89 | Good. 실사용 가능하나 일부 boundary, verification, structure 보완 필요. |
| 70–79 | Adequate. 핵심은 있으나 운영 안정성이 부족함. |
| 60–69 | Weak. substantial revision 필요. agent 행동 개선 효과가 제한적임. |
| 0–59 | Poor. skill로 사용하기 어렵거나 위험함. 재작성 권장. |

## 8. Scoring Procedure

1. 평가 packet을 연다. packet에는 평가 대상 skill 본문, 포함 파일 목록, 필요한 참조 파일 내용, 실행 환경 메모만 있어야 한다.
2. 현재 대화, judge 자신의 memory, 구현 과정 메모, 이전 평가 인상은 사용하지 않는다.
3. 평가 대상 skill의 intended trigger, scope, artifact, 위험 행동 경계를 3–5문장으로 요약한다.
4. global cap 후보를 먼저 메모하되, 총점은 아직 결정하지 않는다.
5. 각 dimension의 checklist item을 evidence 기반으로 채점한다. evidence에는 실제 문구, 섹션명, 파일명, 절차 요약을 넣는다.
6. dimension별 local cap 또는 penalty를 적용한다.
7. dimension 점수를 합산한다.
8. global cap을 적용한다. 여러 cap이 적용되면 가장 낮은 cap을 사용한다.
9. top strengths, critical weaknesses, recommended patches를 작성한다.
10. `score_schema.json`에 맞는 JSON만 출력한다.

## 9. Judge Execution Mode

기본 실행 모드는 `clean_subagent`이다. judge는 평가 대상 skill을 작성하거나 수정한 컨텍스트와 분리된 깨끗한 독립 컨텍스트에서 실행해야 한다.

- `clean_subagent`: 단일 skill 또는 단순 평가의 기본값이다. judge는 packet에 포함된 평가 대상 artifact와 canonical rubric만 사용한다.
- `parallel_clean_subagents`: multi-dimension 평가, high-stakes 평가, 큰 skill package, 여러 후보 비교, 또는 judge variance를 줄여야 하는 경우의 권장 모드다.
- `same_context_exception`: 도구 제약 때문에 clean judge를 만들 수 없거나 긴급 triage만 하는 예외 모드다. 이 경우 `judging_context`에 반드시 `same_context_exception`을 기록하고 `context_contamination_notes`에 오염 가능성을 설명한다.

Parallel clean-subagent workflow:

1. parent는 canonical rubric, 평가 대상 packet, shard assignment를 각 clean subagent에 전달한다.
2. shard judge는 자신에게 배정된 dimension/checklist shard만 평가한다. 예: A–C, D–F, G–H, global cap 후보 검토 등.
3. shard judge는 부분 JSON 또는 parseable fragment로 checklist evidence, raw score, cap 후보, uncertainty만 반환한다.
4. parent가 중앙에서 JSON parse, score bounds 확인, 누락/중복 criterion 탐지, 서로 모순되는 판단 reconciliation, local/global cap 적용, 최종 grade 산출을 수행한다.
5. parent는 deterministic parse/aggregation/schema validation을 재사용 가능한 스크립트로 처리하고, judgment-heavy reconciliation만 agent reasoning으로 수행한다.
6. parent는 최종 `judging_context`를 `parallel_clean_subagents`로 기록하고, shard 간 불일치와 해결 방식을 `context_contamination_notes` 또는 `summary`에 요약한다.

Same-context judging은 품질 평가의 표준 모드가 아니며, 최종 점수를 운영 의사결정에 사용할 때는 clean 또는 parallel clean 재평가를 권장한다.

## 10. Judge Prompt

Canonical judge prompt는 `/Users/stark/project/jarvis/ai_tool/rubric/skill/judge_prompt.md`에 둔다. prompt는 다음 원칙을 반드시 포함해야 한다.

- 깨끗한 독립 컨텍스트에서 실행한다.
- 현재 대화, judge memory, implementation notes, 작성자 self-report를 근거로 사용하지 않는다.
- packet에 포함된 skill content, included reference/template/script, canonical rubric, score schema만 사용한다.
- 점수를 먼저 정하지 않고 checklist evidence를 먼저 채점한다.
- 특정 repository, source family, local collection을 gold standard로 보지 않는다. 모두 calibration sample일 뿐이다.
- 한국어-first 여부, 모순/모호함, 범용 agent skill로서의 이식성, 플랫폼-specific 절차와 범용 절차의 분리 여부를 평가한다.
- 병렬화는 컨텍스트 오염 방지뿐 아니라 동시 처리 가능한 task를 식별해 속도를 높이는지까지 본다.
- 결정론적 파싱/집계/정규화/schema 검증은 재사용 가능한 스크립트로 처리하는지, 판단/해석/우선순위화만 agent reasoning에 맡기는지 평가한다.
- JSON 외의 commentary를 출력하지 않는다.

## 11. JSON Output Schema

최종 출력은 `/Users/stark/project/jarvis/ai_tool/rubric/skill/score_schema.json`을 따른다. 필수 top-level field는 다음과 같다.

- `skill_path`
- `skill_name`
- `judging_context`: `clean_subagent`, `parallel_clean_subagents`, `same_context_exception` 중 하나.
- `context_contamination_notes`: clean/parallel 여부, packet 외 정보 배제 여부, same-context 예외 사유.
- `total_score`
- `max_score`
- `grade`
- `summary`
- `global_caps_applied`
- `dimension_scores`
- `top_strengths`
- `critical_weaknesses`
- `recommended_patches`
- `needs_human_review`
- `confidence`

Schema validation은 deterministic step이다. 반복 실행 가능한 JSON parse/schema validation 스크립트로 검증하고, schema mismatch를 agent reasoning으로 눈대중 처리하지 않는다.

## 12. Calibration Notes

이 루브릭은 v1 초안이다. 실제 사용 전 `/Users/stark/project/jarvis/ai_tool/rubric/skill/calibration/README.md`의 절차에 따라 calibration한다.

특정 repository, source family, local collection은 최고의 기준이 아니라 calibration sample이다. 출처 이름값을 보상하지 않고, skill이 명시적이고 재사용 가능하며 검증 가능한 workflow를 제공하는지만 본다.

최소 calibration sample:

- 매우 좋은 스킬 2개.
- 평균적인 스킬 2개.
- 그럴듯하지만 실행성 낮은 스킬 2개.
- 위험 경계가 빠진 스킬 1개.
- 너무 장황하거나 추상적인 스킬 1개.
- 특정 제품명/에이전트명에 과하게 묶인 스킬 1개.
- 큰 컨텍스트 작업인데 병렬화/서브에이전트 분리가 없는 스킬 1개.
- 동시 처리가 가능한 작업을 순차 처리하도록 만드는 스킬 1개.
- 결정론적 처리와 비결정론적 추론을 구분하지 못하는 스킬 1개.
- 단계마다 일회성 스크립트를 만드는 과잉 자동화 스킬 1개.

Calibration에서는 clean-subagent judging을 기본으로 하고, multi-dimension 또는 high-stakes sample은 parallel clean-subagent judging으로 반복 평가한다. deterministic 요소(JSON parse, score aggregation, bounds check, schema validation)는 재사용 가능한 스크립트로 검증하고, nondeterministic 요소(근거 해석, priority 판단, patch 권장)는 judge reasoning으로 비교한다.

확인 질문:

- 좋은 스킬이 높은 점수를 받는가?
- 장황하지만 실행성 낮은 스킬이 과점되지 않는가?
- approval/verification 누락이 cap으로 잡히는가?
- 사용자 취향과 맞지 않는 스킬이 적절히 감점되는가?
- 모순/모호함이 있는 skill이 구조 점수와 cap에서 잡히는가?
- 한국어-first hard rule이 실제로 적용되는가?
- 특정 제품명/에이전트명에 과하게 묶인 skill이 범용성 감점을 받는가?
- 서브에이전트/병렬 workflow가 필요한 작업에서 해당 지침 누락이 감점되는가?
- 동시 처리가 가능한 작업을 순차 처리하도록 만든 skill이 감점되는가?
- 결정론적 처리와 비결정론적 추론의 분리 실패가 감점되는가?
- 일회성 스크립트 남발 대신 공통 재사용 스크립트를 요구하는가?
- clean judge 간 점수 차이가 5–8점 안에 들어오는가?
