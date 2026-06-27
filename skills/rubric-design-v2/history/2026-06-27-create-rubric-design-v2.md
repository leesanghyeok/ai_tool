# rubric-design-v2 생성 기록

- 날짜: 2026-06-27
- mode: create
- 목표: 기존 `rubric-design`의 장문 본문을 portable skill package 구조로 재구성해 `rubric-design-v2`를 생성한다.
- 주요 변경: trigger와 workflow는 `SKILL.md`에 유지하고, 기존 심화 자료는 `references/`로 이전했으며, 산출물 골격은 `templates/`, 결정적 검사는 `scripts/`로 분리했다.
- trigger 예시: 새 루브릭 설계, 기존 루브릭 엄격화, LLM judge scorecard/schema 설계.
- feedback logging: `feedback/` raw log 정책과 `templates/feedback-log.template.md`를 포함했다.
- 남은 문제: 품질 루브릭 평가는 생성 후 clean/subagent 또는 parent 검증으로 별도 확인한다.
