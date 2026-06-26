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
  feedback/
```

필수 파일은 `SKILL.md`다. 나머지는 필요할 때만 만든다.

- `references/`: 긴 규칙, 사례, 조사 결과, 판단 기준, runbook.
- `templates/`: 반복적으로 복사해 채울 출력물 또는 파일 skeleton.
- `scripts/`: deterministic 검증, 변환, 수집 helper, 반복 workflow.
- `assets/`: 이미지, static artifact, non-text support file.
- `history/`: 생성/개선 이력, trigger 예시, 간단한 검토 기록.
- `feedback/`: 스킬 사용 중 발생한 불만족 raw log. `feedback-ai-logging-v2` 호환 포맷으로 사건 단위 파일을 둔다.

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

## Workflow mode와 품질 루브릭 적용 규칙

`skill-creator-for-stark`는 작업을 먼저 mode로 분류한다.

- `create`: 새 skill package 최초 생성이다. `/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md` 평가가 필수이며 `certification_score >= 95`와 D1-D5 hard gate 통과 전에는 완료로 보고하지 않는다.
- `modify`: 기존 skill 수정이다. 구조 검증은 필수이고 품질 루브릭 평가는 선택이다. 사용자가 품질 검증, 95점, 릴리즈 가능 여부를 요구하거나 workflow, approval, verification, trigger, scope, template, validator에 큰 영향을 주는 수정이면 품질 평가를 필수로 승격한다. 생략하면 생략 사유를 최종 보고에 남긴다.
- `quality-review-only`: 파일 수정 없는 검증 전용 mode다. target skill package와 rubric을 read-only로 평가하고 JSON scorecard를 산출한다. 별도 승인 없이 target skill, rubric, history, scorecard 파일을 쓰지 않는다.

품질 평가는 canonical rubric의 baseline 90점이 아니라 이 creator workflow의 release 기준인 95점을 사용한다. 95점 미만이거나 D1-D5 hard gate 중 하나라도 실패하면 개선 loop로 돌아간다.

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

`INPUT_`, `OUTPUT_`, `ENV_`는 bullet list가 아니라 표로 작성한다. 각 표는 필수 여부, 기본값, 설명을 포함해야 한다.

필수 table header:

```markdown
| 변수 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
```

환경 table은 다음 header를 사용한다.

```markdown
| 환경 항목 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
```

규칙:

- `INPUT_`는 사용자가 제공하거나 agent가 확인해야 하는 작업 입력이다.
- `OUTPUT_`는 최종 보고와 검증에서 대응시킬 산출물이다.
- `ENV_`는 사용자 입력이 아니라 스킬 실행에 필요한 도구, 권한, CLI/MCP/read-write surface, 검증 명령 조건이다.
- `필수` 값은 `required` 또는 `optional`로 쓴다.
- `기본값`은 optional이면 실제 default를 쓰고, required이면 `없음` 또는 fast-fail 조건을 쓴다.
- `설명`은 한 줄 label이 아니라 의미, 필요한 이유, 없을 때 처리, 어떤 산출물/검증에 영향을 주는지를 설명한다.
- 변수가 필수인지 판단하기 어렵다면 optional로 숨기지 말고 “없으면 어떤 결정을 못 하는가”를 설명하고 required 여부를 정한다.
- final response는 실제 산출물을 `OUTPUT_` 변수와 대응시켜 보고해야 한다.

좋은 설명 예:

- `INPUT_SKILL_NAME`: 생성/수정할 스킬의 directory basename과 frontmatter `name`이다. 1-64자 lowercase hyphen slug여야 하며 없으면 target path와 validator 기준을 정할 수 없어 fast fail한다.

나쁜 설명 예:

- `INPUT_SKILL_NAME`: 스킬 이름.

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

`feedback/`로 뺄 것:

- 해당 스킬을 실제로 사용하다가 발생한 불만족 사건 raw log.
- `feedback-ai-logging-v2/references/file-format.md`와 호환되는 one incident one file Markdown.
- 개별 스킬 개선 후보와 `skill-creator-for-stark` 개선 후보를 분리할 수 있는 evidence.

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

## 실패 보고와 갱신 규칙

스킬 생성/수정/품질 검증 중 실패가 발생하면 실패 단위를 숨기지 않고 다음을 분리해 보고한다.

- 실패한 command/API/tool/subagent.
- 기대 결과와 실제 error 또는 점수.
- likely cause.
- impact.
- recovery action과 재시도 조건.

다음 조건에서는 skill package를 갱신 대상으로 본다.

- canonical rubric, validator, template, mode 정책이 바뀐다.
- 문서에 적힌 path나 command가 live repo에서 더 이상 유효하지 않다.
- 사용자 고정 규칙과 충돌하는 오래된 지시가 발견된다.
- 95점 품질 평가에서 반복적으로 같은 dimension issue가 나온다.

## 흔한 실패 패턴

- `SKILL.md`가 너무 길어지고 references가 비어 있음.
- metadata가 너무 길어 항상 컨텍스트를 소모함.
- 입력과 출력이 prose에 섞여 있어 추적 불가.
- 환경 준비 여부를 확인하지 않고 파일을 씀.
- trigger example 없이 description만 작성함.
- 반복 가능한 deterministic workflow를 매번 agent 판단으로 재작성하게 둠.
- 생성된 스킬에 사용 불만족을 남기는 `feedback/` 절차가 없어 개선 evidence가 흩어짐.
- subagent에게 초안 작성을 맡긴 뒤 parent 검증 없이 완료 처리.
- 영어 prose가 많이 남아 사용자의 한국어 문서 기준을 어김.
- 특정 에이전트 실행 환경이나 설치 방식에 불필요하게 종속됨.
- unrelated worktree changes를 함께 건드림.
