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
  history/
```

필수 파일은 `SKILL.md`다. 나머지는 필요할 때만 만든다.

- `references/`: 긴 규칙, 사례, 조사 결과, 판단 기준, runbook.
- `templates/`: 반복적으로 복사해 채울 출력물 또는 파일 skeleton.
- `scripts/`: deterministic 검증, 변환, 수집 helper, 반복 workflow.
- `assets/`: 이미지, static artifact, non-text support file.
- `history/`: 생성/개선 이력, trigger 예시, 간단한 검토 기록.

## Frontmatter 규칙

`SKILL.md`는 YAML frontmatter로 시작한다.

필수 key:

```yaml
---
name: <lowercase-hyphen-slug>
description: <언제 사용할지 분명한 설명>
version: 1.0.0
author: Agent
license: MIT
metadata:
  tags: []
  related_skills: []
---
```

규칙:

- `name`은 directory basename과 일치해야 한다.
- `name`은 1-64자 lowercase hyphen slug다.
- `description`은 기능 나열보다 trigger condition을 설명해야 한다.
- `description`은 1-1024자 이하로 유지한다.
- `description`은 가능하면 약 100 words 이하로 유지한다. metadata는 항상 컨텍스트에 들어간다고 본다.
- `description`에는 사용 시점과 주요 near-miss를 압축적으로 넣되 특정 에이전트 실행 환경에 종속된 문구는 피한다.
- YAML key, file path, command, JSON key, environment variable은 영어 identifier를 유지한다.
- 설명 prose는 한국어로 쓴다.

## 크기와 progressive disclosure gate

- `SKILL.md` body는 trigger 시 로드되는 본문이므로 5,000 words 이하로 유지한다.
- `SKILL.md`가 500 lines에 가까워지거나 긴 판단 tree가 들어가면 `references/`로 분리한다.
- 큰 reference file은 목차 또는 읽어야 하는 조건을 앞부분에 둔다.
- 반복적으로 복사할 구조는 `templates/`로 분리한다.
- 반복 가능하고 입력/출력이 명확한 결정적 작업은 `scripts/`로 분리한다.
- 비결정적 판단이 필요한 작업은 workflow와 판단 기준을 문서화하되, 결정 가능한 하위 단계는 script로 빼는 것을 우선한다.

## 필수 섹션

새 스킬에는 기본적으로 다음 섹션을 둔다.

1. `## 개요`
2. `## 사용 시점`
3. `## 사용하지 말아야 할 때`
4. `## 입력 변수`
5. `## 출력 변수`
6. `## 필수 환경`
7. `## Hard Gates`
8. `## Fast Fail`
9. `## Workflow`
10. `## Commit Pitfalls`
11. `## Verification Checklist`
12. `## Final Response Checklist`

필요하면 다음 섹션을 추가한다.

- `## Subagent Parallelization`
- `## Trigger Examples`
- `## 출력 템플릿`
- `## 보안과 프라이버시`
- `## References`

## INPUT_/OUTPUT_/ENV_ 변수 규칙

모든 주요 입력은 `INPUT_` prefix로 관리한다.

예:

- `INPUT_TASK_SCOPE`
- `INPUT_TARGET_PATH`
- `INPUT_APPROVAL_SCOPE`
- `INPUT_HISTORY_POLICY`

모든 주요 산출물은 `OUTPUT_` prefix로 관리한다.

예:

- `OUTPUT_CREATED_FILES`
- `OUTPUT_HISTORY_RECORD`
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
- hard gate와 fast-fail gate.
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
- 반복 데이터 변환, 수집, 생성, 정규화 workflow.

`history/`로 뺄 것:

- 생성/수정 시점의 짧은 의사결정 기록.
- `should_trigger` / `should_not_trigger` 예시.
- 실행한 검증과 남은 문제.
- 고도화된 반복 평가가 아니라 사람이 나중에 추적할 수 있는 lightweight 기록.

## Trigger example 규칙

고급 평가 시스템을 만들지 않아도 trigger 예시는 남긴다.

- `should_trigger`: 스킬이 반드시 쓰여야 하는 현실적인 사용자 요청 3개 이상.
- `should_not_trigger`: 키워드는 비슷하지만 실제로는 다른 스킬이나 일반 답변이 적합한 near-miss 요청 3개 이상.
- 예시는 abstract keyword가 아니라 실제 사용자가 말할 법한 문장으로 쓴다.
- 예시가 부족하면 생략하지 말고 `OUTPUT_OPEN_QUESTIONS`에 부족한 이유를 남긴다.

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
- API/tool identifier.
- 코드 블록 내부의 syntax.

## 검증 규칙

새 스킬 작성 후 최소 검증:

```bash
python3 skills/skill-creator-for-stark/scripts/validate-skill-package.py skills/<skill-name>
git diff --check
git status --short
```

validator가 없으면 checklist read-back과 frontmatter 확인으로 대체하되, 가능하면 validator를 만든다. 정식 test/lint/build가 없으면 focused ad-hoc verification으로 표시한다.

## 흔한 실패 패턴

- `SKILL.md`가 너무 길어지고 references가 비어 있음.
- metadata가 너무 길어 항상 컨텍스트를 소모함.
- 입력과 출력이 prose에 섞여 있어 추적 불가.
- 환경 준비 여부를 확인하지 않고 파일을 씀.
- trigger example 없이 description만 작성함.
- 반복 가능한 deterministic workflow를 매번 agent 판단으로 재작성하게 둠.
- subagent에게 초안 작성을 맡긴 뒤 parent 검증 없이 완료 처리.
- 영어 prose가 많이 남아 사용자의 한국어 문서 기준을 어김.
- 특정 에이전트 실행 환경이나 설치 방식에 불필요하게 종속됨.
- unrelated worktree changes를 함께 건드림.
