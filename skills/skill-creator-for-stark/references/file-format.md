# 스킬 피드백 로그 파일 형식 (Skill feedback log file format)

이 문서는 `templates/feedback-log.template.md`에 있는 raw feedback log skeleton의 field 의미와 검증 기준을 설명한다.

## Frontmatter 필드

- `type`: 항상 `feedback-log`이며 frontmatter에는 `type: feedback-log`로 쓴다.
- `source_type`: 스킬 사용 불만족이면 `skill-dissatisfaction`.
- `source_platform`: 사건이 발생한 surface. 예: `cli`, `discord`, `telegram`.
- `source_ref`: 대상 skill name, skill path, session/thread/file reference.
- `session_id`: 확인 가능하면 실제 id, 없으면 `unknown-session`.
- `severity`: `low`, `medium`, `high`, `critical` 중 하나.
- `categories`: controlled taxonomy 또는 임시 category 배열.
- `sha256`: closing frontmatter delimiter 뒤의 Markdown body만 대상으로 계산한 hash.

## Body 필수 섹션

- `## 상황 (Situation)`
- `## 불만족한 점 (Dissatisfaction)`
- `## 기대한 동작 (Expected Behavior)`
- `## 근거 (Evidence)`
- `## 실패 범주 (Failure Categories)`
- `## 심각도 (Severity)`
- `## 후보 Agent 규칙 (Candidate Agent Rule)`
- `## 후보 체크리스트 항목 (Candidate Checklist Items)`

## 검증 기준

- 사건 하나는 파일 하나에만 기록한다.
- 새 파일을 쓰기 전에 기존 `feedback/**`에서 같은 session/source와 의미상 같은 incident를 검색해 중복 생성을 피한다.
- raw feedback log에는 처리 상태, 승격 여부, TODO 진행 상황을 쓰지 않는다.
- secret, token, private URL, credential 원문은 저장하지 않는다.
