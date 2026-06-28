# skill-creator-for-stark 사용 가이드

`skill-creator-for-stark`는 Stark 기준에 맞는 portable agent skill package를 만들거나 개선할 때 쓰는 스킬이다. 단순히 `SKILL.md`만 작성하지 않고, 판단 기준은 `references/`, 복사 가능한 skeleton은 `templates/`, 반복 가능한 검증은 `scripts/`, regression contract는 `evals/`로 나누는 것을 기본 원칙으로 한다.

## 언제 사용하나

사용한다:

- 새 범용 agent skill package를 만들 때.
- 기존 skill을 Stark 기준에 맞게 수정할 때.
- skill의 입력/출력 계약, trigger, hard gate, 검증 절차를 정리할 때.
- skill package에 eval case, validator, feedback logging 절차를 포함해야 할 때.
- `references/`, `templates/`, `scripts/`, `evals/`, `history/`를 함께 다루는 복합 skill 작업일 때.

사용하지 않는다:

- 단순 문장 수정이나 일회성 설명만 필요한 경우.
- 이미 더 적합한 도메인 전용 skill이 있는 경우.
- 사용자가 파일 쓰기나 repo metadata 변경을 승인하지 않은 경우.
- 외부 배포, registry publish, credential 사용이 주목적인 경우.

## 입력으로 준비할 것

작업을 시작할 때 최소한 다음을 정한다.

- `INPUT_SKILL_GOAL`: 만들거나 수정할 skill의 목적과 최종 산출물.
- `INPUT_TRIGGER_CONDITIONS`: 이 skill을 언제 사용하고 언제 사용하지 않을지.
- `INPUT_REPO_ROOT`: 대상 repository root.
- `INPUT_SKILL_NAME`: skill directory basename이자 frontmatter `name`.
- `INPUT_APPROVAL_SCOPE`: 승인된 write, overwrite, history/scorecard 작성 범위.
- `INPUT_WORKFLOW_MODE`: `create`, `modify`, `quality-review-only` 중 하나.

승인 범위가 없거나 mode가 불명확하면 먼저 멈추고 확인한다.

## 기본 workflow

1. mode와 승인 범위를 확정한다.
2. 기존 skill, support files, validator, rubric을 read-back한다.
3. public `INPUT_`, `OUTPUT_`, `ENV_` table을 최소화한다.
4. trigger 판단은 한 canonical section에 모은다.
5. generated skill의 `Hard Gates`에는 domain-specific gate만 둔다.
6. 자세한 판단 기준은 `references/`로 분리한다.
7. skeleton, frontmatter/body 구조, 보고 템플릿은 `templates/`로 분리한다.
8. deterministic 반복 작업은 `scripts/`로 분리한다.
9. 생성/수정되는 skill에는 가능한 한 `evals/<skill-name>.eval.md`와 `scripts/run_evals.py`를 포함한다.
10. validator, eval, tests, `git diff --check`, read-back으로 검증한다.
11. 의미 있는 변경은 `history/`에 짧게 남긴다.
12. 최종 보고에는 산출물 경로, 검증 결과, 미검증 항목, commit 여부를 분리해 적는다.

## package 구조

권장 구조:

```text
<skill-name>/
  SKILL.md
  README.md
  references/
  templates/
  scripts/
  evals/
    <skill-name>.eval.md
    golden/
  history/
  feedback/
```

허용 support directory는 `references/`, `templates/`, `scripts/`, `assets/`, `history/`, `feedback/`, `evals/`다.

## 자체 검증 명령

이 skill package 자체를 수정했다면 skill root에서 다음을 실행한다.

```bash
cd /Users/stark/project/jarvis/ai_tool/skills/skill-creator-for-stark
python3 scripts/run_evals.py --validate
python3 scripts/run_evals.py --json
python3.11 -m unittest discover -s scripts/tests -v
python3 scripts/validate-skill-package.py .
git -C /Users/stark/project/jarvis/ai_tool diff --check -- skills/skill-creator-for-stark
```

주의:

- `/usr/bin/python3`는 Python 3.9일 수 있어 `Path | None` syntax가 있는 test/helper 실행에 부적합하다. 가져온 regression tests는 `python3.11`로 실행한다.
- `creator-workflow-contract`는 `llm-judge` criterion이다. `run_evals.py`가 checklist로 출력할 뿐 자동 채점 완료로 보지 않는다.
- 현재 creator 자체 golden cases는 `pending-first-green` 상태다.
- `--promote`는 expected baseline 파일을 쓰므로 별도 승인 전에는 실행하지 않는다.

## 자체 eval case

`evals/skill-creator-for-stark.eval.md`는 creator 자체의 regression contract다.

현재 golden cases:

- `create-new-skill`: 새 skill package 생성 시 eval spec, runner, quality gate가 포함되는지 확인한다.
- `modify-existing-skill`: 기존 skill 수정 시 eval 보존/갱신과 검증 절차가 유지되는지 확인한다.
- `quality-review-only`: read-only 품질 검토에서 파일을 쓰지 않고 scorecard/검증 가능성만 보고하는지 확인한다.

현재 command criteria:

- `package-validator-pass`
- `eval-runner-validate-pass`
- `upstream-regression-tests-pass`

현재 checklist criterion:

- `creator-workflow-contract` (`llm-judge`)

## 가져온 regression tests

`/Users/stark/practice/agent-skill-creator/scripts/tests`에서 필요한 테스트를 가져와 `scripts/tests/` 아래에서 관리한다.

현재 포함된 테스트:

- `scripts/tests/test_run_evals.py`
- `scripts/tests/test_check_pipeline.py`

운영 규칙:

- 복사해온 영어 주석과 docstring은 한국어로 번역한다.
- Python identifier, command, fixture string, assertion 대상 error token은 원문을 보존한다.
- local import 기준은 `SCRIPTS_DIR = Path(__file__).parent.parent`다.
- upstream과 local error message가 다르면 behavior intent를 유지하는 token assertion으로 조정한다.

## 품질 평가

`create` mode에서는 `/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md` 기준 품질 평가가 필수다.

완료 조건:

- `certification_score >= 95`
- D1-D5 hard gate 통과
- scorecard JSON parse 검증 가능

`modify` mode에서는 선택이지만 다음을 바꾸면 품질 평가를 실행한다.

- workflow
- approval boundary
- verification gate
- trigger/scope
- template/validator/eval contract

`quality-review-only` mode에서는 target skill과 rubric을 수정하지 않는다.

## feedback logging

생성/수정되는 skill에는 사용 중 불만족 사건을 해당 skill directory 내부 `feedback/`에 raw log로 남기는 절차를 포함한다.

기준:

- public `INPUT_`/`OUTPUT_` 계약을 늘려서 해결하지 않는다.
- 사건별 raw log는 source evidence와 사용자 발화를 보존한다.
- secret, token, cookie, password, private URL은 원문 저장하지 않는다.

## 완료 보고 형식

최종 보고에는 최소한 다음을 포함한다.

- 변경한 skill directory와 주요 파일 경로.
- mode와 승인 범위.
- 생성/수정한 support files.
- 실행한 검증 command와 실제 결과.
- 품질 루브릭 평가 결과 또는 생략 사유.
- `llm-judge` 등 자동 검증하지 않은 항목.
- 미확인 항목.
- commit 여부.

## 관련 주요 파일

- `SKILL.md`: agent가 load하는 orchestration 문서.
- `references/skill-authoring-rules.md`: skill 작성 세부 규칙.
- `references/skill-eval-authoring-rules.md`: eval spec 작성 규칙.
- `references/skill-quality-rubric-evaluation.md`: 품질 루브릭 평가 절차.
- `references/skill-feedback-logging-rules.md`: feedback logging 절차.
- `templates/SKILL.template.md`: 새 skill skeleton.
- `templates/eval-spec.template.md`: eval spec skeleton.
- `scripts/validate-skill-package.py`: package 구조 validator.
- `scripts/run_evals.py`: creator 자체 eval runner.
- `scripts/run_evals_template.py`: 생성되는 skill에 복사할 eval runner template.
- `scripts/check_pipeline.py`: generated skill pipeline verifier.
