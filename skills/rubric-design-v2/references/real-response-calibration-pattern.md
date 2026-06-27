# 실제 응답 기반 보정 패턴

## 목적

루브릭 초안을 실제 agent 또는 model 응답에 적용해 점수 기준이 현실적으로 작동하는지 확인한다. hand-written placeholder가 아니라 fresh response를 사용해 criterion의 모호함, 과한 관대함, 누락된 cap을 찾는다.

## 입력

- 평가할 prompt 또는 task.
- 강한 응답, 보통 응답, 약한 응답, 유창하지만 틀린 응답.
- 사용할 rubric과 scorecard schema.
- 허용 evidence bundle과 제외 context.

## 절차

1. sample response를 만들거나 수집한다.
2. 각 response를 clean judge 또는 parallel clean subagents로 채점한다.
3. checklist item별 evidence와 missing point를 확인한다.
4. 사람이 기대한 순위와 실제 점수 순위를 비교한다.
5. 약한 response가 높게 나오면 cap과 evidence criterion을 강화한다.
6. 강한 response가 낮게 나오면 과도하게 좁은 criterion을 조정한다.
7. 보정 결과는 canonical rubric이 아니라 별도 calibration artifact로 저장한다.

## 검증

- JSON scorecard가 parse된다.
- dimension sum과 total score가 일치한다.
- local cap과 global cap 적용 순서가 명확하다.
- sample source가 gold standard로 굳어지지 않는다.
