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

- `INPUT_...`: <설명>

## 출력 변수

- `OUTPUT_...`: <설명>

## 필수 환경

- `ENV_...`: <필요한 환경 또는 전제>

## Hard Gates

- Metadata: `name`은 1-64자 lowercase hyphen slug이고 `description`은 1-1024자, 가능하면 약 100 words 이하다.
- `SKILL.md` body는 5,000 words 이하이며 orchestration 중심이다.
- 긴 세부 기준은 `references/`, 반복 skeleton은 `templates/`, deterministic 반복 작업은 `scripts/`, 생성/개선 기록은 `history/`로 분리한다.
- 가능하면 `should_trigger` 3개 이상과 `should_not_trigger` 3개 이상을 남긴다.

## Fast Fail

- <준비되지 않았을 때 즉시 중단할 조건>

## Workflow

1. <입력 정리>
2. <환경 확인>
3. <작업 분해>
4. <하드 게이트 확인>
5. <trigger 예시 작성>
6. <실행>
7. <history 기록>
8. <검증>
9. <보고>

## Subagent Parallelization

- <병렬화 가능한 구간>
- <직렬로 유지해야 하는 구간>
- <parent 검증 방식>

## Commit Pitfalls

- unrelated worktree changes를 함께 commit하지 않는다.
- 검증 실패 상태를 commit하지 않는다.
- <스킬별 commit 주의사항>

## Verification Checklist

- [ ] `SKILL.md`가 존재한다.
- [ ] frontmatter 필수 key가 있다.
- [ ] `name`과 `description`이 Metadata gate를 통과한다.
- [ ] `SKILL.md` body가 5,000 words 이하이고 orchestration 중심이다.
- [ ] `INPUT_`, `OUTPUT_`, `ENV_` 변수가 정의되어 있다.
- [ ] fast-fail 조건이 있다.
- [ ] 출력 템플릿 또는 final response 형식이 있다.
- [ ] support files가 필요한 경우 references/templates/scripts/history로 분리되어 있다.
- [ ] 가능한 deterministic workflow가 `scripts/`로 분리되어 있다.
- [ ] `should_trigger` / `should_not_trigger` 예시가 있거나 생략 사유가 보고됐다.
- [ ] 검증 명령이 실행됐다.

## Final Response Checklist

- `INPUT_` 요약.
- `OUTPUT_` 산출물.
- 검증 결과.
- 남은 문제.
- 다음 단계.
