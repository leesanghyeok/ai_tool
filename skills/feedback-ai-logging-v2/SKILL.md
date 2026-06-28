---
name: feedback-ai-logging-v2
description: AI 또는 agent 출력·workflow 불만족 사건을 raw feedback Markdown으로 남겨야 할 때 사용합니다. 현재/과거 세션, transcript, 파일에서 기대와 실제 차이, 근거, 후보 규칙을 사건 단위로 기록하고 중복·hash·path 검증을 수행합니다.
version: 2.4.0
author: Agent
license: MIT
metadata:
  tags: [feedback, quality, logging, raw-data]
  related_skills: [llm-wiki, rubric-design, skill-creator-for-stark]
---

# AI 피드백 로깅 v2

## 개요

AI 또는 agent의 답변·작업 흐름에서 생긴 불만족, 정정, 재작업 사건을 나중에 분석 가능한 raw Markdown 로그로 남기는 스킬이다.

핵심 원칙:

- 사건 하나는 파일 하나로 기록한다.
- raw log에는 처리 상태, 승격 여부, TODO 진행 상황을 쓰지 않는다.
- 기대 동작, 실제 동작, 차이, 근거, 후보 Agent 규칙이 확인될 때만 기록한다.
- global feedback은 `raw/feedback/YYYY-MM-DD/`에 저장한다.
- 스킬 사용 불만족은 해당 스킬의 `feedback/YYYY-MM-DD/`에 저장한다.
- 처리 여부가 필요하면 raw log를 수정하지 않고 processing ledger를 사용한다.

관련 파일:

- 로그 형식: `references/file-format.md`
- 사건 선정 기준: `references/incident-selection.md`
- 출력 경로 기준: `references/output-routing.md`
- 파일 템플릿: `templates/feedback-log.template.md`
- validator: `scripts/validate-feedback-log.py`
- eval pipeline: `scripts/run_pipeline.py`
- eval runner: `scripts/run_evals.py`

## 언제 사용하는지

사용한다:

- 사용자가 “이 실패 기록해”, “feedback으로 남겨”, “이번 세션에서 불만족했던 것 정리해”처럼 기록을 요청할 때.
- 날짜 범위, session id, thread, transcript, file에서 feedback 사건을 수확하라고 할 때.
- 답변 요구사항 누락, 검증 누락, 포맷 불일치, 맥락 오독, evidence gap을 재발 방지 데이터로 남길 때.
- 특정 스킬 사용 중 발생한 불만족을 그 스킬의 `feedback/` 아래에 남기라고 할 때.

사용하지 않는다:

- 단순히 답변을 다시 쓰거나 짧게 고치라는 요청일 때.
- 사용자가 감정을 표현했지만 기록 저장을 요청하지 않았을 때.
- 즉시 memory, rubric, guide, skill patch만 업데이트하라는 요청일 때.
- 기대 동작, 실제 동작, 차이, 근거, 후보 규칙을 확인할 수 없을 때.

## 검증 방법

생성된 feedback log 검증:

```bash
python3 scripts/validate-feedback-log.py <created-feedback.md>
```

실제 저장 경로가 아닌 temp/eval output의 내용만 검증:

```bash
python3 scripts/validate-feedback-log.py --content-only <generated-feedback.md>
```

pipeline으로 정규화된 incident JSON을 raw feedback Markdown으로 생성:

```bash
python3 scripts/run_pipeline.py --input <input.json> --output <output.md> --validate
```

eval spec 검증:

```bash
python3 scripts/run_evals.py --validate
```

eval rollout 검증:

```bash
python3 scripts/run_evals.py --rollout --json
```

기대 결과:

- `validate-feedback-log.py` 결과가 `ok: true`다.
- `run_evals.py --validate`가 `VALID feedback-ai-logging-v2.eval.md`를 출력한다.
- `run_evals.py --rollout --json`에서 `failed: 0`, `errors: 0`이다.
- `llm_judge` 항목은 자동 채점 완료로 보지 않고 checklist로만 취급한다.
