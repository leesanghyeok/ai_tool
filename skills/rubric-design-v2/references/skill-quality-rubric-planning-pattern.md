# Skill 품질 루브릭 설계 패턴

재사용 가능한 agent skill, 절차 playbook, 절차 기억을 평가하는 루브릭을 설계할 때 이 참고 문서를 사용한다.

## 목적

skill 품질 루브릭은 문서가 그럴듯한지가 아니라, 실제로 다음 agent 행동을 개선하는지를 평가해야 한다. 보상해야 할 요소는 명확한 사용 조건, 실행 가능한 절차, 승인 경계, 검증 규율, 실패 복구, 재사용 가능한 구조, 낮은 모호성, 언어 적합성, 병렬화 판단, 결정론적 자동화 분리다.

기존 skill repository, source family, local skill collection을 gold standard로 취급하지 않는다. 유명 repository나 자주 쓰는 local 예시는 보정 샘플일 뿐이며, 평판이나 문체가 아니라 절차의 명시성과 신뢰성을 채점한다.

## 권장 산출물 분리

재사용 루브릭은 하나의 과적재 문서보다 분리된 산출물로 관리한다.

```text
rubric/skill/
  skill-quality-rubric-plan.md
  skill-quality-rubric-v1.md
  judge_prompt.md
  score_schema.json
  보정/
    README.md
  _backup/
    YYYYMMDDTHHMMSSZ/
      ...previous 산출물s...
```

큰 rewrite 전에는 현재 산출물를 `_backup/<UTC timestamp>/` 아래에 백업한다. 백업은 canonical rubric path 밖에 둔다.

## 권장 canonical rubric 형식

사용자가 `llm-wiki-quality-rubric-v1.md` 같은 기존 rubric format을 기준으로 제시하면 범용 `rubric-design` 템플릿보다 해당 구조를 보존한다. skill 품질 루브릭의 권장 형태는 다음과 같다.

```text
# Agent Skill 품질 루브릭 v1

## 1. 평가 목적
## 2. 평가 대상
## 3. 통과 기준
## 4. 차원 요약
## 5. 세부 채점 기준
## 6. 전역 상한 및 인증 규칙
## 7. 점수 해석
## 8. 채점 절차
## 9. 판정 실행 모드
## 10. 판정자 지침
## 11. JSON 점수카드 Schema
## 12. 보정 노트
```

형식 규칙:

- `D1`, `D2` 같은 차원 ID를 사용한다.
- 차원 요약에는 `Gate Type` 열을 포함한다.
- 각 체크리스트 table에는 `결정론적?` 열을 포함한다.
- 하드 게이트 차원와 품질 차원를 분리한다.
- 각 차원에는 지역 상한을 둔다.
- 체크리스트 scoring 이후 적용되는 전역 상한과 certification rule을 포함한다.
- inline JSON 점수카드 schema는 standalone `score_schema.json`과 일치해야 한다.

## 권장 차원 세트

사용자가 다른 척도를 요구하지 않으면 100점을 사용한다.

| ID | 차원 | 점수 | Gate Type | 평가 초점 |
|---|---:|---:|---|---|
| D1 | 사용 조건과 범위 정밀도 | 15 | Hard gate | 언제 skill을 로드하고 어디서 멈출지 |
| D2 | 운영 절차 명시성 | 20 | Hard gate | 암시가 아닌 실행 가능한 단계 |
| D3 | 안전, 승인, 경계 정합성 | 15 | Hard gate | 승인 경계, risk handling, 사용자 운영 선호 |
| D4 | 검증과 근거 규율 | 15 | Hard gate | 완료 주장 전 실제 output 검증 |
| D5 | 재사용성, 범용성, 언어 적합성 | 10 | Hard gate | 한국어 우선, 범용-agent 적합성, 제품 과종속 방지 |
| D6 | 실패 처리와 복구 | 10 | Quality | 오류 보고, likely cause, impact, recovery path |
| D7 | 구조, 일관성, 인지 부담 | 8 | Quality | 모순 없는 decision flow와 쉬운 탐색 |
| D8 | 병렬화, 컨텍스트 관리, 결정론적 자동화 | 7 | Quality | 병렬 작업 판단, context control, 결정론적 scripting |

권장 통과 모델:

- Baseline passing score: `90 / 100`.
- Hard gate threshold: D1 >= 13, D2 >= 17, D3 >= 13, D4 >= 13, D5 >= 8.
- 하드 게이트 중 하나라도 실패하면 raw total이 90 이상이어도 `pass = false`이고 certification score는 89로 cap한다.

## 고려할 hard rule

사용자의 skill library가 한국어 우선이거나 한국어 운영자를 위한 것이라면 언어와 범용성 규칙을 명시한다.

- task가 다른 언어를 명시적으로 요구하지 않았는데 skill이 한국어 우선이 아니면 score cap을 둔다. machine identifier, command, path, API name, schema key, proper noun은 필요할 때 원문을 유지한다.
- 범용 절차여야 하는데 특정 product name, agent brand, local runtime에 불필요하게 묶이면 재사용성에서 cap 또는 penalty를 적용한다. platform-specific skill은 platform 이름을 쓸 수 있지만, 일반 절차와 platform-specific implementation을 분리해야 한다.
- core 절차가 암시적이고 evaluator가 절차를 추론해야 하면 문장가 좋아 보여도 cap을 적용한다.
- large-context 작업을 다루면서 subagent, 병렬 review, fixed intermediate 산출물 전략이 없으면 context-management 약점으로 cap을 적용한다.
- 결정론적 repeated processing을 agent reasoning에 맡기면 cap 또는 penalty를 적용한다. parsing, counting, normalization, schema validation, bounds check, aggregation은 script/checker로 처리해야 한다.
- 단계마다 one-off script를 만들고 재사용 가능한 common script/checker를 만들지 않으면 자동화 design을 감점한다.

## 병렬화와 결정론적 자동화

Subagent와 병렬ism은 두 가지 이유로 유용하다.

1. context contamination을 줄이고 shard reasoning을 깨끗하게 유지한다.
2. 독립 task를 동시에 처리해 wall-clock time을 줄인다.

좋은 skill은 다음을 구분하도록 agent를 안내해야 한다.

- 순차 의존: step B가 step A output을 필요로 한다.
- 병렬 가능 작업: independent files, 차원s, logs, 샘플s, candidate evaluations는 동시에 처리할 수 있다.
- 결정론적 작업: parse, count, normalize, hash, validate schema, check bounds, aggregate JSON. 재사용 가능한 script/checker를 우선한다.
- 비결정론적 작업: judgment, synthesis, prioritization, tradeoff assessment. bounded evidence packet으로 clean agent reasoning을 사용한다.

작은 단계마다 새 ad-hoc script를 만들지 않는다. 여러 샘플이나 run에 적용되는 재사용 가능한 script/checker를 선호한다.

## 깨끗한 병렬 판정 절차

루브릭을 LLM judge가 적용할 예정이면 다음 절차를 따른다.

1. Parent가 self-contained evaluation packet을 만든다: target skill, included files, rubric, 결정론적 checker output, cap rules, JSON schema.
2. Judge는 기본적으로 `clean_subagent`에서 실행한다.
3. multi-차원, long, high-stakes 평가는 `병렬_clean_subagents`를 사용하고 차원/체크리스트 group 단위로 shard한다.
4. Shard judge는 배정된 shard만 채점하고 final total을 계산하지 않는다.
5. Parent가 JSON parse, score bounds, missing/duplicate criteria, evidence grounding, contradiction, 지역 상한, 전역 상한을 중앙에서 검증한다.
6. `same_context_exception`은 low-stakes quick check 또는 clean subagent unavailable일 때만 사용하고 contamination risk를 기록한다.

## JSON 점수카드 기대 형식

점수카드는 llm-wiki rubric style과 비슷한 형태를 사용하고 최소한 다음 key를 포함한다.

- `skill_path`
- `evaluated_at`
- `read_only`
- `rubric_version`
- `judging_context`
- `context_contamination_notes`
- `baseline_passing_score`
- `raw_total_score`
- `certification_score`
- `max_score`
- `pass`
- `grade`
- `hard_gates`
- `global_caps_applied`
- `차원_scores`
- `counts`
- `issues`
- `unverified`
- `next_actions`

## 보정 패턴

루브릭을 고정하기 전 실제 skill을 샘플로 사용한다.

1. agent 행동을 실제로 개선한 강한 skill.
2. 평균적이지만 사용할 수 있는 skill.
3. 유창하고 길지만 실행 세부가 약한 skill.
4. approval 또는 verification boundary가 빠진 skill.
5. 너무 넓거나 너무 좁거나 session-specific한 skill.
6. 범용 절차여야 하는데 특정 product/agent name에 과하게 묶인 skill.
7. large-context 작업인데 subagent/병렬ization 또는 intermediate-산출물 전략이 없는 skill.
8. 결정론적 processing과 non결정론적 reasoning을 분리하지 못한 skill.
9. common 재사용 가능한 checker 대신 per-step one-off script를 만드는 skill.

강한 skill이 올바른 이유로 높은 점수를 받는지, 장황하지만 non-operational한 skill이 cap으로 잡히는지 확인한다. 약한 예시가 너무 높게 나오면 weight보다 cap을 먼저 조정한다. judge variance가 대략 5–8점을 넘으면 주관적 기준을 더 관찰 가능한 체크리스트 item으로 쪼갠다. 샘플 source family가 암묵적 gold standard가 되지 않는지도 확인한다.

## 보고 선호

사용자가 plan을 먼저 요구하면 간결한 plan을 내고 승인 전에는 파일을 쓰지 않는다. non-destructive scoped file creation 또는 rewrite가 승인되면 기존 산출물를 백업하고 canonical file을 작성한 뒤 file read-back과 JSON parse validation으로 검증한다.

## origin/main 병합 보강

계획 단계에서 다음 항목을 빠뜨리지 않는다.

- 병렬화 평가는 context hygiene뿐 아니라 독립 shard 병렬 실행으로 wall-clock time을 줄일 수 있는지도 본다.
- 독립 shard는 병렬, 의존 단계는 순차라는 기준을 명시한다.
- 결정론적 work는 LLM judgment에 맡기지 않고 재사용 가능한 script/checker로 처리한다.
- Per-step one-off script 남발은 감점 또는 cap 사유로 둔다.
- 보정 샘플에는 병렬화 기회를 놓친 skill과 결정론적/non결정론적 처리를 혼동한 skill을 포함한다.
