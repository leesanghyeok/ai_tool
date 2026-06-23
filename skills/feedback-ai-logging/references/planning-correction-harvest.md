# 계획 교정 피드백 수확 노트

이 reference는 `feedback-ai-logging`을 현재 세션에서 사용할 때 큰 실패뿐 아니라 반복 가능한 작은 planning correction도 raw feedback incident로 남기기 위한 보조 기준이다.

## 추가로 잡아야 하는 사건 유형

### 참고 자료를 직접 의존성으로 오독한 경우

사용자가 어떤 skill, 문서, 과거 사례, 패턴을 “참고”하라고 했는데 agent가 이를 직접 호출, 필수 의존성, 본문 명시, 실행 단계로 바꾸어 계획한 경우다.

예시 evidence:

```text
User: “/rublic_creating_expert 알지?? 어떤 패턴인지 같은 패턴으로 할거야”
Later correction: “직접 호출하는건 아니야. 계획할때 세부내용을 참고하라고 적은거야.”
```

분류 권장:

- task_type: `planning`
- severity: `medium`
- categories: [`context-misread`, `requirement-miss`, `specificity`]

후보 규칙:

> 사용자가 “참고” 또는 “같은 패턴”이라고 말하면, 직접 의존성으로 명시할지 여부를 별도로 확인하고 명시 요청 없이는 패턴만 추상화해 반영한다.

### 기본값과 변수화 경계를 누락한 경우

반복 workflow, skill, config, automation 설계에서 기본값 또는 변수화 경계가 빠져 사용자가 정정한 경우다.

예시 evidence:

```text
User: “평균 점수 90 점은 변수로 빼자. 기본값 90 점.”
User: “기본 질문값은 10개로 하자.”
```

분류 권장:

- task_type: `planning`
- severity: `low` 또는 `medium`
- categories: [`requirement-miss`, `decision-criteria`, `specificity`]

후보 규칙:

> 반복 workflow를 계획할 때 종료조건, 질문 수, max iterations, batch size처럼 실행마다 달라질 수 있는 값은 변수로 분리하고 기본값을 명시한다.

## 수확 판단 기준

다음 조건을 모두 만족하면 low/medium incident로 기록한다.

- 사용자의 기대 동작과 agent의 실제 계획/출력이 구체적으로 다르다.
- 사용자가 정정 또는 불만족 신호를 냈다.
- 재발 방지 가능한 후보 규칙으로 만들 수 있다.
- 단순 취향 변경이나 새 기능 추가가 아니다.

## 주의사항

“작은 수정이라 로그로 남길 정도는 아니다”라고 판단하지 않는다. Skill, automation, rubric, workflow 설계에서 작은 default/variable/reference 오독은 다음 세션에 같은 잘못된 규칙으로 굳어질 수 있다.
