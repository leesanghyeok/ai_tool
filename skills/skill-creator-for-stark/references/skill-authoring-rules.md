# 스킬 작성 규칙

## 목적

이 문서는 `skill-creator-for-stark`가 새 스킬을 만들거나 기존 스킬을 개선할 때 적용할 세부 규칙을 정의한다. `SKILL.md`에는 전체 workflow만 두고, 이 문서에는 판단 기준과 작성 세부사항을 둔다.

## 기본 package 구조

권장 구조:

```text
skills/<skill-name>/
  SKILL.md
  references/
  templates/
  scripts/
  assets/
```

필수 파일은 `SKILL.md`다. 나머지는 필요할 때만 만든다.

- `references/`: 긴 규칙, 사례, 조사 결과, 판단 기준, runbook.
- `templates/`: 반복적으로 복사해 채울 출력물 또는 파일 skeleton.
- `scripts/`: deterministic 검증, 변환, 수집 helper.
- `assets/`: 이미지, static artifact, non-text support file.

## Frontmatter 규칙

`SKILL.md`는 YAML frontmatter로 시작한다.

필수 key:

```yaml
---
name: <lowercase-hyphen-slug>
description: <언제 사용할지 분명한 설명>
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: []
    related_skills: []
---
```

규칙:

- `name`은 directory basename과 일치해야 한다.
- `description`은 기능 나열보다 trigger condition을 설명해야 한다.
- `description`은 1024자 이하로 유지한다.
- YAML key, file path, command, JSON key, environment variable은 영어 identifier를 유지한다.
- 설명 prose는 한국어로 쓴다.

## 필수 섹션

새 스킬에는 기본적으로 다음 섹션을 둔다.

1. `## 개요`
2. `## 사용 시점`
3. `## 사용하지 말아야 할 때`
4. `## 입력 변수`
5. `## 출력 변수`
6. `## 필수 환경`
7. `## Fast Fail`
8. `## Workflow`
9. `## Commit Pitfalls`
10. `## Verification Checklist`
11. `## Final Response Checklist`

필요하면 다음 섹션을 추가한다.

- `## Subagent Parallelization`
- `## 출력 템플릿`
- `## 보안과 프라이버시`
- `## References`

## INPUT_/OUTPUT_/ENV_ 변수 규칙

모든 주요 입력은 `INPUT_` prefix로 관리한다.

예:

- `INPUT_TASK_SCOPE`
- `INPUT_TARGET_PATH`
- `INPUT_APPROVAL_SCOPE`

모든 주요 산출물은 `OUTPUT_` prefix로 관리한다.

예:

- `OUTPUT_CREATED_FILES`
- `OUTPUT_VERIFICATION_RESULT`
- `OUTPUT_NEXT_ACTIONS`

실행 전제 조건은 `ENV_` prefix로 관리한다.

예:

- `ENV_REPO_ROOT`
- `ENV_WRITE_ALLOWED`
- `ENV_GIT_AVAILABLE`

규칙:

- 변수는 스킬 본문에서 한 번 이상 정의되어야 한다.
- final response는 실제 산출물을 `OUTPUT_` 변수와 대응시켜 보고해야 한다.
- 입력이 없을 때 추정하지 말아야 할 항목은 fast fail한다.

## SKILL.md와 support files 분리 기준

`SKILL.md`에 둘 것:

- trigger condition.
- high-level workflow.
- approval boundary.
- fast-fail gate.
- subagent orchestration policy.
- final verification/reporting policy.

`references/`로 뺄 것:

- 긴 checklist.
- 여러 사례.
- 판단 tree.
- 도메인 지식.
- subagent prompt 예시.
- migration/runbook 상세.

`templates/`로 뺄 것:

- 최종 보고 템플릿.
- 새 파일 skeleton.
- 반복적으로 재사용하는 Markdown/YAML/JSON 구조.

`scripts/`로 뺄 것:

- YAML/frontmatter 검증.
- JSON schema 또는 manifest parse check.
- Markdown fence balance check.
- file tree consistency check.

## 한글 작성 규칙

- 사용자와 agent가 읽는 설명은 한국어로 작성한다.
- heading은 한국어 우선으로 작성한다.
- 필요한 경우 영어 compatibility label을 괄호에 둔다.
- machine-readable identifier는 번역하지 않는다.

유지할 영어:

- `INPUT_`, `OUTPUT_`, `ENV_` 변수명.
- YAML/JSON key.
- command.
- file path.
- skill name.
- API/tool/runtime identifier.
- 코드 블록 내부의 syntax.

## 검증 규칙

새 스킬 작성 후 최소 검증:

```bash
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
python3 skills/skill-creator-for-stark/scripts/validate-skill-package.py skills/<skill-name>
git diff --check
git status --short
```

manifest가 없으면 JSON 검증은 생략하고 생략 이유를 보고한다. validator가 없으면 checklist read-back과 frontmatter 확인으로 대체하되, 가능하면 validator를 만든다.

## 흔한 실패 패턴

- `SKILL.md`가 너무 길어지고 references가 비어 있음.
- 입력과 출력이 prose에 섞여 있어 추적 불가.
- 환경 준비 여부를 확인하지 않고 파일을 씀.
- README/plugin manifest를 갱신하지 않아 discovery가 깨짐.
- subagent에게 초안 작성을 맡긴 뒤 parent 검증 없이 완료 처리.
- 영어 prose가 많이 남아 사용자의 한국어 문서 기준을 어김.
- unrelated worktree changes를 함께 건드림.
