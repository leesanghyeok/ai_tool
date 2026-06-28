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

<스킬의 목적, 직접 산출물, 성공 기준을 짧게 설명한다.>

## 사용 판단

### 사용한다

- <이 스킬을 사용해야 하는 trigger condition>
- <현실적인 사용자 요청 예시 또는 상황>

### 사용하지 않는다

- <non-goal, near-miss, 더 적합한 다른 스킬>
- <키워드는 비슷하지만 이 스킬을 쓰면 안 되는 경우>

## 입력 변수

`INPUT_`는 사용자가 실제로 제공하거나 source에서 확인해야 하며 결과를 바꾸는 값만 둔다. 안정적 default, 내부 정책, 보고 문장 조각은 변수로 만들지 않는다.

| 변수 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `INPUT_...` | required | 없음 | <없으면 workflow를 시작할 수 없는 핵심 입력과 그 이유를 설명한다.> |
| `INPUT_...` | optional | <explicit-default> | <사용자가 바꾸면 산출물/검증/안전 경계가 어떻게 달라지는지 설명한다.> |

## 출력 변수

`OUTPUT_`는 완료 여부, 생성/수정 파일, skip/blocker, 검증 결과, 다음 승인점 판단에 필요한 값만 둔다.

| 변수 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `OUTPUT_...` | required | 없음 | <완료 판단이나 검증에 반드시 필요한 산출물이다.> |
| `OUTPUT_...` | optional | `[]` | <없을 수 있는 산출물과 없을 때 보고할 값이다.> |

## 필수 환경

`ENV_`는 사용자 입력이 아니라 실행 전제다. 실패 시 fast-fail하거나 workflow가 달라지는 항목만 표에 둔다. 단순 권장 도구는 prose checklist로 낮춘다.

| 환경 항목 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `ENV_...` | required | <command 또는 권한> | <없으면 어떤 단계가 실패하거나 중단되는지 설명한다.> |

## 하드 게이트 (Hard Gates)

이 스킬의 직접 산출물 품질과 안전성을 보장하는 domain-specific gate만 작성한다. `name`, `description`, body size, directory basename 같은 범용 package 규칙은 여기에 복사하지 않는다.

- <산출물 불변 조건 또는 안전 조건>
- <evidence/idempotency/validation 같은 완료 전 필수 조건>

## 빠른 중단 조건 (Fast Fail)

- <필수 입력, 권한, source, 승인, 검증 전제가 없어 중단해야 하는 조건>

## 작업 절차 (Workflow)

1. <필수 입력과 승인 범위를 확인한다.>
2. <source나 기존 state를 read-only로 확인한다.>
3. <산출물을 만들거나 수정한다.>
4. <deterministic 검증 또는 read-back을 실행한다.>
5. <필요하면 `evals/<skill-name>.eval.yaml`, declared `evals/cases/*/case.yaml`, `scripts/run_evals.py`를 생성하고 `--validate`를 실행한다.>
6. <상태, 파일, 검증 결과, 미확인 항목을 보고한다.>

## Subagent 병렬화

- 병렬화 가능한 구간: <독립 조사, 초안, 검토, fixture 작성 등>
- 직렬로 유지해야 하는 구간: <승인 확인, 최종 write, 최종 검증 등>
- parent 검증 방식: <subagent self-report가 아니라 파일/read-back/test 결과로 확인한다.>

## 피드백 로깅 (Feedback Logging)

- 사용자가 이 스킬 사용 경험의 불만족을 “기록해/남겨/로그로 저장해”라고 명시하면, 해당 사건을 이 스킬 디렉터리 내부 `feedback/YYYY-MM-DD/{HHMMSS}-{session_id}-{short-slug}.md`에 남긴다.
- 가능하면 `feedback-ai-logging-v2` 포맷을 사용하고, 중복 검사와 read-back 검증을 수행한다.
- 개별 스킬 개선 후보와 `skill-creator-for-stark` 개선 후보를 분리해 보고한다.

## 커밋 주의사항 (Commit Pitfalls)

- unrelated worktree changes를 함께 commit하지 않는다.
- 검증 실패 상태를 commit하지 않는다.
- <스킬별 commit 주의사항>

## 검증 체크리스트 (Verification Checklist)

- [ ] `SKILL.md`가 존재한다.
- [ ] frontmatter 필수 key가 있다.
- [ ] trigger 판단이 하나의 canonical section에 있다.
- [ ] `INPUT_`가 결과를 바꾸는 최소 입력만 포함한다.
- [ ] `OUTPUT_`가 완료·검증·후속 승인 판단에 필요한 값만 포함한다.
- [ ] `ENV_`가 사용자 입력이 아니라 실행 전제로 설명된다.
- [ ] `Hard Gates`가 이 스킬의 domain-specific gate만 포함한다.
- [ ] 직접 산출물 skeleton은 `templates/`에 있고 판단 기준은 `references/`에 있다.
- [ ] deterministic 검증 또는 read-back이 실행됐다.
- [ ] eval이 필요한 경우 `evals/<skill-name>.eval.yaml`, declared `evals/cases/*/case.yaml`, `scripts/run_evals.py --validate` 결과가 있다.
- [ ] deterministic multi-step workflow가 있으면 `scripts/run_pipeline.py`가 single entrypoint다.
- [ ] 스킬 사용 불만족을 `feedback/`에 기록하는 절차가 있다.

## 최종 응답 체크리스트 (Final Response Checklist)

- 상태: `completed`, `partial`, `blocked`, `unverified` 중 하나.
- 변경 또는 생성 파일.
- 검증 결과와 실제 command/tool output 요약.
- 품질 평가 결과 또는 생략 사유.
- 미확인 항목과 다음 승인점.
