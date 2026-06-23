# 깨끗한 병렬 Judge 실행

## 적용 시점

rubric이 LLM judge에 의해 적용될 때, 특히 multi-dimension, 장문, high-stakes 또는 반복 평가에 이 참고 문서를 사용한다.

## 문제

judge가 현재 대화를 계속 이어가면, 이전 context 때문에 score가 오염될 수 있다:

- 평가 대상 출력에 없는 이전 user intent 또는 correction
- agent memory 또는 session history
- implementation note 또는 plan
- evaluation packet의 일부가 아닌 대화상의 assumption

이로 인해 score의 재현성이 낮아지고, 실제 평가 artifact에 존재하지 않는 content가 보상받을 수 있다.

## 기본 패턴

1. self-contained evaluation packet을 만든다:
   - evaluation target
   - evaluated output
   - rubric document
   - 허용된 source/evidence bundle이 있다면 포함
   - cap 및 penalty rule
   - JSON output schema
2. 깨끗한 새 subagent/session에서 judging을 실행한다.
3. judge에게 모든 prior conversation, memory, unstated assumption을 무시하라고 지시한다.
4. rubric에 여러 dimension이 있으면 rubric을 dimension/checklist shard로 나눈다.
5. shard judge를 병렬 clean subagent에서 실행한다.
6. 각 shard judge는 자신에게 배정된 shard JSON만 반환하게 한다.
7. parent agent는 모든 shard JSON을 validate하고, score bounds와 누락/중복 criteria를 확인하며, contradiction을 조정하고, global cap을 중앙에서 적용한다.

## Parent 집계 검증

- 모든 dimension/checklist item이 정확히 한 번씩 존재한다.
- 모든 score가 `0..max_score` 범위 안에 있다.
- evidence는 외부 context가 아니라 evaluation packet에서 quote 또는 summarize된다.
- local cap은 global cap보다 먼저 적용된다.
- global cap은 모든 shard score가 merge된 뒤 중앙에서 한 번만 적용된다.
- 최종 결과에는 `judging_context`와 context contamination note가 포함된다.

## Same-context 예외

same-context judging은 low-stakes quick check이거나 clean subagent를 사용할 수 없을 때에만 허용된다. scorecard에는 이를 명시적으로 라벨링해야 한다. 예:

```json
{
  "judging_context": "same_context_exception",
  "context_contamination_notes": "Low-stakes quick check; no external evidence beyond the provided output was used."
}
```

## 한국어 우선 rubric 문서

한국어 사용자 요청 또는 Korean-first domain의 경우, 사람이 읽는 rubric prose는 Korean-first여야 한다. JSON key, file path, command, API name, enum value, schema field, proper noun 같은 machine identifier는 원래 언어로 유지해도 된다.
