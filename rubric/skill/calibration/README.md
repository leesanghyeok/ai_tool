# Skill Quality Rubric Calibration

## 목적

이 디렉터리는 `/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md`의 calibration sample, judge run, human preference comparison, tuning notes를 보관한다.

Canonical rubric과 calibration artifact는 분리한다.

- Canonical rubric: 평가 기준, 배점, cap, judge execution mode, JSON schema 요구.
- Calibration artifacts: 샘플 skill, clean/parallel judge output, human preference comparison, tuning notes, schema validation 결과.

## 핵심 원칙

1. 특정 repository, source family, local collection은 최고의 기준이 아니라 calibration sample family다.
2. 출처 이름값, 유명한 작성자, 로컬에서 자주 쓰였다는 이유를 점수로 보상하지 않는다.
3. skill이 명시적이고 재사용 가능하며 검증 가능한 workflow를 제공하는지만 본다.
4. human-facing prose는 한국어-first 원칙을 따른다. JSON key, enum, path, command, API name 같은 machine identifier는 영어 유지가 가능하다.
5. 좋은 skill은 workflow가 암시적으로 숨지 않고 직관적이고 명시적으로 작동해야 한다.
6. 모순/모호함, 불필요한 제품명/에이전트명 종속, verification/approval 누락은 calibration에서 반드시 잡혀야 한다.
7. 플랫폼-specific skill은 해당 플랫폼명을 쓸 수 있지만, 범용 절차와 플랫폼 고유 절차를 분리했는지 확인한다.

## 권장 artifact 구조

```text
calibration/
  README.md
  samples.jsonl
  runs/
    YYYYMMDD-HHMM/
      scorecards.jsonl
      shard_scorecards.jsonl
      schema_validation.txt
      summary.md
      notes.md
```

`samples.jsonl` 권장 필드:

```json
{
  "sample_id": "string",
  "skill_path": "string",
  "source_family": "local | gstack | superpower | mattpocock | other",
  "expected_quality_band": "excellent | good | adequate | weak | poor | unknown",
  "selection_reason": "string",
  "deterministic_features_to_check": ["json_parse", "aggregation", "normalization", "schema_validation"],
  "nondeterministic_features_to_check": ["judgment", "interpretation", "prioritization"],
  "notes": "string"
}
```

`scorecards.jsonl`은 `/Users/stark/project/jarvis/ai_tool/rubric/skill/score_schema.json`를 따른다.

## 초기 샘플 구성 계획

최소 샘플 세트:

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
11. 한국어-first 원칙을 위반하거나 human-facing prose가 외국어 중심인 스킬 1개.
12. 플랫폼-specific 절차와 범용 절차가 잘 분리된 스킬 1개.

레퍼런스 후보 source family:

- gstack 계열 skill: 실행성/operational workflow sample.
- superpower 계열 skill: agent behavior-shaping sample.
- mattpocock 계열 skill: concise, practical, coding-workflow sample.
- 현재 local skills: 실제 사용성/사용자 취향 적합성 sample.
- other: 위 family에 속하지 않는 비교 sample.

위 family는 모두 sample family일 뿐이며 gold standard가 아니다.

## Clean / Parallel Judging 절차

기본 calibration run은 `clean_subagent`로 수행한다.

1. parent가 각 sample에 대해 평가 packet을 만든다.
2. clean judge는 packet, canonical rubric, score schema만 사용한다.
3. clean judge는 현재 대화, memory, implementation notes, 작성자 self-report를 사용하지 않는다.
4. 결과는 `score_schema.json`에 맞는 JSON으로 저장한다.
5. parent는 JSON parse와 schema validation을 deterministic step으로 수행한다.

Multi-dimension, high-stakes, 큰 package, judge variance가 큰 sample은 `parallel_clean_subagents`로 재평가한다.

1. parent가 dimension/checklist shard를 나눈다.
2. shard judge는 배정된 shard만 평가하고 최종 총점을 확정하지 않는다.
3. shard output은 parseable fragment로 저장한다.
4. parent가 중앙에서 JSON parse, score bounds, missing/duplicate criteria, contradiction reconciliation, local/global cap application을 수행한다.
5. parent는 deterministic aggregation/schema validation을 재사용 가능한 스크립트로 처리한다.
6. parent는 shard 간 판단 차이와 reconciliation 이유를 `summary.md`에 남긴다.

`same_context_exception`은 calibration 표준 모드가 아니다. 불가피하게 사용할 경우 결과를 운영 기준으로 확정하지 말고, 나중에 clean 또는 parallel clean 재평가 대상으로 표시한다.

## Deterministic vs Nondeterministic Calibration

Calibration은 deterministic 부분과 nondeterministic 부분을 분리해 확인한다.

Deterministic checks:

- JSON parse 성공 여부.
- `score_schema.json` validation 성공 여부.
- dimension score bounds와 max score 합계 확인.
- required field 누락 여부.
- duplicate/missing criterion 탐지.
- global cap 적용 후 `total_score`가 cap 이하인지 확인.
- 여러 judge output의 score aggregation, variance 계산.

Nondeterministic checks:

- evidence가 실제 skill 문구와 맞는지 판단.
- 모순/모호함 해석이 타당한지 판단.
- recommended patches가 우선순위와 영향도를 잘 반영하는지 판단.
- source family 이름값을 배제했는지 판단.
- 플랫폼-specific 절차와 범용 절차의 분리를 제대로 평가했는지 판단.

각 단계마다 일회성 스크립트를 만들지 않는다. JSONL load, schema validation, score aggregation, cap consistency check, variance summary를 여러 run과 sample에 반복 적용할 수 있는 공통 스크립트로 설계한다.

## Calibration 질문

- 좋은 스킬이 높은 점수를 받는가?
- 장황하지만 실행성 낮은 스킬이 과점되지 않는가?
- approval/verification 누락이 cap으로 잡히는가?
- 사용자 취향과 맞지 않는 스킬이 적절히 감점되는가?
- 모순/모호함이 있는 skill이 구조 점수와 cap에서 잡히는가?
- 한국어-first hard rule이 실제로 적용되는가?
- 특정 제품명/에이전트명에 과하게 묶인 skill이 범용성 감점을 받는가?
- 플랫폼-specific skill에서 범용 절차와 플랫폼 고유 절차의 분리 여부가 평가되는가?
- 서브에이전트/병렬 workflow가 필요한 작업에서 해당 지침 누락이 감점되는가?
- 동시 처리가 가능한 작업을 순차 처리하도록 만든 skill이 감점되는가?
- 결정론적 처리와 비결정론적 추론의 분리 실패가 감점되는가?
- 일회성 스크립트 남발 대신 공통 재사용 스크립트를 요구하는가?
- clean judge 간 점수 차이가 5–8점 안에 들어오는가?
- parallel clean shard 결과를 parent가 중앙에서 일관되게 reconcile하는가?
- global cap이 너무 자주 또는 너무 드물게 적용되지 않는가?
- high score skill을 실제 task replay에 사용했을 때 agent 행동이 개선되는가?

## Tuning 원칙

- weak sample이 과점되면 weight보다 cap을 먼저 조정한다.
- 병렬화 기준은 컨텍스트 오염 방지만 보지 말고, 동시 처리가 가능한 작업의 속도 개선 여부도 함께 본다.
- 결정론적 처리에는 스크립트 검증을 요구하고, 비결정론적 판단에는 evidence-backed reasoning을 요구한다.
- 스크립트는 단계별 임시 조각보다 공통 재사용 단위로 설계되었는지 확인한다.
- judge 간 variance가 크면 checklist recognition standard를 더 observable하게 쪼갠다.
- 좋은 sample이 낮게 나오면 해당 sample의 실제 장점이 rubric 목적과 맞는지 먼저 확인한다.
- calibration example을 canonical rule 본문에 직접 섞지 않는다.
- v1을 수정하면 rubric version을 올리고 이전 run 결과와 비교한다.
