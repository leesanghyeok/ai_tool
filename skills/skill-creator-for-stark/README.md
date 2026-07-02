# skill-creator-for-stark

`skill-creator-for-stark`는 Stark 기준의 portable agent skill package를 설계, 생성, 개선, migration, 검증하도록 돕는 스킬이다. README는 사용자가 맡길 수 있는 일과 eval 활용 방식을 빠르게 파악하기 위한 안내서이며, 세부 workflow와 내부 규칙은 [`SKILL.md`](SKILL.md), [`references/`](references/), [`templates/`](templates/), [`scripts/`](scripts/), [`evals/`](evals/)를 따른다.

## 이 스킬로 할 수 있는 일

- 새 스킬 패키지를 `SKILL.md`, `references/`, `templates/`, `scripts/`, `evals/`, `history/`, `feedback/` 구조로 설계하고 생성한다.
- 기존 스킬의 trigger, 입력/출력 계약, hard gate, support files, validator, eval suite를 Stark 기준에 맞게 개선한다.
- legacy 또는 비표준 스킬 흐름을 Stark 포맷으로 migration하면서 원래 목적, trigger, workflow를 보존한다.
- case-based eval suite와 package validator를 포함해 반복 검증 가능한 스킬 패키지로 정리한다.
- 사용 중 불만족 사건을 `feedback/`에 안전하게 기록하는 절차를 포함한다.
- `create`, `modify`, `quality-review-only` mode에 따라 파일 작성, 보존, read-only 평가 경계를 분리한다.

이 스킬은 외부 registry publish, 자동 설치, credential 사용, production mutation을 기본 목표로 하지 않는다. 그런 작업은 별도 승인과 별도 절차가 필요하다.

## 대표 사용자 시나리오

| 시나리오 | 사용자가 기대하는 결과 | 주로 확인하는 것 |
|---|---|---|
| 새 스킬 만들기 | 새 `<skill-name>/SKILL.md`와 support files skeleton | 목적, trigger, 최소 `INPUT_`/`OUTPUT_`, domain-specific hard gate, eval skeleton |
| 기존 스킬 최소 수정 | 기존 계약을 보존하면서 필요한 파일만 patch | 기존 workflow 보존, 승인 범위, 회귀 방지, read-back |
| 기존 workflow migration | legacy 흐름을 Stark package 구조로 이전 | 원본 trigger/workflow 보존, create-path equivalence, 불확실성 표시 |
| 품질 검토만 수행 | target skill과 rubric을 수정하지 않는 평가 결과 | hard gate, scorecard parse 가능성, 개선 제안, 미검증 항목 |
| eval suite 보강/점검 | `evals/<skill>.eval.yaml`, `evals/<case-id>/case.yaml`, runner 검증 | case type, expected baseline, `command`/`llm-judge` 책임 분리 |

## 주요 기능 맵

- `SKILL.md`: agent가 로드하는 orchestration 문서다. 사용 시점, 입력/출력/환경 계약, hard gate, workflow, 완료 보고 기준을 담는다.
- `references/`: 작성 규칙, eval authoring rules, 품질 루브릭 평가, feedback logging, trigger/history, deterministic workflow 같은 판단 기준을 둔다.
- `templates/`: `SKILL.template.md`, `eval-spec.template.md`, `skill-output-template.md`, `feedback-log.template.md`처럼 복사 가능한 skeleton을 둔다.
- `scripts/`: deterministic 검증과 반복 작업을 둔다. 주요 명령은 `scripts/run_evals.py`, `scripts/validators/validate-skill-package.py`, `scripts/run_pipeline.py`, `scripts/run_llm_judge.py`, `scripts/validators/validate-pipeline.py`, `scripts/run_evals.py`다.
- `evals/`: `evals/skill-creator-for-stark.eval.yaml`와 declared `case.yaml` file(`evals/<case-id>/case.yaml`)로 case-based regression/evaluation contract를 관리한다.
- `history/`: 의미 있는 변경 이력과 이전 migration 기록을 보관한다.
- `feedback/`: 생성/수정되는 스킬에 포함할 사용자 불만족 사건 기록 절차의 대상 디렉터리다.

## Eval 방식 가이드

`skill-creator-for-stark`는 case-based eval suite를 기본 단위로 본다. `eval.yaml` suite file은 `evals/<skill>.eval.yaml`, 각 `case.yaml`은 `evals/<case-id>/case.yaml`에 둔다. 사용자는 runner 내부 구현을 이해하기보다 “무엇을 deterministic하게 검증할지”와 “무엇을 의미 판단으로 남길지”를 먼저 정하면 된다.

### case type 의미

- `happy-path`: 대표 성공 경로를 검증한다. 예: 새 스킬 생성 시 기본 package skeleton이 만들어지는지 확인한다.
- `integration`: 여러 파일, 단계, 보존 조건이 함께 맞아야 하는 흐름을 검증한다. 예: 기존 스킬 수정에서 feedback logging과 `eval.yaml`이 함께 생기는지 확인한다.
- `regression`: 이미 보장한 동작이 깨지지 않았는지 확인한다. 예: package validator, runner regression, 계약 문서 정합성.
- `safety`: 승인, credential, destructive action, no-invention 같은 안전 경계를 검증한다.
- `edge`: 예상 가능한 경계 조건이나 예외 입력을 검증한다.
- `llm-judge`: 정적 검사나 byte 비교만으로 부족한 의미 품질을 subprocess-backed judge로 확인한다.

현재 creator 자체 `eval.yaml`에는 `07-validate-package`, `08-runner-regression`, `06-eval-contract`, `02-create-skill`, `01-create-skill-judge`, `04-modify-skill`, `03-modify-skill-judge`, `05-migrate-skill-judge`가 case entry로 등록되어 있다.

### `command` assertion과 `llm-judge` 책임 분리

- `command` assertion은 파일 존재, JSON/YAML shape, validator 통과, 특정 문자열/경로 확인처럼 결정론적으로 재실행 가능한 조건을 맡는다.
- `llm-judge`는 contract minimalism, approval boundary, no-invention, 원본 intent 보존, migration 품질처럼 의미 판단이 필요한 조건을 맡는다.
- `llm-judge` adapter의 canonical entrypoint는 `scripts/run_llm_judge.py output --input input.json --output primary-output.json`와 `scripts/run_llm_judge.py assertion --input assertion-input.json --output assertion-output.json`다. Migration 기간에는 기존 `scripts/run_llm_judge.py --input {judge_packet} --output {judge_output}` 호출도 `schema_version`/`prompt` public packet을 받는 자연어 assertion alias로 유지한다.
- `llm-judge`는 deterministic 검증을 대체하지 않는다. 파일 상태나 runner provenance처럼 명령으로 확인 가능한 내용은 `command` assertion 또는 별도 verify 단계로 확인해야 한다.

### `expected`와 `--promote` 승인 경계

- `expected` 파일은 “현재 output을 앞으로의 baseline으로 삼겠다”는 결정이다.
- `--promote`는 passing case의 actual output을 `expected`로 생성하거나 overwrite할 수 있으므로, 사용자가 expected baseline 갱신을 명시 승인한 경우에만 실행한다.
- 일반 README 수정, eval 구조 점검, runner 검증 중에는 `--promote`를 실행하지 않는다.
- expected가 없는 case는 byte equality baseline을 비교하지 않고, `command` assertion 또는 `llm-judge` 결과로 통과 여부를 판단한다.

### 대표 명령

```bash
cd /Users/stark/project/jarvis/ai_tool/skills/skill-creator-for-stark
make check
make lint
make complexity-check
make test
git -C /Users/stark/project/jarvis/ai_tool diff --check -- skills/skill-creator-for-stark
```

주의: standalone 검증은 `Makefile` target을 canonical entrypoint로 사용한다. 전체 검증은 `make check`, 부분 검증은 `make lint`, `make complexity-check`, `make test`를 사용한다. `run_evals.py` 옵션 이름은 `--validate`이며 `--validation`은 지원하지 않는다.

## 사용자가 준비하면 좋은 입력

작업 시작 전에 아래 정보를 준비하면 범위와 완료 기준을 빠르게 확정할 수 있다.

- `INPUT_SKILL_GOAL`: 만들거나 수정할 스킬의 목적, 핵심 workflow, 최종 산출물.
- `INPUT_TRIGGER_CONDITIONS`: 스킬을 언제 사용하고 언제 사용하지 않을지에 대한 task/action 중심 조건.
- `INPUT_REPO_ROOT`: 대상 repository root.
- `INPUT_SKILL_NAME`: skill directory basename이자 `SKILL.md` frontmatter `name`.
- `INPUT_APPROVAL_SCOPE`: 허용된 write, overwrite, metadata/history/scorecard 작성, external action 범위.
- `INPUT_WORKFLOW_MODE`: `create`, `modify`, `quality-review-only` 중 하나.
- 검증 기대 수준: package validator만 필요한지, `run_evals.py --validate`, `run_evals.py --json`, 품질 루브릭 평가까지 필요한지.
- migration 또는 modify 작업이라면 기존 파일에서 반드시 보존해야 하는 trigger, workflow, public contract, 사용자 변경 사항.

승인 범위가 없거나 mode가 불명확하면 스킬은 먼저 멈추고 확인해야 한다.

## 검증과 완료 기준

완료는 “파일을 썼다”가 아니라 “요구한 산출물을 read-back하고 검증 결과를 보고했다”로 판단한다.

- 생성/수정된 skill root와 주요 파일 경로를 보고한다.
- `SKILL.md`, `references/`, `templates/`, `scripts/`, `evals/`, `history/`, `feedback/` 중 실제로 생성/수정한 support files를 구분한다.
- package 구조는 `uv run python scripts/validators/validate-skill-package.py .` 또는 대상 skill root 인자로 검증한다.
- eval suite는 가능하면 `uv run python scripts/run_evals.py --validate`와 `uv run python scripts/run_evals.py --json`으로 확인한다.
- creator 자체의 runner/helper/test를 바꿨다면 `uv run python -m unittest discover -s scripts/tests -v`를 실행한다.
- whitespace와 patch 품질은 `git diff --check`로 확인한다.
- `create` mode는 `/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md` 기준 품질 평가가 필수이며, `certification_score >= 95`와 D1-D5 hard gate 통과 전에는 완료로 보지 않는다.
- `modify` mode에서 workflow, approval boundary, verification gate, trigger/scope, template/validator/eval contract를 크게 바꾸면 품질 평가를 실행하거나 생략 사유를 명시한다.
- `quality-review-only` mode에서는 target skill, rubric, scorecard, history를 수정하지 않는다.
- 자동 검증하지 못한 항목, `llm-judge` 판단 경계, 미확인 사항, commit 여부를 최종 보고에서 분리한다.

## 더 자세한 문서

- [`SKILL.md`](SKILL.md): 전체 workflow, hard gate, 입력/출력/환경 계약, 보안/프라이버시, 실패 보고 형식.
- [`references/skill-authoring-rules.md`](references/skill-authoring-rules.md): 스킬 작성 세부 규칙.
- [`references/skill-eval-authoring-rules.md`](references/skill-eval-authoring-rules.md): case-based eval suite 작성 규칙.
- [`references/eval-terminology-glossary.md`](references/eval-terminology-glossary.md): `eval.yaml`, `case.yaml`, `entries[]` 등 eval 용어 기준.
- [`references/skill-quality-rubric-evaluation.md`](references/skill-quality-rubric-evaluation.md): 품질 루브릭 평가 절차.
- [`references/skill-feedback-logging-rules.md`](references/skill-feedback-logging-rules.md): feedback logging 절차.
- [`templates/SKILL.template.md`](templates/SKILL.template.md): 새 스킬 `SKILL.md` skeleton.
- [`templates/eval-spec.template.md`](templates/eval-spec.template.md): eval suite skeleton.
- [`scripts/validators/validate-skill-package.py`](scripts/validators/validate-skill-package.py): package 구조 validator.
- [`scripts/run_evals.py`](scripts/run_evals.py): creator 자체 eval runner.
- [`scripts/run_evals.py`](scripts/run_evals.py): 생성되는 skill에 복사할 eval runner template.
- [`scripts/run_pipeline.py`](scripts/run_pipeline.py): creator 사용자 시나리오 command case의 deterministic template rendering entrypoint.
- [`scripts/run_llm_judge.py`](scripts/run_llm_judge.py): `llm-judge` output/assertion adapter. Canonical subcommand는 `output`/`assertion`이며, 기존 `--input {judge_packet} --output {judge_output}`는 migration alias다.
- [`scripts/validators/validate-pipeline.py`](scripts/validators/validate-pipeline.py): generated skill pipeline verifier.
