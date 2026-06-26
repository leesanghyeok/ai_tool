# feedback-ai-logging-v2 skill-creator-for-stark 업데이트 반영

## 날짜

2026-06-27

## mode

modify

## 목표

`skill-creator-for-stark` v1.3.0 기준을 `feedback-ai-logging-v2`에 반영한다.

## 주요 변경

- trigger 판단을 `사용 판단` 한 섹션으로 통합하고 별도 `Trigger Examples` 중복 섹션을 제거했다.
- `Hard Gates`에서 `Metadata gate`, `Body size gate` 같은 package-authoring 규칙을 제거하고 raw feedback domain gate만 남겼다.
- feedback log skeleton을 `templates/feedback-log.template.md`로 분리하고, `references/file-format.md`는 field 의미와 hash 기준 설명으로 정리했다.
- `scripts/validate-feedback-log.py`가 global `raw/feedback`과 skill-local `feedback/` path를 모두 검증할 수 있게 확장했다.
- skill-local dissatisfaction logging 절차를 workflow와 checklist에 추가했다.

## trigger 예시

- should_trigger: “방금 답변이 요구사항을 빼먹었으니까 이 실패를 기록해.”
- should_trigger: “이 스킬 사용 경험을 해당 스킬 feedback/에 남겨줘.”
- should_not_trigger: “이 답변을 더 짧게 다시 써줘.”
- should_not_trigger: “이 반복 패턴으로 rubric을 바로 업데이트해.”

## 검증 기록

최종 검증 결과는 작업 완료 보고의 `OUTPUT_VERIFICATION_RESULT`를 기준으로 한다.
