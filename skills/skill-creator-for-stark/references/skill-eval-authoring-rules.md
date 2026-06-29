# 스킬 eval 작성 규칙

## 목적

생성되는 skill package가 처음부터 regression 가능한 test suite를 갖도록 case-based eval 모델을 사용한다. 이 모델은 모든 case에 같은 global criteria를 강제하지 않고, `eval.yaml`은 suite manifest와 human-readable test map 역할만 하며, 실제 실행과 검증은 각 `case.yaml`이 독립적으로 가진다.

## 기본 원칙

- eval generation은 기본값으로 켠다. 사용자가 명시적으로 원하지 않거나 skill이 eval에 부적합할 때만 생략한다.
- eval은 “더 좋아졌는가” 비교가 아니라 “의도한 대로 동작하는가”를 검증하는 test contract다.
- `evals/<skill-name>.eval.yaml`이 실행 source of truth다. `evals/cases/` 아래 case directory가 있어도 `eval.yaml`에 선언되지 않으면 실행하지 않고 validation error로 본다.
- `eval.yaml`에는 top-level `run.command`, `global_assertions`, `description`을 두지 않는다. `title`, `test_policy`, `cases`만 간결하게 둔다.
- 각 `case.yaml`은 `id`, `type`, `title`, optional `input`, optional `expected`, optional `run`, `assertions`를 가진다.
- assertion type은 `command`, `llm-judge` 두 개만 지원한다.
- `expected`가 있으면 runner가 자동으로 actual output과 byte equality 비교를 수행한다. `expected`가 없으면 비교하지 않는다.
- `--promote`는 expected 유무와 독립적이다. expected가 없으면 `expected.json`을 생성하고, 있으면 overwrite한다.
- `llm-judge`는 subprocess 기반 `run_llm_judge.py` contract로 실행한다. checklist/pending으로 남기지 않는다.

## Phase 2 — Case-based Eval Definition

SKILL.md를 쓰기 전에 다음을 정한다.

1. suite title과 case 목록을 정한다.
   - `eval.yaml`의 `cases`는 runner가 읽는 유일한 case 목록이다.
   - 각 case entry는 `id`, `type`, `title`, `path`를 가진다.
2. case별 실행 방식을 정한다.
   - non-`llm-judge` case는 `run.command`를 갖고 `{output}` placeholder를 포함해야 한다.
   - `type: llm-judge` case는 `run.command`를 갖지 않고, `llm-judge` assertion의 `judge.command`만 사용한다.
3. case별 assertion을 정한다.
   - deterministic check는 `command`로 작성한다.
   - 의미·품질 판단은 `llm-judge`로 작성한다.
   - 각 assertion은 `id`, `title`, `type`을 가진다.
4. `expected` 필요 여부를 정한다.
   - 예상 출력이 안정적이면 `expected` 파일을 둔다.
   - 안정적 baseline이 아직 없으면 `expected`를 생략하고, 필요할 때 `--promote`로 생성한다.

## Phase 5 — Eval emission

생성되는 skill 안에 다음 구조를 둔다.

```text
<skill>/
  scripts/run_pipeline.py        # 필요한 case에서만 호출
  scripts/run_evals.py           # scripts/run_evals_template.py 복사본
  scripts/run_llm_judge.py       # llm-judge assertion이 필요할 때
  evals/
    <skill-name>.eval.yaml       # suite manifest + human-readable test map
    cases/
      <case-id>/
        case.yaml
        input.*                  # optional
        expected.*               # optional
```

## `eval.yaml` 형식

```yaml
version: 1
skill: example-skill
title: example-skill eval suite

test_policy:
  expected_compare: auto
  llm_judge: required
  undeclared_cases: error
  promote: allow-overwrite

cases:
  - id: create-basic
    type: happy-path
    title: 기본 생성 workflow 검증
    path: cases/create-basic/case.yaml
  - id: judge-quality
    type: llm-judge
    title: 생성물 품질을 LLM judge로 검증
    path: cases/judge-quality/case.yaml
```

### `test_policy` 의미

| key | 값 | 의미 |
|---|---|---|
| `expected_compare` | `auto` | case에 `expected`가 있으면 runner가 자동으로 actual output과 byte equality 비교를 수행한다. |
| `llm_judge` | `required` | `llm-judge` assertion은 기본 실행에 포함되며 judge command 실패나 verdict fail은 case fail이다. |
| `undeclared_cases` | `error` | `evals/cases/*/case.yaml`이 있어도 `eval.yaml`에 없으면 validation error다. |
| `promote` | `allow-overwrite` | `--promote`가 있으면 expected가 없을 때 생성하고 이미 있으면 overwrite한다. |

## `case.yaml` 형식

```yaml
id: create-basic
type: happy-path
title: 기본 생성 workflow 검증

input: input.json
expected: expected.json

run:
  command: python3 scripts/run_pipeline.py --input {input} --output {output}
  timeout_sec: 120

assertions:
  - id: valid-json
    title: 출력이 JSON으로 parse되는지 검증
    type: command
    cmd: python3 -m json.tool {output}

  - id: package-shape
    title: 필수 스킬 패키지 파일이 생성됐는지 검증
    type: command
    cmd: python3 scripts/assert_package_shape.py --actual {output}
```

## Case type

초기 허용값:

- `happy-path`
- `edge`
- `regression`
- `safety`
- `llm-judge`
- `integration`

`type`은 case 목적을 사람이 이해하기 위한 단일 분류다. `tags`는 두지 않는다. runner에서 type별 부분 실행 옵션도 제공하지 않는다.

## Expected handling

`expected`는 optional이다.

```yaml
expected: expected.json
```

있으면 runner가 자동으로 actual output과 expected file을 byte equality 비교한다. 별도 assertion에서 `{expected}`를 반복해서 넣지 않아도 된다.

없으면 expected 비교를 하지 않는다.

`--promote`는 명시적 파일쓰기 옵션이다.

```bash
python3 scripts/run_evals.py --promote
```

동작:

- expected 없음: `cases/<case-id>/expected.json` 생성
- expected 있음: 해당 파일 overwrite
- promote 없음: expected 파일을 쓰지 않음

## Assertion types

### `command`

```yaml
- id: no-placeholder-left
  title: 템플릿 placeholder가 남아 있지 않은지 검증
  type: command
  cmd: python3 -c "import sys; t=open(sys.argv[1]).read(); assert '{{' not in t" {output}
```

`cmd` exit code가 0이면 pass다. `{input}`, `{output}`, `{expected}` placeholder를 사용할 수 있다. 단, `{expected}`를 쓰는 command는 case에 `expected`가 있어야 한다.

### `llm-judge`

`llm-judge`는 `type: llm-judge` case에서만 사용한다. `judge.command`는 case top-level에 두고, 각 assertion은 검증할 자연어 `prompt`를 직접 가진다.

```yaml
id: skill-quality
type: llm-judge
title: 생성된 스킬이 Stark 품질 기준을 만족하는지 검증

input: input.json

judge:
  method: subagent
  command: python3 scripts/run_llm_judge.py --input {judge_packet} --output {judge_output}
  timeout_sec: 300

assertions:
  - id: actionable-workflow
    title: 실행 가능한 workflow가 있는지 검증
    type: llm-judge
    prompt: 출력에는 사용자가 바로 실행할 수 있는 구체적인 workflow가 있어야 한다.
  - id: deterministic-verification
    title: 결정론적 검증 방법이 있는지 검증
    type: llm-judge
    prompt: 출력에는 command 기반 또는 재현 가능한 검증 방법이 포함되어야 한다.
```

`judge.method` 허용값:

- `subagent`: check별 독립 subprocess/agent call로 평가한다.
- `aggregate`: 기존 fixture 호환용 허용값이지만 신규 case에서는 쓰지 않는다.

`hybrid`는 두지 않는다.

## `type: llm-judge` case

`type: llm-judge` case는 `run.command`를 정의하지 않는다. 이 case는 primary execution이 아니라 judge 검증 자체가 목적이다. 필요한 실행은 top-level `judge.command`가 수행한다.

## `run_llm_judge.py` contract

LLM judge는 subprocess 방식으로 호출한다. Runner는 assertion-level `prompt`를 `{judge_packet}` JSON의 `prompt` 필드에 넣고, top-level `judge.command`를 실행해 `{judge_output}` text를 기대한다.

Required judge behavior:

- `run_llm_judge.py`에는 `--input {judge_packet}`을 넘긴다.
- `{judge_packet}` JSON의 public payload는 `schema_version`과 `prompt` 필드다.
- `{judge_output}`은 skill에 정의된 자연어 응답이며 고정 JSON verdict/evidence schema가 아니다.
- command exit code가 0이고 `{judge_output}`이 non-empty이면 runner-level 실행은 통과로 볼 수 있다. 자연어 판단 내용의 정책 결정은 review 단계에서 다룬다.

## run_evals.py 사용법

생성된 skill root에서 실행한다.

```bash
python3 scripts/run_evals.py --validate
python3 scripts/run_evals.py
python3 scripts/run_evals.py --promote
python3 scripts/run_evals.py --json
```

- `--validate`: `eval.yaml`과 선언된 `case.yaml` 구조를 검증한다. undeclared case directory도 여기서 잡는다.
- 기본 실행: `eval.yaml`에 선언된 모든 case를 실행한다. LLM judge assertion도 포함한다.
- `--promote`: passing case의 output을 expected로 생성 또는 overwrite한다.
- `--json`: machine-readable result를 출력한다.

`--no-llm-judge`, `--rollout`, `--output`, `--case`, type 기반 실행 옵션은 사용하지 않는다.

## 기본 case 적용

`skill-creator-for-stark`가 만드는 skill에는 최소 다음 성격의 case를 설계한다.

1. 새 skill 생성: eval suite, declared case, runner, quality gate가 포함되는지 확인한다.
2. 기존 skill 수정: 기존 eval suite를 보존·갱신하고 새 behavior에 맞춰 case/assertion이 변하는지 확인한다.
3. 다른 skill의 Stark 포맷 업데이트: source workflow를 보존하면서 Stark format과 case-based eval structure를 함께 심는지 확인한다.

## 검증 체크리스트

- [ ] `evals/<skill-name>.eval.yaml`이 존재한다.
- [ ] `eval.yaml`에 `skill`, `title`, `cases`가 있다.
- [ ] `eval.yaml`에 `description`이 없다.
- [ ] runner는 `eval.yaml`에 선언된 case만 실행한다.
- [ ] undeclared `evals/cases/*/case.yaml`은 validation error다.
- [ ] 각 case는 `id`, `type`, `title`, `assertions`를 가진다.
- [ ] 각 assertion은 `id`, `title`, `type`을 가진다.
- [ ] assertion type은 `command`, `llm-judge`만 사용한다.
- [ ] non-`llm-judge` case의 `run.command`에는 `{output}`이 있다.
- [ ] `type: llm-judge` case에는 `run.command`가 없다.
- [ ] `type: llm-judge` case는 top-level `judge.method`, `judge.command`를 가진다.
- [ ] `llm-judge` assertion은 `prompt`를 직접 가진다.
- [ ] `judge.method`는 `aggregate` 또는 `subagent`다.
- [ ] `expected`가 있으면 자동 equality 비교가 수행된다.
- [ ] `--promote`는 expected를 생성 또는 overwrite한다.
