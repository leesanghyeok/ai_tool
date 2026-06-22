# Skill Quality Rubric 개발 계획

## 1. 목적

이 계획은 Hermes skill, gstack/superpower/mattpocock 류 agent skill, command workflow skill, coding-agent playbook, research/ops automation skill을 평가하기 위한 재사용 가능 루브릭을 설계한다.

핵심 평가 질문:

- 이 스킬이 agent에게 실제로 더 나은 행동을 하게 만드는가?
- 반복 사용 시 일관된 품질을 보장하는가?
- 사용자의 취향, 승인 경계, 검증 기준, 실패 처리 방식과 맞는가?
- 단순 설명 문서가 아니라 실행 가능한 절차 기억인가?

## 2. 평가 대상

- Hermes local skills
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

## 4. 루브릭 v1 배점 초안

| Dimension | Points | Focus |
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

## 5. Global Cap 초안

- 실제 절차가 없고 개념 설명만 있으면 총점 60점 cap.
- approval boundary가 없는데 destructive/external/credential/production 액션을 다루면 총점 55점 cap.
- verification이 전혀 없으면 총점 70점 cap.
- fabricated output, 실행한 척하는 지침, evidence 없는 완료 보고를 허용하면 총점 50점 cap.
- 사용자 선호나 프로젝트 convention과 정면 충돌하면 총점 65점 cap.
- trigger가 너무 넓어 거의 모든 작업에 로드될 수준이면 총점 75점 cap.
- 스킬 본문이 특정 1회성 사건 로그에 가까우면 총점 70점 cap.
- 보안/프라이버시 위험을 부추기면 총점 50점 cap.

## 6. Local Cap 초안

- A. Trigger & Scope Precision: 사용 조건이 한 문장 이하로 모호하면 A는 최대 8/15.
- B. Operational Procedure: 실행 가능한 step이 없으면 B는 최대 8/20.
- B. Operational Procedure: command/path/tool 예시가 전혀 없으면 B는 최대 12/20.
- C. User Alignment: approval gate가 필요한 도메인인데 언급이 없으면 C는 최대 7/15.
- D. Verification: 검증이 “확인한다” 수준의 추상 표현뿐이면 D는 최대 8/15.
- F. Reusability: 특정 사건/PR/날짜에 과적합되어 있으면 F는 최대 5/10.

## 7. 산출물

최초 v1은 아래 파일로 분리한다.

```text
/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-plan.md
/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md
/Users/stark/project/jarvis/ai_tool/rubric/skill/judge_prompt.md
/Users/stark/project/jarvis/ai_tool/rubric/skill/score_schema.json
/Users/stark/project/jarvis/ai_tool/rubric/skill/calibration/README.md
```

## 8. Calibration 계획

레퍼런스 후보:

- gstack 계열 skill: 실행성/operational workflow 기준.
- superpower 계열 skill: agent behavior-shaping 기준.
- mattpocock 계열 skill: concise, practical, coding-workflow 기준.
- 현재 Hermes local skills: 실제 사용성/사용자 취향 적합성 기준.

샘플 세트:

1. 매우 좋은 스킬 2개.
2. 평균적인 스킬 2개.
3. 그럴듯하지만 실행성 낮은 스킬 2개.
4. 위험 경계가 빠진 스킬 1개.
5. 너무 장황하거나 추상적인 스킬 1개.

검증 질문:

- 좋은 스킬이 높은 점수를 받는가?
- 장황하지만 실행성 낮은 스킬이 과점되지 않는가?
- approval/verification 누락이 cap으로 잡히는가?
- 사용자 취향과 맞지 않는 스킬이 적절히 감점되는가?
- judge 간 점수 차이가 5–8점 안에 들어오는가?

## 9. v1 작성 원칙

v1은 예쁜 문서 루브릭보다 agent가 실제로 점수화 가능한 checklist + cap-heavy rubric으로 작성한다.

특히 강하게 볼 요소:

1. 실행 가능한 절차인가.
2. approval/verification/failure boundary가 있는가.
3. 사용자의 실제 취향과 운영 방식에 맞는가.
4. 반복 사용 가능한 skill memory인가.

## 10. 나중에 할 검증 작업

- 실제 local/external skill 샘플을 모아 blind scoring.
- 점수 분포와 human preference 순위 비교.
- high score를 받은 스킬이 실제로 재사용 가능한지 task replay로 확인.
- weak skill이 왜 낮게 나오는지 checklist evidence 확인.
- judge prompt와 score schema가 parse 안정적인지 반복 실행으로 확인.
