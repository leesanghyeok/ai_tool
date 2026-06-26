---
name: skill-creator-for-stark
description: 사용자의 고정 규칙에 맞춰 범용 에이전트 스킬 패키지를 설계, 작성, 검증, 기록할 때 사용합니다.
version: 1.3.0
author: Agent
license: MIT
metadata:
  tags: [skills, authoring, workflow, verification, subagents]
  related_skills: [writing-plans, portable-skill-library-operations]
---

# Stark용 스킬 생성기 (Skill Creator for Stark)

## 개요

이 스킬은 사용자의 기준에 맞는 재사용 가능한 범용 에이전트 스킬 패키지를 만들 때 사용한다. 목표는 단순히 `SKILL.md` 하나를 쓰는 것이 아니라, 입력과 산출물을 과도하게 변수화하지 않고, 결과를 바꾸는 최소 계약만 드러내며, 세부 지식은 `references/`, 출력 형식과 산출물 skeleton은 `templates/`, 반복 가능한 deterministic 작업은 `scripts/`로 분리한 portable skill package를 만드는 것이다.

`SKILL.md`는 전체 workflow를 조율하는 orchestration 문서로 유지한다. 구체적인 작성 규칙, 하드 게이트, trigger 설계, subagent 분할 기준, 템플릿 세부사항은 linked support files를 참조한다.

## 사용 시점

다음 요청에 이 스킬을 사용한다.

- 새 범용 에이전트 스킬 패키지를 설계하거나 생성할 때.
- 기존 스킬을 사용자의 고정 규칙에 맞게 개선할 때.
- 스킬의 입력/출력 계약, 실행 전제, 출력 템플릿, 검증 checklist를 최소화하고 정리해야 할 때.
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

스킬 작성 전에 다음 입력을 표로 채운다. 모든 입력은 `필수`, `기본값`, `설명`을 가져야 한다. 설명은 변수의 의미, 필요한 이유, 없을 때의 처리 방식을 포함한다.

| 변수 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `INPUT_SKILL_GOAL` | required | 없음 | 만들거나 수정할 스킬이 해결해야 하는 문제와 최종 목적이다. 이 값이 없으면 스킬의 범위와 성공 기준을 정할 수 없으므로 fast fail한다. |
| `INPUT_TRIGGER_CONDITIONS` | required | 없음 | 새 스킬이 언제 사용되어야 하는지에 대한 사용자 요청, 상황, near-miss 경계다. description과 `should_trigger` / `should_not_trigger` 예시의 근거가 된다. |
| `INPUT_TARGET_USERS` | optional | `현재 사용자와 유사한 agent 사용자` | 스킬을 읽고 실행할 주 사용자 또는 사용 맥락이다. 특정 실행 환경이 아니라 사용자 수준, 팀 맥락, 도메인 숙련도를 설명한다. |
| `INPUT_REPO_ROOT` | required | 현재 작업 repository | 스킬 파일을 생성하거나 수정할 repository root다. 상대 경로 해석, git 검증, unrelated change 확인의 기준이 된다. |
| `INPUT_SKILL_ROOT` | required | `<INPUT_REPO_ROOT>/skills` | 스킬 디렉터리들이 위치한 root다. 존재하지 않으면 생성 승인이 필요하다. |
| `INPUT_SKILL_NAME` | required | 없음 | 생성/수정할 스킬의 directory basename과 frontmatter `name`이다. 1-64자 lowercase hyphen slug여야 한다. |
| `INPUT_CONSTRAINTS` | optional | 사용자 고정 규칙 + 현재 요청 | 반드시 지켜야 하는 언어, 형식, 승인, 보안, scope 제한이다. 없으면 현재 사용자 고정 규칙과 대화의 명시 요구를 기본으로 사용한다. |
| `INPUT_REFERENCE_MATERIALS` | optional | `[]` | 참고할 기존 스킬, 문서, 세션, 파일, repo artifact 목록이다. 참고 자료는 직접 의존성으로 넣기 전에 사용 목적을 구분한다. |
| `INPUT_APPROVAL_SCOPE` | required | 없음 | 파일 쓰기, overwrite, metadata 변경 등 사용자가 승인한 실행 범위다. 필요한 write 승인이 없으면 후보/계획만 보고한다. |
| `INPUT_OVERWRITE_POLICY` | optional | `abort_if_exists` | 대상 스킬이 이미 있을 때의 정책이다. `abort_if_exists`, `merge`, `patch`, `replace` 중 하나로 기록한다. |
| `INPUT_HISTORY_POLICY` | optional | `history/YYYYMMDD-<topic>.md` | 스킬 생성/개선 이력을 남길지와 경로 형식이다. 기본값은 lightweight history 기록을 남기는 것이다. |
| `INPUT_TRIGGER_EXAMPLE_POLICY` | optional | `canonical_trigger_section` | trigger 예시를 어디에 둘지 정한다. 기본값은 `사용 시점` 또는 `사용 판단` 안에 positive/negative/near-miss 예시를 통합하고, 긴 예시는 `history/`나 `references/`로 분리하는 것이다. |
| `INPUT_WORKFLOW_MODE` | required | 없음 | 현재 요청이 새 스킬 최초 생성(`create`), 기존 스킬 수정(`modify`), 파일 수정 없는 품질 검증 전용(`quality-review-only`) 중 무엇인지 나타낸다. 이 값으로 품질 루브릭 평가가 필수인지와 파일 write 가능 여부를 결정하므로 없으면 fast fail한다. |
| `INPUT_SKILL_QUALITY_RUBRIC_PATH` | optional | `/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md` | 스킬 품질 평가에 사용할 canonical rubric path다. 최초 생성과 검증 전용 모드에서는 반드시 읽어야 하며, 수정 모드에서는 평가가 필요한 경우 사용한다. |
| `INPUT_MIN_QUALITY_SCORE` | optional | `95` | `skill-creator-for-stark` workflow에서 완료로 인정할 최소 `certification_score`다. rubric 자체 baseline 90보다 엄격하며 최초 생성과 품질 검증 요청에서는 95점 미만을 실패로 보고한다. |
| `INPUT_QUALITY_EVALUATION_REQUIRED` | optional | mode별 기본값 | 품질 루브릭 평가가 필수인지 나타낸다. 기본값은 `create=true`, `modify=false`, `quality-review-only=true`이며, 수정 모드에서도 사용자가 품질/95점/릴리즈 가능 여부를 요구하거나 workflow·approval·verification·trigger를 크게 바꾸면 `true`로 승격한다. |
| `INPUT_QUALITY_EVALUATION_MODE` | optional | `clean_subagent` | 품질 평가 실행 방식이다. 기본은 `clean_subagent`이고, 긴 skill package나 high-stakes 평가는 `parallel_clean_subagents`, low-stakes quick check에서만 `same_context_exception`을 허용한다. |
| `INPUT_SKILL_FEEDBACK_LOGGING_POLICY` | optional | `skill-local-feedback-v2` | 생성/수정되는 스킬에 스킬 사용 불만족 feedback을 남기는 절차를 포함할지 정한다. 기본값은 public `INPUT_`/`OUTPUT_` 계약을 늘리지 않고, 짧은 workflow 절차나 reference link로 각 스킬 디렉터리 내부 `feedback/` raw log 방식을 설명하는 것이다. |

## 출력 변수

작업 결과는 다음 산출물 변수에 대응시켜 보고한다. 모든 출력은 `필수`, `기본값`, `설명`을 가져야 하며, 생성되지 않은 선택 산출물은 빈 배열이나 생략 사유로 보고한다.

| 변수 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `OUTPUT_SKILL_DIR` | required | 없음 | 생성/수정된 skill directory의 절대 경로다. 파일 쓰기를 하지 못했으면 계획상 target path와 미작성 사유를 함께 보고한다. |
| `OUTPUT_SKILL_MD` | required | 없음 | 생성/수정된 `SKILL.md` 경로다. read-back과 validator의 주 검증 대상이다. |
| `OUTPUT_REFERENCES` | optional | `[]` | 생성/수정된 `references/` 파일 목록이다. 긴 판단 기준, runbook, taxonomy, 사례가 없으면 빈 배열로 둔다. |
| `OUTPUT_TEMPLATES` | optional | `[]` | 생성/수정된 `templates/` 파일 목록이다. 반복 skeleton이나 출력 형식이 없으면 빈 배열로 둔다. |
| `OUTPUT_SCRIPTS` | optional | `[]` | 생성/수정된 `scripts/` 파일 목록이다. deterministic 반복 작업이 없거나 아직 분리하지 못했으면 이유를 보고한다. |
| `OUTPUT_HISTORY_RECORD` | optional | 없음 | 생성/수정 이력을 남긴 파일 경로다. `INPUT_HISTORY_POLICY=none`이면 생략 사유를 보고한다. |
| `OUTPUT_TRIGGER_EXAMPLES` | required | 없음 | `should_trigger` / `should_not_trigger` 예시 목록 또는 파일 경로다. 예시를 만들 수 없으면 부족한 입력을 `OUTPUT_OPEN_QUESTIONS`에 남긴다. |
| `OUTPUT_VERIFICATION_RESULT` | required | 없음 | validator, syntax check, `git diff --check`, read-back, ad-hoc verification의 실제 결과다. 검증하지 못한 항목은 `unverified`로 표시한다. |
| `OUTPUT_OPEN_QUESTIONS` | optional | `[]` | 승인, 경로, overwrite, reference 해석, runtime-independent 설계 등 미확인 사항이다. |
| `OUTPUT_WORKFLOW_MODE` | required | 없음 | 실제 적용한 workflow mode다. `create`, `modify`, `quality-review-only` 중 하나로 보고한다. |
| `OUTPUT_QUALITY_SCORECARD` | optional | 없음 | 품질 루브릭 평가를 실행한 경우 JSON scorecard 또는 저장 경로다. 실행하지 않았으면 생략 사유를 함께 보고한다. |
| `OUTPUT_QUALITY_CERTIFICATION` | optional | 없음 | `passed_95`, `failed_below_95`, `hard_gate_failed`, `blocked`, `unverified`, `skipped` 중 하나로 품질 판정을 요약한다. |
| `OUTPUT_QUALITY_FIXES` | optional | `[]` | 95점 미만이거나 hard gate 실패일 때 우선 수정해야 하는 path 단위 action 목록이다. |
| `OUTPUT_QUALITY_EVALUATION_SKIPPED_REASON` | optional | 없음 | `modify` 모드에서 품질 평가를 생략한 경우 생략 근거다. `create`와 `quality-review-only`에서는 사용할 수 없다. |
| `OUTPUT_NEXT_ACTIONS` | optional | `[]` | commit, 추가 review, 실제 sample run, 후속 skill patch 같은 다음 단계다. |
| `OUTPUT_SKILL_FEEDBACK_LOGGING_GUIDE` | required | 없음 | 생성/수정된 스킬에 포함된 feedback logging 절차 또는 생략 사유다. 기본 산출물은 `feedback-ai-logging-v2` 호환 포맷, `feedback/` 저장 위치, 중복 검사, 검증 방법을 설명하는 section 또는 reference link다. |

## 필수 환경

이 섹션의 `ENV_` 항목은 사용자 입력이 아니라 스킬이 실행되려면 필요한 도구, 권한, 명령, read/write surface 조건이다. 새 스킬 템플릿에도 같은 방식으로 작성한다.

| 환경 항목 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `ENV_FILESYSTEM_READ` | required | 현재 workspace 권한 | source skill, reference materials, 기존 target directory, validator script를 읽을 수 있어야 한다. 읽을 수 없으면 현재 상태 확인과 중복/overwrite 판단이 불가능하다. |
| `ENV_FILESYSTEM_WRITE` | required | 현재 workspace 권한 + `INPUT_APPROVAL_SCOPE` | 승인된 범위 안에서 target skill directory와 support files를 쓸 수 있어야 한다. 쓰기 승인이 없으면 파일 생성 없이 계획만 보고한다. |
| `ENV_VALIDATOR_COMMAND` | required | `python3 scripts/validate-skill-package.py` | 생성된 skill package의 frontmatter, 변수 표, hard gate, support links를 deterministic하게 검증하는 명령이다. 없으면 대체 검증을 명시한다. |
| `ENV_GIT_COMMAND` | optional | `git` | `git diff --check`, `git status --short`, unrelated changes 확인에 사용한다. git repo가 아니면 생략 사유를 보고한다. |
| `ENV_LOOKUP_TOOLS` | optional | 현재 사용 가능한 read/search 도구 | reference material, 기존 유사 스킬, session history를 읽기 위한 read-only 도구다. 없으면 사용자가 제공한 자료와 파일 시스템만 사용한다. |
| `ENV_SKILL_QUALITY_RUBRIC_READ` | required | `/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md` 읽기 권한 | 최초 생성과 품질 검증 전용 모드, 그리고 품질 평가가 필요한 수정 모드에서 canonical rubric을 read-back할 수 있어야 한다. 읽을 수 없으면 95점 통과 여부를 주장할 수 없다. |
| `ENV_CLEAN_JUDGE_AVAILABLE` | optional | 현재 agent/subagent 도구 | clean context 품질 평가에 사용할 subagent 또는 동등한 judge surface다. 없으면 `same_context_exception`으로 낮출 수 있지만 contamination risk를 scorecard에 기록해야 한다. |
| `ENV_SCORECARD_PARSE_CHECK` | required | JSON parse 가능 runtime | 품질 평가 결과가 rubric schema에 맞는 JSON scorecard인지 parse하고 `raw_total_score`, `certification_score`, D1-D5 hard gate, cap 적용을 확인할 수 있어야 한다. |
| `ENV_FEEDBACK_LOG_FORMAT_REFERENCE` | required | `feedback-ai-logging-v2/references/file-format.md` | 생성되는 스킬의 feedback logging 절차가 따라야 할 raw Markdown 포맷과 body-only `sha256` 기준이다. 접근할 수 없으면 `references/skill-feedback-logging-rules.md`의 호환 포맷을 사용하되 미확인으로 표시한다. |

## 하드 게이트 (Hard Gates)

이 섹션은 creator 자신이 지키는 package-level gate다. 생성되는 개별 스킬의 `Hard Gates`에는 아래 항목을 그대로 복사하지 말고, 해당 스킬의 산출물 품질·안전성에 직접 영향을 주는 domain-specific gate만 작성한다.

- Metadata gate: `name` + `description`은 항상 컨텍스트에 들어간다고 보고 짧게 유지한다.
  - `name`: 1-64자, lowercase hyphen slug, directory basename과 일치.
  - `description`: 1-1024자, 가능하면 약 100 words 이하, trigger condition과 주요 near-miss를 압축적으로 설명.
- `SKILL.md` body gate: trigger 시 로드된다고 보고 5,000 words 이하로 유지한다.
- Support file gate: `references/`, `templates/`, `scripts/`, `assets/`, `history/`, `feedback/` 외 임의 디렉터리를 만들지 않는다.
- Contract minimalism gate: 생성 스킬의 `INPUT_`는 사용자 결정이 필요하고 결과를 바꾸는 값만, `OUTPUT_`는 완료·검증·후속 승인 판단에 필요한 값만 남긴다. 안정적 default, 내부 정책, 보고 문장 조각은 변수로 승격하지 않는다.
- Environment clarity gate: 생성 스킬의 `ENV_`는 사용자 입력이 아니라 실행 전제다. 실패 시 workflow가 달라지거나 fast-fail해야 하는 항목만 표로 두고, 단순 권장 도구는 prose checklist로 낮춘다.
- Domain-specific hard gate: 생성 스킬의 `Hard Gates`에는 산출물 불변 조건, idempotency, evidence completeness, safety boundary처럼 그 스킬 실행 결과를 직접 좌우하는 기준만 둔다. `Metadata gate`, `Body size gate`, `directory basename` 같은 범용 package 규칙은 validator/checklist에 둔다.
- Trigger de-duplication gate: trigger 판단은 하나의 canonical section에 둔다. `사용 시점`, `사용하지 말아야 할 때`, `Trigger Examples`가 같은 판단을 반복하면 실패로 본다.
- Template placement gate: 직접 생성할 파일의 skeleton, frontmatter/body 구조, copyable output 형식은 `templates/`에 둔다. `references/`에는 판단 기준, taxonomy, routing, incident selection, runbook만 둔다.
- Deterministic workflow gate: 반복 가능하고 입력/출력이 명확한 작업은 가능한 한 `scripts/`로 분리한다.
- Skill feedback logging gate: 생성/수정되는 모든 스킬은 사용 중 불만족 사건을 해당 스킬 디렉터리 내부 `feedback/`에 raw log로 남기는 짧은 절차를 포함해야 한다. public `INPUT_`/`OUTPUT_` 계약을 늘리는 방식은 피한다.
- Skill quality rubric gate: `INPUT_WORKFLOW_MODE=create`에서는 `/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md` 평가가 필수이며 `certification_score >= 95`와 D1-D5 hard gate 통과 전에는 완료로 보고하지 않는다. `modify`에서는 선택이지만 workflow, approval, verification, trigger, scope, template, validator를 크게 바꾸면 필수로 승격한다.

## 빠른 중단 조건 (Fast Fail)

다음 조건에서는 즉시 중단하고 사용자에게 필요한 입력이나 승인을 요청한다.

- `INPUT_SKILL_NAME`이 없거나 lowercase hyphen slug가 아니다.
- `INPUT_SKILL_ROOT`가 없고 새 root 생성 승인이 없다.
- file write, metadata write, destructive overwrite 중 필요한 승인이 없다.
- 대상 skill directory가 이미 존재하지만 `INPUT_OVERWRITE_POLICY`가 없다.
- 기존 사용자 변경이 있는데 덮어써야만 진행 가능한 상황이다.
- validator script를 만들기로 했지만 실행 가능한 명령이 없다.
- 사용자가 `SKILL.md`에 긴 세부 자료를 모두 넣으라고 요구해 orchestration-only 원칙과 충돌한다.
- 외부 배포, 자동 설치, registry publish, credential 사용이 필요하지만 별도 승인이 없다.
- `INPUT_WORKFLOW_MODE`가 `create`, `modify`, `quality-review-only` 중 하나로 확정되지 않았다.
- `create` 또는 `quality-review-only`인데 skill quality rubric을 읽을 수 없거나 JSON scorecard parse 방법이 없다.
- `create`에서 품질 평가 결과가 `certification_score < 95`이거나 D1-D5 hard gate가 실패했는데 완료 보고를 해야 하는 상황이다.
- `quality-review-only` 요청인데 target skill 또는 rubric을 수정해야만 진행 가능한 상황이다.

## 작업 절차 (Workflow)

1. **입력 정리와 mode 확정**
   - 사용자 요청과 live repo 상태에서 `INPUT_` 변수를 채운다.
   - `INPUT_WORKFLOW_MODE`를 `create`, `modify`, `quality-review-only` 중 하나로 확정한다.
   - 추정값은 `추정`, tool로 확인한 값은 `확인됨`, 확인 불가 값은 `미확인`으로 구분한다.

2. **환경 확인**
   - `ENV_` 항목을 확인한다.
   - `create`와 `quality-review-only`에서는 skill quality rubric read-back과 scorecard parse 가능 여부를 반드시 확인한다.
   - fast-fail 조건을 먼저 적용한다.

3. **작업 분해**
   - 산출물을 `SKILL.md`, `references`, `templates`, `scripts`, `history`, `verification`, `quality_scorecard`로 나눈다.
   - dependency graph를 만들고 독립 가능한 구간을 subagent 병렬 작업 후보로 표시한다.

4. **Contract triage**
   - 생성 스킬에 넣을 `INPUT_`, `OUTPUT_`, `ENV_` 후보를 먼저 줄인다.
   - `INPUT_` 후보는 사용자가 실제로 제공해야 하는지, 값이 바뀌면 산출물·검증·안전 경계가 달라지는지, 안정적 default나 내부 정책으로 처리할 수 없는지 확인한다.
   - `OUTPUT_` 후보는 완료 여부, 생성/수정 파일, skip/blocker, 검증 결과, 다음 승인점 판단에 필요한 값인지 확인한다.
   - `ENV_` 후보는 사용자 입력이 아니라 실행 전제이며, 없을 때 fast-fail하거나 workflow가 달라지는 경우만 남긴다.
   - 최종 보고 문장 조각, 안정적 기본값, creator 내부 정책은 public variable table로 승격하지 않는다.

5. **하드 게이트 설계**
   - creator/package-level gate와 generated-skill domain gate를 분리한다.
   - 생성 스킬의 `Hard Gates`에는 해당 산출물의 불변 조건, evidence completeness, idempotency, validation, safety boundary처럼 실행 결과를 직접 좌우하는 기준만 둔다.
   - metadata, body size, support directory 같은 범용 package 규칙은 generated skill의 `Hard Gates`에 복사하지 않고 validator/checklist에 둔다.
   - `create`에서는 skill quality rubric gate를 필수 완료 조건으로 추가한다.
   - `modify`에서는 품질 평가가 필요한 변경인지 판단하고, 생략하면 `OUTPUT_QUALITY_EVALUATION_SKIPPED_REASON`에 근거를 남긴다.

6. **Trigger 판단 통합**
   - trigger 판단은 `사용 시점` 또는 `사용 판단` 하나의 canonical section에 통합한다.
   - positive, negative, near-miss 예시는 그 section 안에 짧게 두거나 긴 경우 `history/` 또는 `references/`로 분리한다.
   - `사용 시점`, `사용하지 말아야 할 때`, `Trigger Examples`가 같은 판단을 반복하지 않게 한다.
   - 상세 기준은 `references/trigger-history-rules.md`를 따른다.

7. **Subagent 병렬 초안 작성**
   - 독립 초안, 도메인 조사, 검토, 검증 checklist 확장은 subagent에 병렬 위임한다.
   - subagent prompt에는 반드시 `INPUT_`, `OUTPUT_`, `ENV_`, mode, 한글 작성, references 분리 규칙을 포함한다.
   - 상세 패턴은 `references/subagent-parallelization-patterns.md`를 따른다.

8. **Parent 통합**
   - parent agent가 subagent 결과를 직접 검증하고 통합한다.
   - subagent self-report만으로 완료를 주장하지 않는다.

9. **파일 작성 또는 read-only 평가**
   - `create`와 승인된 `modify`에서는 `SKILL.md`를 workflow 중심으로 작성한다.
   - 세부 기준은 `references/`, 재사용 skeleton은 `templates/`, deterministic 반복 작업은 `scripts/`, 생성/개선 기록은 `history/`에 둔다.
   - `quality-review-only`에서는 target skill과 rubric을 읽기만 하고 파일을 수정하지 않는다.
   - deterministic workflow 분리 기준은 `references/deterministic-workflow-rules.md`를 따른다.
   - 작성 규칙은 `references/skill-authoring-rules.md`를 따른다.

10. **History 기록**
   - `create`와 의미 있는 `modify`에서는 간단한 이력을 남긴다.
   - 기록에는 날짜, mode, 목표, 주요 변경, trigger 예시, 구조 검증 결과, 품질 평가 실행 여부와 남은 문제를 포함한다.
   - `quality-review-only`에서는 별도 승인 없이 history나 scorecard 파일을 쓰지 않는다.

11. **구조 검증**
    - `Verification Checklist`를 적용한다.
    - validator, `git diff --check`, `git status --short`, 대표 파일 read-back을 수행한다.

12. **스킬 feedback logging 절차 확인**
    - 생성/수정되는 스킬에 스킬 사용 불만족을 감지하고 `feedback/`에 raw log를 남기는 절차가 포함됐는지 확인한다.
    - 포맷과 운영 기준은 `references/skill-feedback-logging-rules.md`와 `feedback-ai-logging-v2/references/file-format.md`를 따른다.
    - feedback logging 절차가 빠졌다면 template/reference/validator를 먼저 보완하고, 생략 시에는 `OUTPUT_SKILL_FEEDBACK_LOGGING_GUIDE`에 사유를 보고한다.

13. **품질 루브릭 평가**
    - `create`: `/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md` 기준 평가를 반드시 수행한다. `certification_score >= 95`와 D1-D5 hard gate 통과 전에는 완료로 보고하지 않는다.
    - `modify`: 평가가 선택 사항이다. 단, 사용자가 품질 검증/95점/릴리즈 가능 여부를 요구하거나 workflow, approval, verification, trigger, scope, template, validator를 크게 바꾸면 필수로 수행한다.
    - `quality-review-only`: 파일 수정 없이 read-only로 평가 packet을 만들고 JSON scorecard를 parse한다.
    - 세부 절차는 `references/skill-quality-rubric-evaluation.md`를 따른다.
    - scorecard JSON은 가능하면 `scripts/validate-quality-scorecard.py`로 점수 합계, D1-D5 hard gate, 95점 기준을 parse 검증한다.

14. **템플릿 기반 보고**
    - 최종 보고는 `templates/skill-output-template.md` 구조를 따른다.
    - 품질 평가를 실행한 경우 score, hard gate, scorecard, fixes를 보고한다.
    - `modify`에서 품질 평가를 생략한 경우 생략 사유를 보고한다.

## Subagent 병렬화

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

## 보안과 프라이버시

- API key, token, cookie, password, private URL, credential은 raw evidence나 history에 그대로 저장하지 않는다.
- 품질 평가 packet을 만들 때 secret 의심 문자열은 redaction 필요 여부를 먼저 확인하고, 필요하면 `redacted`로 대체한다.
- 외부 배포, registry publish, production mutation, credential 사용은 `INPUT_APPROVAL_SCOPE`에 명시 승인된 경우에만 수행한다.
- `quality-review-only` mode에서는 target skill, rubric, scorecard, history를 쓰지 않으며, 사용자가 저장을 승인한 경우에도 지정 경로에만 저장한다.
- 실패 보고에는 민감정보 원문을 넣지 않고 `actual_error`에서도 secret-like token은 축약하거나 마스킹한다.

## Trigger 예시 운영

이 creator 자체의 trigger는 위 `사용 시점`과 `사용하지 말아야 할 때`가 canonical 기준이다. 생성되는 스킬에는 같은 판단을 여러 section에 반복하지 않는다. 예시가 필요하면 canonical trigger section 안에 다음처럼 짧게 둔다.

- 사용: "새 스킬 패키지를 하나 만들어줘. 입력/출력 계약과 검증까지 포함해야 해."
- 사용: "이 기존 스킬을 사용자 기준에 맞게 개선하고 95점 이상인지 확인해줘."
- 사용 안 함: "이 문장만 자연스럽게 다듬어줘." — 재사용 가능한 skill package 작성이나 검증이 아니다.
- 사용 안 함: "GitHub PR을 리뷰해줘." — PR review 전용 workflow가 더 적합하다.

## 실패 보고 형식

검증, 품질 평가, 파일 작성이 실패하면 최종 보고에 다음 필드를 채운다.

| 필드 | 설명 |
|---|---|
| `failed_command_or_tool` | 실패한 command, API, tool, subagent, validator 이름이다. |
| `expected_result` | 기대한 통과 조건 또는 출력이다. |
| `actual_error` | 실제 error, exit code, score, blocker다. |
| `likely_cause` | 확인된 원인 또는 근거 있는 추정 원인이다. |
| `impact` | 완료 주장, 품질 통과, 파일 안전성에 미치는 영향이다. |
| `recovery_action` | 다음 복구 행동, 재시도 조건, 대체 경로다. |
| `status_class` | `blocked`, `partial`, `unverified`, `failed`, `recovered` 중 현재 상태다. |
| `retry_condition` | 같은 방법으로 재시도해도 되는 조건과 재시도하지 말아야 할 조건이다. |
| `alternative_path` | 재시도가 부적절할 때 사용할 대체 도구, 수동 확인, 축소 scope다. |

## 갱신 정책

- `/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md`가 변경되면 이 스킬의 품질 평가 절차와 scorecard template을 재검토한다.
- validator, template, mode 정책을 바꾸면 `modify`라도 품질 루브릭 평가를 실행한다.
- 오래된 path, 실행 불가능한 command, 사용자 기준과 충돌하는 규칙을 발견하면 해당 support file을 patch하고 validator를 다시 실행한다.
- 버전은 workflow, gate, output schema가 바뀌면 minor 이상으로 올리고, 단순 문구 수정은 patch 수준으로 기록한다.

## 커밋 주의사항 (Commit Pitfalls)

- unrelated worktree changes를 함께 commit하지 않는다.
- auto-sync 또는 background process가 이미 commit했을 수 있으므로 `git status`만 보지 말고 필요하면 `git log -- <path>`를 확인한다.
- 검증 실패 상태를 commit하지 않는다.
- 기존 스킬 rename/move는 git에서 delete+create처럼 보일 수 있으므로 diff를 확인한다.
- generated artifact와 source skill package를 섞지 않는다.
- 스킬 파일 생성과 현재 세션의 즉시 사용 가능 여부를 혼동하지 않는다.

## 검증 체크리스트 (Verification Checklist)

- [ ] `SKILL.md`가 존재한다.
- [ ] YAML frontmatter가 존재하고 필수 key가 있다.
- [ ] `name`이 directory basename과 일치한다.
- [ ] `name`이 1-64자 lowercase hyphen slug다.
- [ ] `description`이 사용 시점을 설명하고 1024자 이하이며 가능하면 약 100 words 이하다.
- [ ] `SKILL.md` body가 5,000 words 이하이고 orchestration 중심이다.
- [ ] `INPUT_`, `OUTPUT_`, `ENV_` table이 있고 각 항목에 필수/기본값/설명이 있다.
- [ ] `INPUT_`는 사용자 결정과 결과 차이에 필요한 값만 남겼다.
- [ ] `OUTPUT_`는 완료·검증·후속 승인 판단에 필요한 값만 남겼다.
- [ ] `ENV_`가 사용자 입력이 아니라 필요한 도구/권한/명령 조건으로 설명되어 있다.
- [ ] 하드 게이트 섹션이 generated skill의 domain-specific gate와 creator package gate를 혼동하지 않는다.
- [ ] 출력 템플릿이 있다.
- [ ] 커밋 주의사항 섹션이 있다.
- [ ] 검증 체크리스트 섹션이 있다.
- [ ] 병렬 처리 가능한 subagent 구간이 정의되어 있다.
- [ ] 세부 기준은 references/templates/scripts/history로 분리되어 있다.
- [ ] 스킬 사용 불만족을 `feedback/`에 raw log로 남기는 절차가 포함되어 있다.
- [ ] 가능한 deterministic workflow는 `scripts/`로 분리되어 있다.
- [ ] trigger 판단이 하나의 canonical section에 있으며 중복 section을 만들지 않았다.
- [ ] `INPUT_WORKFLOW_MODE`가 확정됐고 mode별 품질 평가 필수 여부가 보고됐다.
- [ ] `create`에서는 `skill-quality-rubric-v1.md` 평가 결과 `certification_score >= 95`이고 D1-D5 hard gate가 모두 통과했다.
- [ ] `modify`에서는 품질 평가를 실행했거나 생략 사유가 보고됐다.
- [ ] `quality-review-only`에서는 파일 수정 없이 JSON scorecard를 parse했다.
- [ ] validator script가 있다면 통과한다.
- [ ] `git diff --check`가 통과한다.
- [ ] 최종 보고가 `OUTPUT_` 변수와 대응된다.

## 최종 응답 체크리스트 (Final Response Checklist)

최종 응답에는 다음을 포함한다.

- `INPUT_` 요약.
- `OUTPUT_` 산출물 경로.
- feedback logging 절차 포함 여부와 `feedback/` 저장 기준.
- 수행한 검증과 실제 결과.
- 품질 루브릭 평가 결과 또는 생략 사유.
- 의도적으로 남긴 영어 identifier.
- 미확인 사항.
- commit 여부와 다음 단계.
