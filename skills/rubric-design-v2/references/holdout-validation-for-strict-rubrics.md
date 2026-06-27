# 엄격한 루브릭의 holdout 검증

## 목적

엄격화된 루브릭이 calibration sample에 과적합했는지 확인한다. 새로운 질문과 fresh output을 사용해 criterion이 일반화되는지 검증한다.

## 절차

1. 기존 calibration sample과 겹치지 않는 holdout prompt를 만든다.
2. fresh answer를 생성하거나 수집한다.
3. judge는 holdout answer의 기대 점수나 작성 의도를 모르는 상태로 채점한다.
4. parent가 score bounds, missing criterion, duplicate criterion, cap consistency를 검증한다.
5. calibration set과 holdout set의 score pattern을 비교한다.
6. holdout에서 강한 답변이 과도하게 낮거나 약한 답변이 높으면 criterion을 재검토한다.

## 통과 기준

- holdout에서도 강한/보통/약한 output 순위가 유지된다.
- global cap이 예상 가능한 실패에만 적용된다.
- judge variance가 허용 범위에 들어온다.

## 보고

- holdout prompt 수.
- score distribution.
- cap application.
- overfit 의심 criterion.
- 수정 필요 여부.
