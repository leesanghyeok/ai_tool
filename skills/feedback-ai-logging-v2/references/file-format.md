# Feedback file format

## Path

```text
<OUTPUT_ROOT>/<OUTPUT_SUBDIR>/YYYY-MM-DD/{HHMMSS}-{session_id}-{short-slug}.md
```

`created_at`에서 date와 `HHMMSS`를 만든다. `short-slug`는 failure pattern 중심의 영어 lowercase hyphen slug다.

## Frontmatter

```yaml
---
type: feedback-log
source_type: ai-dissatisfaction
source_platform: cli
source_ref: ""
session_id: "unknown-session"
ingested: YYYY-MM-DD
created_at: YYYY-MM-DDTHH:MM:SS+09:00
task_type: planning
agent_or_model: ""
severity: medium
categories: [requirement-miss]
sha256: "<body-sha256>"
---
```

## Body sections

- `## 상황 (Situation)`
- `## 불만족한 점 (Dissatisfaction)`
- `## 기대한 동작 (Expected Behavior)`
- `## 근거 (Evidence)`
- `## 실패 범주 (Failure Categories)`
- `## 심각도 (Severity)`
- `## 후보 Agent 규칙 (Candidate Agent Rule)`
- `## 후보 체크리스트 항목 (Candidate Checklist Items)`

`sha256`은 closing frontmatter delimiter 뒤의 Markdown body만 대상으로 계산한다.
