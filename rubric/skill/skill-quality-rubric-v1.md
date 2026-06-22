# Skill Quality Rubric v1

## 1. Evaluation Purpose

이 루브릭은 agent skill의 품질을 평가하기 위한 100점 기준이다. 목표는 skill이 단순히 잘 쓰인 문서인지가 아니라, agent가 반복 작업에서 더 정확하고 안전하고 검증 가능한 행동을 하도록 만드는지를 평가하는 것이다.

이 루브릭은 특히 다음 유형의 skill에 적용한다.

- Hermes skill
- gstack/superpower/mattpocock 류 agent workflow skill
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
| G. Structure, Concision, and Cognitive Load | 8 | agent가 빠르게 읽고 따를 수 있는 구조 |
| H. Integration with Agent Tooling / Environment | 7 | Hermes/Codex/tooling과의 결합도 |
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
| subagent/tool 결과 재검증 | 2 | subagent self-report를 그대로 믿지 않고 parent가 artifact나 output을 확인하게 한다. |
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

### G. Structure, Concision, and Cognitive Load — 8 points

| Checklist Criterion | Points | Recognition Standard |
|---|---:|---|
| headings가 명확하고 탐색 가능함 | 2 | agent가 필요한 섹션을 빠르게 찾을 수 있다. |
| 핵심 절차가 bullet/numbered steps로 압축됨 | 2 | 긴 산문보다 실행 순서가 눈에 띈다. |
| 결정 규칙 중심 | 2 | 배경 설명보다 조건, 판단 기준, 금지/허용 규칙이 중심이다. |
| 중복/모호한 표현이 적음 | 1 | 같은 내용이 반복되지 않고 용어가 일관된다. |
| final report template이 있음 | 1 | 작업 후 보고 형식이 있다. |

Local caps:

- 길지만 구조가 없어 agent가 다시 요약해야 하면 G는 최대 4/8.
- 과도한 배경 설명이 절차를 가리면 G는 최대 6/8.

### H. Integration with Agent Tooling / Environment — 7 points

| Checklist Criterion | Points | Recognition Standard |
|---|---:|---|
| 관련 tool choice가 구체적임 | 2 | terminal, read_file, search_files, browser, delegate_task, cronjob 등 사용할 도구가 구체적이다. |
| large-context sharding 기준 있음 | 1 | 큰 로그/문서/코드베이스는 subagent 또는 shard workflow를 사용한다. |
| persistent state 변경 경계가 있음 | 1 | memory, skill, cron, config, scheduler 변경의 approval boundary가 있다. |
| artifact 저장 규칙 있음 | 1 | path, schema, logs, scorecard 저장 위치나 형식이 있다. |
| existing convention 확인 절차 있음 | 1 | 기존 repo/project convention을 먼저 확인한다. |
| skill maintenance workflow 있음 | 1 | skill이 틀리거나 stale할 때 update/patch 기준이 있다. |

Local caps:

- tool 사용이 모두 일반론이면 H는 최대 4/7.
- 실제 Hermes/Codex 환경과 맞지 않는 명령을 중심으로 하면 H는 최대 5/7.

## 6. Global Caps and Penalties

체크리스트 총점을 먼저 계산한 뒤 아래 cap을 적용한다. 여러 cap이 적용되면 가장 낮은 cap을 사용한다.

- 실제 절차가 없고 개념 설명만 있으면 총점 60점 cap.
- approval boundary가 없는데 destructive/external/credential/production 액션을 다루면 총점 55점 cap.
- verification이 전혀 없으면 총점 70점 cap.
- fabricated output, 실행한 척하는 지침, evidence 없는 완료 보고를 허용하면 총점 50점 cap.
- 사용자 선호나 프로젝트 convention과 정면 충돌하면 총점 65점 cap.
- trigger가 너무 넓어 거의 모든 작업에 로드될 수준이면 총점 75점 cap.
- 스킬 본문이 특정 1회성 사건 로그에 가까우면 총점 70점 cap.
- 보안/프라이버시 위험을 부추기면 총점 50점 cap.
- skill 본문이 너무 짧아 평가 가능한 substance가 부족하면 총점 50점 cap.

## 7. Score Interpretation

| Total Score | Interpretation |
|---:|---|
| 90–100 | Excellent. 반복 사용 가능한 고품질 skill. 작은 보완만 필요. |
| 80–89 | Good. 실사용 가능하나 일부 boundary, verification, structure 보완 필요. |
| 70–79 | Adequate. 핵심은 있으나 운영 안정성이 부족함. |
| 60–69 | Weak. substantial revision 필요. agent 행동 개선 효과가 제한적임. |
| 0–59 | Poor. skill로 사용하기 어렵거나 위험함. 재작성 권장. |

## 8. Scoring Procedure

1. 평가 대상 skill 파일과 linked reference/template/script를 확인한다.
2. skill의 intended trigger와 operational scope를 요약한다.
3. global cap 후보를 먼저 메모하되, 총점은 아직 결정하지 않는다.
4. 각 dimension의 checklist item을 evidence 기반으로 채점한다.
5. dimension별 local cap을 적용한다.
6. dimension 점수를 합산한다.
7. global cap을 적용한다.
8. top strengths, critical weaknesses, recommended patches를 작성한다.
9. JSON schema에 맞춰 결과를 출력한다.

## 9. Judge Instructions

- 점수를 먼저 정하지 말고 checklist item을 먼저 채점한다.
- 평가 대상 skill에 명시된 내용만 근거로 사용한다.
- implied intent나 evaluator의 선의로 missing content에 점수를 주지 않는다.
- evidence에는 실제 문구, 섹션명, 파일명, 절차 요약을 넣는다.
- 길이와 전문 용어 자체를 보상하지 않는다.
- 실행성, approval boundary, verification discipline을 강하게 본다.
- cap은 checklist scoring 이후 적용한다.
- 여러 cap이 적용되면 가장 낮은 cap을 사용한다.
- 평가 불확실성이 높으면 `needs_human_review=true`로 표시한다.

## 10. Expected Final Report Template

```text
결론: {score}/100 — {grade}

강점:
- ...

주요 감점:
- ...

적용된 cap/penalty:
- ...

권장 수정:
- ...

검증/근거:
- 평가 대상 파일: ...
- 참조 파일 포함 여부: ...
- confidence: ...
```

## 11. Calibration Notes

이 루브릭은 v1 초안이다. 실제 사용 전 다음 샘플로 calibration한다.

- 매우 좋은 스킬 2개.
- 평균적인 스킬 2개.
- 그럴듯하지만 실행성 낮은 스킬 2개.
- 위험 경계가 빠진 스킬 1개.
- 너무 장황하거나 추상적인 스킬 1개.

Calibration에서는 다음을 확인한다.

- 좋은 스킬이 높은 점수를 받는가?
- 장황하지만 실행성 낮은 스킬이 과점되지 않는가?
- approval/verification 누락이 cap으로 잡히는가?
- 사용자 취향과 맞지 않는 스킬이 적절히 감점되는가?
- judge 간 점수 차이가 5–8점 안에 들어오는가?
