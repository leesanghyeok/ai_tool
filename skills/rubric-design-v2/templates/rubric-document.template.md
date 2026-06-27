# {rubric_name} 평가 루브릭

## 1. 평가 목적

{evaluation_goal}

## 2. 평가 대상과 허용 근거

- 평가 대상: {evaluation_target}
- 허용 근거: {allowed_evidence}
- 제외 context: {excluded_context}

## 3. 총점과 차원 요약

총점: {max_score}

| 차원 | 배점 | 평가 초점 |
|---|---:|---|
| {dimension_1} | {points} | {focus} |
| **합계** | **{max_score}** | |

## 4. 세부 채점 기준

### 4.1 {dimension_1} — {points}점

| 체크리스트 기준 | 배점 | 인정 근거 |
|---|---:|---|
| {criterion_1} | {points} | {observable_evidence} |

지역 상한/감점:
- {local_cap_or_penalty}

## 5. 전역 상한 및 감점 규칙

- {global_cap_rule}

## 6. 채점 절차

1. evaluation packet의 범위와 허용 근거를 확인한다.
2. checklist item을 먼저 채점한다.
3. local cap과 penalty를 적용한다.
4. global cap을 적용한다.
5. scorecard JSON과 사람이 읽는 요약을 생성한다.

## 7. 판정자 프롬프트

```text
{judge_prompt}
```

## 8. JSON scorecard schema

```json
{scorecard_schema}
```
