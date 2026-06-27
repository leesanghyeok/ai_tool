# 엄격도 반복 보정 패턴

## 목적

루브릭이 너무 관대하거나 목표 평균 점수보다 높게 나올 때, checklist와 cap을 반복적으로 조정해 원하는 엄격도에 맞춘다. 목표는 특정 sample에 과적합하는 것이 아니라, 강한 답변은 높은 점수를 유지하고 약한 답변은 명확히 낮아지도록 판정 기준을 좁히는 것이다.

## 사용 조건

- 같은 sample family에서 점수가 전반적으로 높게 나온다.
- 유창하지만 근거가 약한 답변이 high score를 받는다.
- 사용자가 평균 점수, 통과율, target strictness를 지정했다.
- judge 간 점수 차이가 5–8점을 넘는다.

## 절차

1. 현재 score distribution을 기록한다.
2. 높은 점수를 받은 약한 sample의 공통 원인을 찾는다.
3. weight를 먼저 바꾸지 말고 local/global cap을 먼저 검토한다.
4. 관찰 불가능한 criterion을 더 작은 checklist item으로 쪼갠다.
5. 변경 후 같은 sample family를 다시 채점한다.
6. 목표 평균, rank order, cap trigger가 모두 맞는지 확인한다.
7. calibration result는 canonical rubric과 분리해 `calibration/` 또는 history에 둔다.

## 중단 기준

- 강한 sample과 약한 sample의 순위가 안정된다.
- judge variance가 5–8점 안에 들어온다.
- 같은 issue를 더 세분화해도 점수 변화가 거의 없다.

## 주의사항

- 특정 sample 하나에 맞춰 criterion을 만들지 않는다.
- 긴 답변이나 jargon을 품질로 보상하지 않는다.
- raw score와 cap 적용 후 certification score를 분리해 보고한다.
