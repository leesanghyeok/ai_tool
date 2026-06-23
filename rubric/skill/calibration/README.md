# Agent Skill 품질 루브릭 Calibration

## 목적

이 디렉터리는 `/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md`의 calibration 결과를 보관한다.

canonical rubric과 calibration result를 분리한다.

- Canonical rubric: 평가 기준, 배점, hard gate, cap, judge instruction, JSON scorecard schema.
- Calibration artifacts: sample skill, deterministic checker output, judge output, human preference comparison, tuning notes.

## Source family 원칙

특정 repository/style/local collection은 최고의 기준이 아니라 calibration sample family다. 출처 이름값을 점수로 보상하지 않고, workflow가 명시적이고 재사용 가능하며 검증 가능한지만 본다.

## 초기 샘플 구성 계획

최소 샘플 세트:

1. 실제로 agent 행동을 개선한 강한 skill.
2. 평균적이지만 사용 가능한 skill.
3. 길고 그럴듯하지만 실행성이 낮은 skill.
4. approval boundary 또는 verification이 빠진 skill.
5. trigger가 너무 넓거나 너무 좁은 skill.
6. 특정 제품명/에이전트명에 과하게 묶인 skill.
7. 큰 context 작업인데 parallel/subagent/intermediate artifact 전략이 없는 skill.
8. 결정론적 처리와 비결정론적 추론을 구분하지 못하는 skill.
9. 단계마다 일회성 script를 만드는 과잉 자동화 skill.

## 권장 artifact 구조

```text
calibration/
  README.md
  samples.jsonl
  runs/
    YYYYMMDD-HHMM/
      deterministic_checks.jsonl
      scorecards.jsonl
      summary.md
      notes.md
```

`samples.jsonl` 권장 필드:

```json
{
  "sample_id": "string",
  "skill_path": "string",
  "source_family": "local | external_repo | generated | other",
  "expected_quality_band": "excellent | strong_not_passing | adequate | weak | unacceptable | unknown",
  "selection_reason": "string",
  "notes": "string"
}
```

`scorecards.jsonl`은 `/Users/stark/project/jarvis/ai_tool/rubric/skill/score_schema.json`를 따른다.

## Clean/parallel judging 절차

1. parent가 sample별 evaluation packet을 만든다.
2. deterministic criteria는 가능한 한 script/checker로 먼저 계산한다.
3. 비결정론적 criteria는 clean judge 또는 parallel clean shard judge가 평가한다.
4. shard judge는 자기 dimension/checklist만 평가한다.
5. parent가 JSON parse, score bounds, missing/duplicate criteria, contradiction, local/global cap을 중앙에서 검증한다.
6. same-context judging을 사용한 경우 `same_context_exception`으로 표시하고 오염 가능성을 기록한다.

## Calibration 질문

- 강한 skill이 높은 점수를 받는가?
- verbose하지만 non-operational한 skill이 cap으로 잡히는가?
- approval/verification 누락이 hard gate에서 잡히는가?
- source family 이름값이 점수에 영향을 주지 않는가?
- 동시 처리가 가능한 task를 순차 처리하도록 만든 skill이 감점되는가?
- 결정론적 처리와 비결정론적 추론의 분리 실패가 감점되는가?
- 일회성 script 남발 대신 공통 재사용 script를 요구하는가?
- 한국어-first와 machine identifier 보존이 균형 있게 평가되는가?
- judge 간 score variance가 5–8점 안에 들어오는가?

## Tuning 원칙

- weak sample이 과점되면 weight보다 cap을 먼저 조정한다.
- judge variance가 크면 checklist recognition standard를 더 observable하게 쪼갠다.
- 결정론적 처리에는 script 검증을 요구하고, 비결정론적 판단에는 evidence-backed reasoning을 요구한다.
- script는 단계별 임시 조각보다 공통 재사용 단위로 설계되었는지 확인한다.
- calibration example을 canonical rule 본문에 직접 섞지 않는다.
- v1을 수정하면 rubric version을 올리고 이전 run 결과와 비교한다.

## origin/main 병합 보강

이번 병합에서 `origin/main`의 calibration 운영 원칙을 보존한다.

- Source family는 gold standard가 아니라 calibration sample family다. `local`, `gstack`, `superpower`, `mattpocock`, `other` 같은 분류는 이름값 보상이 아니라 분포 확인용으로만 사용한다.
- Artifact에는 `shard_scorecards.jsonl`과 `schema_validation.txt`를 포함할 수 있다.
- Clean judge는 packet, canonical rubric, score schema만 사용한다. 현재 대화, memory, 구현 노트, 작성자 self-report는 근거로 사용하지 않는다.
- 큰 package, high-stakes sample, judge variance가 큰 sample은 `parallel_clean_subagents`로 나누고 parent가 중앙에서 JSON parse, score bounds, duplicate/missing criterion, cap 적용, contradiction reconciliation을 수행한다.
- Deterministic checks(JSON parse, schema validation, bounds, cap consistency, aggregation)는 재사용 가능한 script/checker로 처리한다.
- Nondeterministic checks(evidence 해석, 우선순위 판단, 모순 해석)는 judge reasoning으로 처리하되 evidence-backed여야 한다.
- 플랫폼-specific skill은 플랫폼 고유 절차와 범용 절차를 분리했는지 평가한다.
- 병렬화 평가는 context 오염 방지만 보지 않고, 독립 작업을 병렬화해 wall-clock time을 줄일 수 있었는지도 본다.
