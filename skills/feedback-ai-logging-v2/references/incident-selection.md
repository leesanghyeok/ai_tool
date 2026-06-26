# 사건 선정 기준 (Incident selection)

## 기록할 사건 조건

새 feedback log를 만들 후보는 다음을 모두 만족해야 한다.

- 사용자가 기대한 동작이 구체적으로 식별된다.
- agent 또는 AI가 실제로 한 동작이 식별된다.
- 기대와 실제의 차이가 명확하다.
- 현재 source에서 짧게 인용하거나 요약할 수 있는 evidence가 있다.
- 재발 방지 가능한 candidate rule 또는 checklist item으로 바꿀 수 있다.

## 포함할 수 있는 가벼운 planning correction

- 기본값을 빠뜨려 사용자가 추가한 경우.
- 변수화해야 할 값을 고정값으로 둔 경우.
- 참고 자료를 직접 의존성이나 실행 단계로 오독한 경우.
- skill, automation, rubric, workflow의 추상화 수준을 잘못 잡은 경우.

## 제외할 것

- 단순 새 요구사항 추가.
- 정상적인 범위 조정.
- 불만족이나 수정 의도가 없는 일반 질의응답.
- evidence가 부족한 추정 사건.
- 이미 같은 session/source에서 같은 expected/actual/rule로 기록된 사건.
