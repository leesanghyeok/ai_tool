# feedback-ai-logging-v2 생성 기록

- 날짜: 2026-06-26
- 대상 스킬: feedback-ai-logging-v2
- 목표: feedback-ai-logging을 required/optional/default 변수 체계와 명확한 환경 요구사항을 갖춘 v2 스킬로 재작성
- 승인 범위: 기존 스킬을 보존하고 새 디렉터리 `feedback-ai-logging-v2` 생성

## 변경 요약

- 입력/출력 변수를 table로 재작성하고 required/optional/default/설명을 추가했다.
- `ENV_`를 사용자 입력이 아니라 필요한 도구/권한/명령 조건으로 설명했다.
- 고급 평가 대신 raw log 생성 검증과 history 중심으로 유지했다.
- deterministic 검증은 `scripts/validate-feedback-log.py`로 분리했다.

## Trigger examples

### should_trigger

- “이번 세션에서 내가 고치라고 한 것들 raw feedback으로 남겨줘.”
- “방금 답변이 요구사항을 빼먹었으니까 이 실패를 기록해.”
- “어제 이후 대화에서 검증 안 하고 완료라고 한 사건들을 feedback log로 만들어줘.”

### should_not_trigger

- “이 답변을 더 짧게 다시 써줘.”
- “이 선호를 앞으로 기억해.”
- “이 반복 패턴으로 rubric을 바로 업데이트해.”

## 검증

- skill package validator 실행 예정.
- Python validator compile 실행 예정.
- git diff check 실행 예정.

## 남은 문제

- 실제 raw feedback log 생성 smoke test는 별도 승인된 sample incident로 수행할 수 있다.
