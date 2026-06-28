# 2026-06-28 eval contract backfill

- mode: modify
- 목표: `skill-creator-for-stark`의 eval contract gate에 맞춰 `feedback-ai-logging-v2`에 deterministic eval harness를 추가했다.
- 주요 변경:
  - `evals/feedback-ai-logging-v2.eval.md` 추가.
  - `evals/golden/case-1/input.json`, `evals/golden/case-2/input.json`, `evals/golden/case-3/input.json`과 각 `expected.md` 추가.
  - `scripts/run_evals.py` 추가.
  - `scripts/run_pipeline.py` 추가. 정규화된 incident JSON을 raw feedback Markdown으로 생성하는 deterministic happy path다.
  - `scripts/validate-feedback-log.py --content-only` 추가. Rollout temp output처럼 실제 저장 경로가 아닌 파일은 path convention을 건너뛰고 content/hash/taxonomy/section을 검증한다.
- trigger 영향: 없음. 기존 raw feedback logging workflow를 유지하고 regression contract만 추가했다.
- 품질 평가: 구조 검증과 eval rollout 검증 후 별도 보고에서 판단한다.
