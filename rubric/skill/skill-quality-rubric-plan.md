# Agent Skill 품질 루브릭 개발 계획

## 목적

`/Users/stark/project/jarvis/ai_tool/rubric/llm-wiki/llm-wiki-quality-rubric-v1.md`의 형식을 기준으로 agent skill 품질 루브릭을 다시 작성한다.

이번 버전은 기존 broad category rubric이 아니라 다음 구조를 따른다.

- 평가 목적
- 평가 대상
- 통과 기준
- Dimension 요약
- 세부 채점 기준
- Global caps and certification rules
- 점수 해석
- 채점 절차
- Judge 지침
- JSON scorecard schema
- Calibration notes

## 핵심 판단 기준

- 특정 repository/source family/local collection은 최고의 기준이 아니라 calibration sample이다.
- 좋은 skill은 workflow가 암시적으로 동작하지 않고 직관적이고 명시적으로 동작해야 한다.
- 모순/모호함이 없어야 한다.
- 한국어-first human-facing prose를 사용해야 한다.
- 특정 제품명/에이전트명에 불필요하게 종속되지 않아야 한다.
- 병렬화는 context 오염 방지뿐 아니라 동시 처리 가능한 task의 속도 개선까지 포함한다.
- 결정론적 처리와 비결정론적 추론을 분리해야 한다.
- 결정론적 파싱/집계/정규화/schema 검증은 공통 재사용 script로 처리해야 한다.
- 판단/해석/우선순위화 등 비결정론적 부분만 agent reasoning에 맡겨야 한다.
- 단계마다 일회성 script를 만드는 방식은 피해야 한다.

## Artifact 구성

```text
/Users/stark/project/jarvis/ai_tool/rubric/skill/
  skill-quality-rubric-plan.md
  skill-quality-rubric-v1.md
  judge_prompt.md
  score_schema.json
  calibration/
    README.md
  _backup/
    YYYYMMDDTHHMMSSZ/
      ...previous artifacts...
```

## Dimension 설계

| ID | 차원 | 점수 | Gate Type |
|---|---:|---:|---|
| D1 | Trigger & Scope Precision | 15 | Hard gate |
| D2 | Operational Workflow Explicitness | 20 | Hard gate |
| D3 | Safety, Approval & Boundary Alignment | 15 | Hard gate |
| D4 | Verification & Evidence Discipline | 15 | Hard gate |
| D5 | Reusability, Generality & Language Fit | 10 | Hard gate |
| D6 | Failure Handling & Recovery | 10 | Quality |
| D7 | Structure, Consistency & Cognitive Load | 8 | Quality |
| D8 | Parallelization, Context Management & Deterministic Automation | 7 | Quality |
| **Total** |  | **100** |  |

## 통과 기준

- baseline passing score: 90 / 100
- D1 >= 13
- D2 >= 17
- D3 >= 13
- D4 >= 13
- D5 >= 8
- hard gate 하나라도 실패하면 certification score cap은 89

## 검증 계획

- `score_schema.json` JSON parse.
- canonical rubric에 D1-D8, hard gate, local cap, global cap, JSON scorecard schema가 있는지 확인.
- judge prompt가 packet-only clean context를 요구하는지 확인.
- calibration README가 source-family non-gold-standard와 deterministic/nondeterministic sample을 포함하는지 확인.

## origin/main 병합 보강 계획

`origin/main`에서 병합된 상세 계획은 다음 원칙으로 유지한다.

- Hard/global cap 초안과 local cap 초안은 canonical rubric 본문과 schema에 동기화한다.
- Calibration sample은 좋은 skill, 평균 skill, 그럴듯하지만 실행성 낮은 skill, 위험 경계 누락 skill, 장황/추상 skill, 특정 제품/에이전트에 과하게 묶인 skill, 병렬화 기회를 놓친 skill, deterministic/nondeterministic 처리를 혼동한 skill을 포함한다.
- Source family는 정답 스타일이 아니라 분포 확인용 sample family로만 사용한다.
- Judge 실행은 기본적으로 `clean_subagent`, 필요 시 `parallel_clean_subagents`이며, `same_context_exception`은 표준 결과로 확정하지 않는다.
- JSON parse, schema validation, score aggregation, variance summary, cap consistency check는 반복 사용 가능한 검증 script로 둔다.
- Task replay 검증으로 high-score skill이 실제 agent 행동을 개선하는지 확인한다.
