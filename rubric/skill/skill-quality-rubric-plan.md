# Skill Quality Rubric 개발 계획

## 1. 목적

이 계획은 agent skill, 외부 skill repository의 workflow 문서, command workflow skill, coding-agent playbook, research/ops automation skill을 평가하기 위한 재사용 가능 루브릭을 설계한다.

여기서 특정 repository나 기존 skill 묶음은 “최고의 기준”이 아니라 calibration sample 후보일 뿐이다. 좋은 스킬의 기준은 이름값이나 출처가 아니라, 작업 workflow가 암시적으로 숨지 않고 직관적이고 명시적으로 잘 동작하는가에 있다.

핵심 평가 질문:

- 이 스킬이 agent에게 실제로 더 나은 행동을 하게 만드는가?
- 반복 사용 시 일관된 품질을 보장하는가?
- 모순이나 모호함이 없고 직관적인 구조로 되어 있는가?
- 사용자의 취향, 승인 경계, 검증 기준, 실패 처리 방식과 맞는가?
- 단순 설명 문서가 아니라 실행 가능한 절차 기억인가?
- 동시 처리가 가능한 작업을 식별해 서브에이전트/병렬 작업으로 속도를 높이고, 동시에 컨텍스트 오염을 줄이도록 유도하는가?
- 결정론적 처리와 비결정론적 추론을 구분해, 결정론적 부분은 재사용 가능한 스크립트로 안정화하고 비결정론적 부분만 agent reasoning에 맡기는가?

## 2. 평가 대상

- 로컬 agent skill
- 외부 skill repository의 agent workflow 문서
- coding/research/devops/productivity 자동화 skill
- LLM agent에게 procedure, boundary, verification, reporting style을 주입하는 문서

## 3. 좋은 스킬의 정의

좋은 스킬은 다음 조건을 만족한다.

1. 언제 써야 하는지 명확하다.
2. 실행 절차가 구체적이다.
3. 위험한 액션의 approval boundary가 분리되어 있다.
4. 검증 방법이 있다.
5. 실패/복구 경로가 있다.
6. 도구, 파일, 명령, 출력 포맷이 명확하다.
7. 불필요한 추상론보다 실제 재사용성을 우선한다.
8. 특정 1회성 사건 로그가 아니라 stable operational knowledge로 구성된다.
9. 모순되거나 모호한 지시가 없고, 직관적인 섹션 구조와 결정 흐름을 갖는다.
10. 큰 컨텍스트나 다면적 판단이 필요한 작업에서는 서브에이전트와 병렬 검토를 활용해 컨텍스트 오염을 줄이고 작업 속도를 높인다.
11. 작업 시퀀스에서 결정론적 단계와 비결정론적 단계를 구분하고, 결정론적 반복 처리는 공통 재사용 스크립트로 만든다.
12. 각 단계마다 임시 스크립트를 남발하지 않고, 여러 작업에 공통 적용 가능한 스크립트와 agent reasoning이 필요한 판단 지점을 분리한다.
13. 한국어로 작성되어 있고, machine identifier, command, path, API name처럼 필요한 식별자만 원문을 유지한다.
14. 특정 제품명/에이전트명에 과도하게 묶이지 않고 범용 agent skill로 재사용 가능하다. 단, 특정 플랫폼 연동을 다루는 skill은 예외적으로 해당 플랫폼명을 명시할 수 있다.

## 4. 루브릭 v1 배점 초안

| Dimension | Points | Focus |
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

## 5. Hard Rules / Global Cap 초안

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
- 결정론적 반복 처리와 비결정론적 추론을 구분하지 않아 모든 작업을 agent reasoning에 맡기면 총점 75점 cap.
- 단계마다 일회성 스크립트를 남발하고 공통 재사용 가능한 자동화로 정리하지 않으면 총점 80점 cap.

## 6. Local Cap 초안

- A. Trigger & Scope Precision: 사용 조건이 한 문장 이하로 모호하면 A는 최대 8/15.
- B. Operational Procedure: 실행 가능한 step이 없으면 B는 최대 8/20.
- B. Operational Procedure: command/path/tool 예시가 전혀 없으면 B는 최대 12/20.
- C. User Alignment: approval gate가 필요한 도메인인데 언급이 없으면 C는 최대 7/15.
- D. Verification: 검증이 “확인한다” 수준의 추상 표현뿐이면 D는 최대 8/15.
- F. Reusability: 특정 사건/PR/날짜에 과적합되어 있으면 F는 최대 5/10.
- G. Structure: 모순되거나 충돌하는 지시가 있으면 G는 최대 4/8.
- H. Parallelization/Automation: 큰 컨텍스트 작업인데 서브에이전트/병렬 검토/중간 artifact 분리가 없으면 H는 최대 3/7.
- H. Parallelization/Automation: 동시 처리가 가능한 독립 작업인데 순차 처리만 지시하면 H는 최대 4/7.
- H. Parallelization/Automation: 결정론적 작업을 스크립트화하지 않고 agent reasoning에 맡기면 H는 최대 4/7.
- H. Parallelization/Automation: 각 단계별 일회성 스크립트만 만들고 공통 스크립트 설계가 없으면 H는 최대 5/7.

## 7. 산출물

v1 artifact는 아래 파일로 분리한다.

```text
/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-plan.md
/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md
/Users/stark/project/jarvis/ai_tool/rubric/skill/judge_prompt.md
/Users/stark/project/jarvis/ai_tool/rubric/skill/score_schema.json
/Users/stark/project/jarvis/ai_tool/rubric/skill/calibration/README.md
```

Canonical rubric 문서인 `skill-quality-rubric-v1.md`는 최신 rubric-design 출력 형식에 맞춰 다음 섹션 구조를 유지한다.

1. Evaluation Purpose
2. Evaluation Target
3. Total Score
4. Dimension Summary
5. Detailed Scoring Criteria
6. Global Caps and Penalties
7. Score Interpretation
8. Scoring Procedure
9. Judge Execution Mode
10. Judge Prompt
11. JSON Output Schema
12. Calibration Notes

`score_schema.json`은 최소한 `skill_path`, `skill_name`, `judging_context`, `context_contamination_notes`, `total_score`, `max_score`, `grade`, `summary`, `global_caps_applied`, `dimension_scores`, `top_strengths`, `critical_weaknesses`, `recommended_patches`, `needs_human_review`, `confidence`를 top-level required field로 가진다. `judging_context` enum은 `clean_subagent | parallel_clean_subagents | same_context_exception`이다.

## 8. Judge 실행 모드

기본 judge 실행 모드는 `clean_subagent`다. 평가자는 skill 작성/수정 컨텍스트와 분리된 깨끗한 독립 컨텍스트에서 packet만 보고 평가한다. current conversation, memory, implementation notes, 작성자 self-report는 근거로 사용하지 않는다.

Multi-dimension, high-stakes, 큰 skill package, 여러 후보 비교, judge variance가 큰 평가에서는 `parallel_clean_subagents` workflow를 사용한다.

1. parent가 canonical rubric, score schema, 평가 packet, shard assignment를 clean subagent에 전달한다.
2. shard judge는 배정된 dimension/checklist shard만 평가하고 최종 총점은 확정하지 않는다.
3. parent가 JSON parse, score bounds, missing/duplicate criteria, contradiction reconciliation, local/global cap application을 중앙에서 수행한다.
4. deterministic aggregation/schema validation은 재사용 가능한 스크립트로 처리하고, nondeterministic reconciliation만 agent reasoning으로 처리한다.

`same_context_exception`은 예외 모드이며, 사용할 경우 오염 가능성과 제한을 `context_contamination_notes`에 기록한다.

## 9. Calibration 계획

아래 repository/style은 “최고의 기준”이 아니라 비교 평가와 calibration을 위한 sample family다. 출처별 이름값을 점수로 보상하지 않고, 각 skill이 얼마나 명시적이고 재사용 가능하며 검증 가능한 workflow를 제공하는지만 본다.

레퍼런스 후보:

- gstack 계열 skill: 실행성/operational workflow sample.
- superpower 계열 skill: agent behavior-shaping sample.
- mattpocock 계열 skill: concise, practical, coding-workflow sample.
- 현재 local skills: 실제 사용성/사용자 취향 적합성 sample.

샘플 세트:

1. 매우 좋은 스킬 2개.
2. 평균적인 스킬 2개.
3. 그럴듯하지만 실행성 낮은 스킬 2개.
4. 위험 경계가 빠진 스킬 1개.
5. 너무 장황하거나 추상적인 스킬 1개.
6. 특정 제품명/에이전트명에 과하게 묶인 스킬 1개.
7. 큰 컨텍스트 작업인데 병렬화/서브에이전트 분리가 없는 스킬 1개.
8. 동시 처리가 가능한 작업을 순차 처리하도록 만드는 스킬 1개.
9. 결정론적 처리와 비결정론적 추론을 구분하지 못하는 스킬 1개.
10. 단계마다 일회성 스크립트를 만드는 과잉 자동화 스킬 1개.

검증 질문:

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

## 10. v1 작성 원칙

v1은 예쁜 문서 루브릭보다 agent가 실제로 점수화 가능한 checklist + cap-heavy rubric으로 작성한다.

특히 강하게 볼 요소:

1. 실행 가능한 절차인가.
2. approval/verification/failure boundary가 있는가.
3. 사용자의 실제 취향과 운영 방식에 맞는가.
4. 반복 사용 가능한 skill memory인가.
5. 모순과 모호함 없이 직관적으로 읽히는가.
6. 큰 작업을 단일 컨텍스트에 밀어 넣지 않고 병렬/서브에이전트 workflow로 분해하는가.
7. 동시 처리가 가능한 작업을 식별해 작업 속도를 높이는가.
8. 결정론적 부분은 스크립트로, 비결정론적 판단은 agent reasoning으로 분리하는가.
9. 단계별 일회성 스크립트가 아니라 공통 재사용 스크립트를 설계하는가.
10. 한국어-first, 범용 agent skill 원칙을 지키는가.

## 11. 나중에 할 검증 작업

- 실제 local/external skill 샘플을 모아 blind scoring.
- 점수 분포와 human preference 순위 비교.
- high score를 받은 스킬이 실제로 재사용 가능한지 task replay로 확인.
- weak skill이 왜 낮게 나오는지 checklist evidence 확인.
- judge prompt와 score schema가 parse 안정적인지 반복 실행으로 확인.
- 특정 sample family가 “정답 스타일”로 과대 보상되지 않는지 확인.
