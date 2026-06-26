# Trigger examples and history rules

## 목적

고도화된 반복 평가 시스템 없이도 스킬 생성과 개선의 판단 근거가 나중에 추적되도록 한다. 이 문서는 trigger 예시와 lightweight history 기록 규칙을 정의한다.

## Trigger examples

새 스킬 또는 trigger 변경이 있는 스킬은 가능하면 다음 예시를 남긴다.

```yaml
should_trigger:
  - "현실적인 사용자 요청 1"
  - "현실적인 사용자 요청 2"
  - "현실적인 사용자 요청 3"
should_not_trigger:
  - "키워드는 비슷하지만 다른 작업인 near-miss 요청 1"
  - "키워드는 비슷하지만 다른 작업인 near-miss 요청 2"
  - "키워드는 비슷하지만 다른 작업인 near-miss 요청 3"
```

규칙:

- 예시는 실제 사용자가 말할 법한 문장으로 쓴다.
- `should_not_trigger`는 명백히 무관한 문장이 아니라 near-miss로 만든다.
- 과소 trigger와 과잉 trigger를 모두 줄이는 것이 목적이다.
- 실행형 평가나 반복 점수화는 기본 범위가 아니다.

## History record

작업 이력은 `history/YYYYMMDD-<short-topic>.md` 같은 파일로 남길 수 있다.

권장 형식:

```markdown
# <작업 제목>

- 날짜: YYYY-MM-DD
- 대상 스킬: <skill-name>
- 목표: <한 문장>
- 승인 범위: <사용자가 승인한 범위>

## 변경 요약

- ...

## Trigger examples

### should_trigger

- ...

### should_not_trigger

- ...

## 검증

- ...

## 남은 문제

- ...
```

## 원칙

- history는 사람이 추적하는 기록이지 고도화된 평가 시스템이 아니다.
- 오래 유지될 판단 기준은 history가 아니라 `SKILL.md` 또는 `references/`로 승격한다.
- 반복 실행 가능한 검증은 history에 붙여두지 말고 `scripts/`로 분리한다.
