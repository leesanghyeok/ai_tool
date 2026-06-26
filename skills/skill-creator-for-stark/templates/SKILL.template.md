---
name: <skill-name>
description: <언제 이 스킬을 사용할지 한 문장으로 설명>
version: 1.0.0
author: Agent
license: MIT
metadata:
  tags: []
  related_skills: []
---

# <스킬 제목>

## 개요

<스킬의 목적과 산출물을 설명한다.>

## 사용 시점

- <trigger condition>

## 사용하지 말아야 할 때

- <non-goal 또는 다른 스킬을 써야 하는 경우>

## 입력 변수

| 변수 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `INPUT_...` | required | 없음 | <입력의 의미, 필요한 이유, 없을 때 처리, 영향을 받는 workflow/검증을 설명한다.> |
| `INPUT_...` | optional | <default> | <기본값을 언제 쓰는지와 사용자가 바꾸면 무엇이 달라지는지 설명한다.> |
| `INPUT_WORKFLOW_MODE` | required | 없음 | `create`, `modify`, `quality-review-only` 중 하나다. 최초 생성은 품질 루브릭 평가 필수, 수정은 선택, 검증 전용은 read-only 평가 필수로 처리한다. |
| `INPUT_FEEDBACK_LOGGING_REQUEST` | optional | 없음 | 사용자가 이 스킬 사용 경험의 불만족을 feedback log로 남기라고 요청했는지와 대상 사건이다. 명시 요청이 없으면 일반 실행 중에는 파일을 쓰지 않는다. |

## 출력 변수

| 변수 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `OUTPUT_...` | required | 없음 | <반드시 보고해야 하는 산출물과 검증 방법을 설명한다.> |
| `OUTPUT_...` | optional | `[]` | <없을 수 있는 산출물과 없을 때 보고할 값을 설명한다.> |
| `OUTPUT_QUALITY_CERTIFICATION` | optional | 없음 | 최초 생성 또는 품질 검증을 실행한 경우 95점 기준 통과 여부와 hard gate 결과를 보고한다. 수정 모드에서 생략했으면 생략 사유를 보고한다. |
| `OUTPUT_FEEDBACK_LOG_FILES` | optional | `[]` | 사용자가 스킬 사용 불만족 기록을 요청해 생성한 `feedback/` raw log 파일 목록이다. 요청이 없거나 중복이면 빈 배열과 사유를 보고한다. |

## 필수 환경

| 환경 항목 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `ENV_...` | required | <command 또는 권한> | <이 기능 수행에 필요한 CLI, MCP, file permission, network/API, validator command를 설명한다. 사용자 입력이 아니라 실행 전제 조건이다.> |
| `ENV_...` | optional | <default> | <없으면 어떤 기능을 생략하거나 대체하는지 설명한다.> |
| `ENV_FEEDBACK_LOGGING_REFERENCE` | optional | `feedback-ai-logging-v2` | 스킬 사용 불만족 raw log 작성 시 참고할 format/workflow다. 사용 가능하면 `feedback-ai-logging-v2`를 로드하고, 없으면 이 스킬의 `feedback/` 절차와 동일한 필수 section을 사용한다. |

## 하드 게이트 (Hard Gates)

- Metadata: `name`은 1-64자 lowercase hyphen slug이고 `description`은 1-1024자, 가능하면 약 100 words 이하다.
- `SKILL.md` body는 5,000 words 이하이며 orchestration 중심이다.
- 긴 세부 기준은 `references/`, 반복 skeleton은 `templates/`, deterministic 반복 작업은 `scripts/`, 생성/개선 기록은 `history/`, 사용 불만족 raw log는 `feedback/`로 분리한다.
- 가능하면 `should_trigger` 3개 이상과 `should_not_trigger` 3개 이상을 남긴다.
- 최초 생성 시 `/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md` 평가에서 `certification_score >= 95`와 D1-D5 hard gate 통과 전에는 완료로 보고하지 않는다. 수정 작업에서는 품질 평가를 실행하거나 생략 사유를 보고한다.
- 사용자가 이 스킬 사용 불만족을 기록해 달라고 요청하면 `feedback/` 아래에 `feedback-ai-logging-v2` 호환 raw log를 남길 수 있어야 한다.

## 빠른 중단 조건 (Fast Fail)

- <준비되지 않았을 때 즉시 중단할 조건>

## 작업 절차 (Workflow)

1. <입력 정리>
2. <환경 확인>
3. <작업 분해>
4. <하드 게이트 확인>
5. <trigger 예시 작성>
6. <실행>
7. <사용자가 요청한 경우 `feedback/` raw log 기록>
8. <history 기록>
9. <검증>
10. <보고>

## Subagent 병렬화

- <병렬화 가능한 구간>
- <직렬로 유지해야 하는 구간>
- <parent 검증 방식>

## Trigger 예시

### 사용해야 하는 예시 (`should_trigger`)

- <스킬이 사용되어야 하는 현실적인 사용자 요청>

### 사용하지 말아야 하는 예시 (`should_not_trigger`)

- <키워드는 비슷하지만 이 스킬을 쓰면 안 되는 near-miss 요청>

## 피드백 로깅 (Feedback Logging)

- 사용자가 이 스킬을 사용한 뒤 기대와 다르게 동작했다고 명시하고 기록을 요청하면, 해당 사건을 이 스킬 디렉터리 내부 `feedback/YYYY-MM-DD/{HHMMSS}-{session_id}-{short-slug}.md`에 남긴다.
- 포맷은 `feedback-ai-logging-v2/references/file-format.md`를 기반으로 하며, `type: feedback-log`, `source_type: skill-dissatisfaction`, body-only `sha256`, 필수 body section을 유지한다.
- 새 파일을 쓰기 전에 기존 `feedback/**`에서 같은 session/source와 의미상 같은 사건이 있는지 확인한다.
- 개별 스킬 개선 후보와 `skill-creator-for-stark` 개선 후보를 분리해 최종 보고한다.

## 커밋 주의사항 (Commit Pitfalls)

- unrelated worktree changes를 함께 commit하지 않는다.
- 검증 실패 상태를 commit하지 않는다.
- <스킬별 commit 주의사항>

## 검증 체크리스트 (Verification Checklist)

- [ ] `SKILL.md`가 존재한다.
- [ ] frontmatter 필수 key가 있다.
- [ ] `name`과 `description`이 Metadata gate를 통과한다.
- [ ] `SKILL.md` body가 5,000 words 이하이고 orchestration 중심이다.
- [ ] `INPUT_`, `OUTPUT_`, `ENV_` table이 있고 각 항목에 필수/기본값/설명이 있다.
- [ ] `ENV_`가 사용자 입력이 아니라 필요한 도구/권한/명령 조건으로 설명되어 있다.
- [ ] fast-fail 조건이 있다.
- [ ] 출력 템플릿 또는 final response 형식이 있다.
- [ ] support files가 필요한 경우 references/templates/scripts/history/feedback으로 분리되어 있다.
- [ ] 가능한 deterministic workflow가 `scripts/`로 분리되어 있다.
- [ ] `should_trigger` / `should_not_trigger` 예시가 있거나 생략 사유가 보고됐다.
- [ ] 스킬 사용 불만족을 `feedback/`에 기록하는 절차가 있다.
- [ ] 검증 명령이 실행됐다.
- [ ] 최초 생성이면 `skill-quality-rubric-v1.md` 기준 `certification_score >= 95`와 D1-D5 hard gate 통과가 확인됐다.
- [ ] 수정 작업이면 품질 평가 실행 결과 또는 생략 사유가 보고됐다.
- [ ] 검증 전용 요청이면 파일 수정 없이 JSON scorecard가 산출됐다.

## 최종 응답 체크리스트 (Final Response Checklist)

- `INPUT_` 값과 사용한 default.
- `OUTPUT_` 산출물.
- 검증 결과.
- 품질 루브릭 평가 결과 또는 생략 사유.
- feedback log 생성 파일 또는 미생성 사유.
- 남은 문제.
- 다음 단계.
