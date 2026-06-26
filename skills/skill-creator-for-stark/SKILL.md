---
name: skill-creator-for-stark
description: 사용자의 고정 규칙에 맞춰 범용 에이전트 스킬 패키지를 설계, 작성, 검증, 기록할 때 사용합니다.
version: 1.1.0
author: Agent
license: MIT
metadata:
  tags: [skills, authoring, workflow, verification, subagents]
  related_skills: [writing-plans, portable-skill-library-operations]
---

# Skill Creator for Stark

## 개요

이 스킬은 사용자의 기준에 맞는 재사용 가능한 범용 에이전트 스킬 패키지를 만들 때 사용한다. 목표는 단순히 `SKILL.md` 하나를 쓰는 것이 아니라, 입력과 산출물을 명확히 변수화하고, 필요한 환경을 먼저 검증하며, 세부 지식은 `references/`, 출력 형식은 `templates/`, 반복 가능한 deterministic 작업은 `scripts/`로 분리한 portable skill package를 만드는 것이다.

`SKILL.md`는 전체 workflow를 조율하는 orchestration 문서로 유지한다. 구체적인 작성 규칙, 하드 게이트, trigger 설계, subagent 분할 기준, 템플릿 세부사항은 linked support files를 참조한다.

## 사용 시점

다음 요청에 이 스킬을 사용한다.

- 새 범용 에이전트 스킬 패키지를 설계하거나 생성할 때.
- 기존 스킬을 사용자의 고정 규칙에 맞게 개선할 때.
- 스킬의 입력/출력 변수, 환경 fast-fail, 출력 템플릿, 검증 checklist를 정리해야 할 때.
- 여러 support files가 필요한 복합 스킬을 만들 때.
- 가능한 결정적 작업을 `scripts/`로 분리해 반복 실행 가능하게 만들 때.
- subagent 병렬 작업으로 초안 작성, 검토, 검증을 나누는 것이 효과적인 경우.

## 사용하지 말아야 할 때

- 단순한 일회성 답변이나 일반 문서 작성만 필요한 경우.
- 도메인별 전문 스킬이 이미 있고, 새 스킬 package가 필요 없는 경우.
- 사용자가 파일 쓰기나 repo metadata 변경을 승인하지 않은 경우.
- legal, financial, medical 판단을 사용자 대신 결정해야 하는 경우.
- 설치 가이드, 외부 배포, registry publish, 자동 설치가 주목적인 경우.

## 입력 변수

스킬 작성 전에 다음 입력을 명시하거나 tool로 확인한다. 중요한 입력이 빠졌고 안전하게 추론할 수 없으면 fast fail한다.

- `INPUT_SKILL_GOAL`: 만들거나 수정할 스킬의 목적.
- `INPUT_TRIGGER_CONDITIONS`: 스킬을 사용해야 하는 상황.
- `INPUT_TARGET_USERS`: 주 사용자 또는 사용 맥락.
- `INPUT_REPO_ROOT`: repository root.
- `INPUT_SKILL_ROOT`: `skills/` root.
- `INPUT_SKILL_NAME`: 생성/수정할 skill name과 directory basename.
- `INPUT_CONSTRAINTS`: 반드시 지켜야 하는 사용자 규칙.
- `INPUT_REFERENCE_MATERIALS`: 참고할 기존 문서, 세션, 파일, repo artifact.
- `INPUT_APPROVAL_SCOPE`: 사용자가 승인한 실행 범위.
- `INPUT_OVERWRITE_POLICY`: 대상 스킬이 이미 있을 때 merge, patch, replace, abort 중 어떤 정책을 쓸지.
- `INPUT_HISTORY_POLICY`: 스킬 생성/개선 이력을 어디에 어떤 형식으로 남길지.
- `INPUT_TRIGGER_EXAMPLE_POLICY`: `should_trigger` / `should_not_trigger` 예시를 작성만 할지, 검토까지 할지, 생략할지.

## 출력 변수

작업 결과는 다음 산출물 변수에 대응시켜 보고한다.

- `OUTPUT_SKILL_DIR`: 생성/수정된 skill directory.
- `OUTPUT_SKILL_MD`: 생성/수정된 `SKILL.md` 경로.
- `OUTPUT_REFERENCES`: 생성/수정된 `references/` 파일 목록.
- `OUTPUT_TEMPLATES`: 생성/수정된 `templates/` 파일 목록.
- `OUTPUT_SCRIPTS`: 생성/수정된 `scripts/` 파일 목록.
- `OUTPUT_HISTORY_RECORD`: 생성/수정된 작업 이력 파일 또는 기록 위치.
- `OUTPUT_TRIGGER_EXAMPLES`: `should_trigger` / `should_not_trigger` 예시 목록 또는 파일.
- `OUTPUT_VERIFICATION_RESULT`: 실행한 검증과 결과.
- `OUTPUT_OPEN_QUESTIONS`: 남은 질문 또는 미확인 사항.
- `OUTPUT_NEXT_ACTIONS`: commit, 추가 review 등 다음 단계.

## 필수 환경

작업 전에 다음 환경을 확인한다.

- `ENV_REPO_ROOT`: `INPUT_REPO_ROOT`가 존재하고 접근 가능해야 한다.
- `ENV_SKILL_ROOT`: `INPUT_SKILL_ROOT`가 존재하거나 생성 승인을 받아야 한다.
- `ENV_WRITE_ALLOWED`: 파일 생성/수정 승인이 있어야 한다.
- `ENV_VALIDATOR_COMMAND`: validator를 만들거나 실행하려면 `python3` 또는 대체 실행 명령이 있어야 한다.
- `ENV_GIT_AVAILABLE`: diff/status 검증을 위해 `git` 사용 가능 여부를 확인한다.
- `ENV_EXISTING_WORKTREE`: unrelated worktree changes가 있는지 확인한다.

## Hard Gates

스킬 패키지는 다음 크기와 구조 제한을 통과해야 한다. 제한을 넘으면 support file로 분리하거나 scope를 줄인다.

- Metadata gate: `name` + `description`은 항상 컨텍스트에 들어간다고 보고 짧게 유지한다.
  - `name`: 1-64자, lowercase hyphen slug, directory basename과 일치.
  - `description`: 1-1024자, 가능하면 약 100 words 이하, trigger condition과 주요 near-miss를 압축적으로 설명.
- `SKILL.md` body gate: trigger 시 로드된다고 보고 5,000 words 이하로 유지한다.
- Support file gate: `references/`, `templates/`, `scripts/`, `assets/`, `history/` 외 임의 디렉터리를 만들지 않는다.
- Progressive disclosure gate: `SKILL.md`가 긴 판단 tree, 긴 예시, 도메인 지식, 반복 skeleton, deterministic logic을 직접 품으면 실패로 본다.
- Trigger example gate: 가능하면 최소 3개 `should_trigger`, 3개 `should_not_trigger` 예시를 남긴다. 실행형 고급 평가는 요구하지 않는다.
- Deterministic workflow gate: 반복 가능하고 입력/출력이 명확한 작업은 가능한 한 `scripts/`로 분리한다.

## Fast Fail

다음 조건에서는 즉시 중단하고 사용자에게 필요한 입력이나 승인을 요청한다.

- `INPUT_SKILL_NAME`이 없거나 lowercase hyphen slug가 아니다.
- `INPUT_SKILL_ROOT`가 없고 새 root 생성 승인이 없다.
- file write, metadata write, destructive overwrite 중 필요한 승인이 없다.
- 대상 skill directory가 이미 존재하지만 `INPUT_OVERWRITE_POLICY`가 없다.
- 기존 사용자 변경이 있는데 덮어써야만 진행 가능한 상황이다.
- validator script를 만들기로 했지만 실행 가능한 명령이 없다.
- 사용자가 `SKILL.md`에 긴 세부 자료를 모두 넣으라고 요구해 orchestration-only 원칙과 충돌한다.
- 외부 배포, 자동 설치, registry publish, credential 사용이 필요하지만 별도 승인이 없다.

## Workflow

1. **입력 정리**
   - 사용자 요청과 live repo 상태에서 `INPUT_` 변수를 채운다.
   - 추정값은 `추정`, tool로 확인한 값은 `확인됨`, 확인 불가 값은 `미확인`으로 구분한다.

2. **환경 확인**
   - `ENV_` 항목을 확인한다.
   - fast-fail 조건을 먼저 적용한다.

3. **작업 분해**
   - 산출물을 `SKILL.md`, `references`, `templates`, `scripts`, `history`, `verification`으로 나눈다.
   - dependency graph를 만들고 독립 가능한 구간을 subagent 병렬 작업 후보로 표시한다.

4. **하드 게이트 설계**
   - metadata, `SKILL.md` body, support file 구조, trigger example, deterministic workflow gate를 먼저 정한다.
   - 하드 게이트는 `references/skill-authoring-rules.md`와 validator에 반영한다.

5. **Trigger 예시 작성**
   - `should_trigger` / `should_not_trigger` 예시를 현실적인 사용자 요청으로 작성한다.
   - near-miss negative case를 포함해 과소/과잉 trigger를 줄인다.
   - 고급 반복 평가는 이 단계의 기본 범위가 아니다. 이력에 남길 수 있는 간단한 Markdown/JSON만 작성한다.
   - 상세 기준은 `references/trigger-history-rules.md`를 따른다.

6. **Subagent 병렬 초안 작성**
   - 독립 초안, 도메인 조사, 검토, 검증 checklist 확장은 subagent에 병렬 위임한다.
   - subagent prompt에는 반드시 `INPUT_`, `OUTPUT_`, `ENV_`, 한글 작성, references 분리 규칙을 포함한다.
   - 상세 패턴은 `references/subagent-parallelization-patterns.md`를 따른다.

7. **Parent 통합**
   - parent agent가 subagent 결과를 직접 검증하고 통합한다.
   - subagent self-report만으로 완료를 주장하지 않는다.

8. **파일 작성**
   - `SKILL.md`는 workflow 중심으로 작성한다.
   - 세부 기준은 `references/`, 재사용 skeleton은 `templates/`, deterministic 반복 작업은 `scripts/`, 생성/개선 기록은 `history/`에 둔다.
   - deterministic workflow 분리 기준은 `references/deterministic-workflow-rules.md`를 따른다.
   - 작성 규칙은 `references/skill-authoring-rules.md`를 따른다.

9. **History 기록**
   - 고도화된 평가 시스템 대신 간단한 이력을 남긴다.
   - 기록에는 날짜, 목표, 주요 변경, trigger 예시, 검증 결과, 남은 문제를 포함한다.

10. **검증**
    - `Verification Checklist`를 적용한다.
    - validator, `git diff --check`, `git status --short`, 대표 파일 read-back을 수행한다.

11. **템플릿 기반 보고**
    - 최종 보고는 `templates/skill-output-template.md` 구조를 따른다.

## Subagent Parallelization

Subagent는 적극적으로 사용하되, 병렬화가 실제 이득을 주는 구간에만 사용한다.

병렬화에 적합한 작업:

- 기존 유사 스킬 조사.
- 도메인 요구사항 정리.
- `references/` 초안 작성.
- `templates/` 초안 작성.
- validator script 초안 작성.
- trigger example 초안 작성.
- 구조 review, 한국어/식별자 보존 review, verification coverage review, portability review.

직렬로 처리해야 하는 작업:

- `INPUT_SKILL_NAME` 확정.
- overwrite/metadata write 승인 확인.
- 최종 파일 write.
- 최종 검증과 완료 보고.

상세 기준과 prompt skeleton은 `references/subagent-parallelization-patterns.md`를 따른다.

## 출력 템플릿

스킬 실행 결과는 `templates/skill-output-template.md`를 사용해 보고한다. 템플릿을 그대로 복사하지 말고 실제 `INPUT_`/`OUTPUT_` 값을 채운다.

## Commit Pitfalls

- unrelated worktree changes를 함께 commit하지 않는다.
- auto-sync 또는 background process가 이미 commit했을 수 있으므로 `git status`만 보지 말고 필요하면 `git log -- <path>`를 확인한다.
- 검증 실패 상태를 commit하지 않는다.
- 기존 스킬 rename/move는 git에서 delete+create처럼 보일 수 있으므로 diff를 확인한다.
- generated artifact와 source skill package를 섞지 않는다.
- 스킬 파일 생성과 현재 세션의 즉시 사용 가능 여부를 혼동하지 않는다.

## Verification Checklist

- [ ] `SKILL.md`가 존재한다.
- [ ] YAML frontmatter가 존재하고 필수 key가 있다.
- [ ] `name`이 directory basename과 일치한다.
- [ ] `name`이 1-64자 lowercase hyphen slug다.
- [ ] `description`이 사용 시점을 설명하고 1024자 이하이며 가능하면 약 100 words 이하다.
- [ ] `SKILL.md` body가 5,000 words 이하이고 orchestration 중심이다.
- [ ] `INPUT_`, `OUTPUT_`, `ENV_` 변수가 정의되어 있다.
- [ ] 필수 환경 fast-fail 조건이 있다.
- [ ] `Hard Gates` 섹션이 있다.
- [ ] 출력 템플릿이 있다.
- [ ] `Commit Pitfalls` 섹션이 있다.
- [ ] `Verification Checklist` 섹션이 있다.
- [ ] 병렬 처리 가능한 subagent 구간이 정의되어 있다.
- [ ] 세부 기준은 references/templates/scripts/history로 분리되어 있다.
- [ ] 가능한 deterministic workflow는 `scripts/`로 분리되어 있다.
- [ ] `should_trigger` / `should_not_trigger` 예시가 있거나 생략 사유가 보고됐다.
- [ ] validator script가 있다면 통과한다.
- [ ] `git diff --check`가 통과한다.
- [ ] 최종 보고가 `OUTPUT_` 변수와 대응된다.

## Final Response Checklist

최종 응답에는 다음을 포함한다.

- `INPUT_` 요약.
- `OUTPUT_` 산출물 경로.
- 수행한 검증과 실제 결과.
- 의도적으로 남긴 영어 identifier.
- 미확인 사항.
- commit 여부와 다음 단계.
