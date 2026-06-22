# Skill Quality Rubric Calibration

## 목적

이 디렉터리는 `/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md`의 calibration 결과를 보관하기 위한 공간이다.

canonical rubric과 calibration result를 분리한다.

- Canonical rubric: 평가 기준, 배점, cap, judge instruction.
- Calibration artifacts: 샘플 skill, judge output, human preference comparison, tuning notes.

## 초기 샘플 구성 계획

최소 샘플 세트:

1. 매우 좋은 스킬 2개.
2. 평균적인 스킬 2개.
3. 그럴듯하지만 실행성 낮은 스킬 2개.
4. 위험 경계가 빠진 스킬 1개.
5. 너무 장황하거나 추상적인 스킬 1개.

레퍼런스 후보:

- gstack 계열 skill: 실행성/operational workflow 기준.
- superpower 계열 skill: agent behavior-shaping 기준.
- mattpocock 계열 skill: concise, practical, coding-workflow 기준.
- 현재 Hermes local skills: 실제 사용성/사용자 취향 적합성 기준.

## 권장 artifact 구조

```text
calibration/
  README.md
  samples.jsonl
  runs/
    YYYYMMDD-HHMM/
      scorecards.jsonl
      summary.md
      notes.md
```

`samples.jsonl` 권장 필드:

```json
{
  "sample_id": "string",
  "skill_path": "string",
  "source_family": "hermes | gstack | superpower | mattpocock | other",
  "expected_quality_band": "excellent | good | adequate | weak | poor | unknown",
  "selection_reason": "string",
  "notes": "string"
}
```

`scorecards.jsonl`은 `/Users/stark/project/jarvis/ai_tool/rubric/skill/score_schema.json`를 따른다.

## Calibration 질문

- 좋은 스킬이 높은 점수를 받는가?
- 장황하지만 실행성 낮은 스킬이 과점되지 않는가?
- approval/verification 누락이 cap으로 잡히는가?
- 사용자 취향과 맞지 않는 스킬이 적절히 감점되는가?
- judge 간 점수 차이가 5–8점 안에 들어오는가?
- global cap이 너무 자주 또는 너무 드물게 적용되지 않는가?
- high score skill을 실제 task replay에 사용했을 때 agent 행동이 개선되는가?

## Tuning 원칙

- weak sample이 과점되면 weight보다 cap을 먼저 조정한다.
- judge 간 variance가 크면 checklist recognition standard를 더 observable하게 쪼갠다.
- 좋은 sample이 낮게 나오면 해당 sample의 실제 장점이 rubric 목적과 맞는지 먼저 확인한다.
- calibration example을 canonical rule 본문에 직접 섞지 않는다.
- v1을 수정하면 rubric version을 올리고 이전 run 결과와 비교한다.
