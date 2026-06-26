# 피드백 파일 형식 (Feedback file format)

## 목적

이 문서는 raw feedback Markdown의 field 의미, path 규칙, hash 기준을 설명한다. 작성자가 복사해 채우는 파일 skeleton은 `templates/feedback-log.template.md`에 둔다.

## 경로 (Path)

전역 raw feedback:

```text
<OUTPUT_ROOT>/<OUTPUT_SUBDIR>/YYYY-MM-DD/{HHMMSS}-{session_id}-{short-slug}.md
```

기본값은 `<OUTPUT_ROOT>/raw/feedback/YYYY-MM-DD/{HHMMSS}-{session_id}-{short-slug}.md`다.

스킬 내부 feedback:

```text
<SKILL_DIR>/feedback/YYYY-MM-DD/{HHMMSS}-{session_id}-{short-slug}.md
```

`created_at`에서 date와 `HHMMSS`를 만든다. `short-slug`는 failure pattern 중심의 영어 lowercase hyphen slug다.

## Frontmatter 필드

필수 field:

- `type`: 항상 `feedback-log`.
- `source_type`: 일반 AI/agent 불만족은 `ai-dissatisfaction`, 스킬 사용 불만족은 `skill-dissatisfaction`.
- `source_platform`: `cli`, `discord`, `telegram`, `web`, `session-db`, `file` 등 source가 온 표면.
- `source_ref`: session id, thread link, file path, skill name처럼 source를 다시 찾을 수 있는 짧은 참조.
- `session_id`: 확인되면 실제 id, 없으면 `unknown-session`.
- `ingested`: log 작성 날짜 `YYYY-MM-DD`.
- `created_at`: 사건 또는 log 작성 시각 `YYYY-MM-DDTHH:MM:SS+09:00` 형식.
- `task_type`: controlled taxonomy 값. `research`, `coding`, `recommendation`, `summarization`, `planning`, `automation`, `review`, `translation`, `conversation`, `skill-usage`, `other`.
- `agent_or_model`: 확인된 agent/model 이름. 모르면 빈 문자열.
- `severity`: `low`, `medium`, `high`, `critical`.
- `categories`: controlled taxonomy 배열.
- `sha256`: closing frontmatter delimiter 뒤 Markdown body의 UTF-8 `sha256`.

## 본문 섹션 (Body sections)

본문에는 다음 section을 둔다.

- `## 상황 (Situation)`
- `## 불만족한 점 (Dissatisfaction)`
- `## 기대한 동작 (Expected Behavior)`
- `## 실제 동작 (Actual Behavior)`
- `## 근거 (Evidence)`
- `## 실패 범주 (Failure Categories)`
- `## 심각도 (Severity)`
- `## 후보 Agent 규칙 (Candidate Agent Rule)`
- `## 후보 체크리스트 항목 (Candidate Checklist Items)`

## Hash 기준

`sha256`은 closing frontmatter delimiter 뒤의 Markdown body만 대상으로 계산한다. Frontmatter의 `sha256` field 자체는 hash 입력에 포함하지 않는다.

Python 예시:

```python
import hashlib
body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
```

## Raw log 금지 필드

Raw feedback log에는 처리 상태나 승격 상태를 넣지 않는다. 다음 field는 금지한다.

- `triage_status`
- `derived_pages`
- `converted_to_rule`
- `converted_to_rubric`
