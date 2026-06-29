# Eval Suite: <skill-name>

`<skill-name>`의 case-based eval suite manifest다. 이 파일은 실행 로직이 아니라 runner가 실행할 case 목록과 사람이 읽는 test map을 제공한다.

```yaml
version: 1
skill: <skill-name>
title: <skill-name> eval suite

test_policy:
  expected_compare: auto
  llm_judge: required
  undeclared_cases: error
  promote: allow-overwrite

cases:
  - id: <case-id>
    type: happy-path
    title: <이 case가 검증하는 목적을 한글로 작성>
    path: cases/<case-id>/case.yaml
```

## Case skeleton

`evals/cases/<case-id>/case.yaml`:

```yaml
id: <case-id>
type: happy-path
title: <이 case가 검증하는 목적을 한글로 작성>

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

```

`type: llm-judge` case 예시:

```yaml
id: semantic-quality
type: llm-judge
title: 출력이 요구사항을 의미적으로 만족하는지 검증

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
```

## 작성 규칙

- `eval.yaml`에는 `description`, top-level `run.command`, `global_assertions`를 두지 않는다.
- runner는 `eval.yaml`에 선언된 case만 실행한다.
- `expected`가 있으면 자동 equality 비교가 수행된다.
- `expected`가 없으면 비교하지 않는다.
- `--promote`는 expected를 생성하거나 overwrite한다.
- assertion type은 `command`, `llm-judge`만 사용한다.
- `type: llm-judge` case에는 `run.command`를 두지 않는다.
- `type: llm-judge` case의 `judge.command`는 top-level에 두고, assertion에는 `prompt`를 직접 둔다.
