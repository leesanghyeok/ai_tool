# Eval Spec: skill-creator-for-stark

이 eval spec은 `skill-creator-for-stark` 자체의 regression contract다. 자동 `command` criteria는 package 구조, eval spec 유효성, 가져온 upstream regression test 실행 가능성을 확인한다. `llm-judge` criteria는 자동 채점하지 않고 checklist로만 출력한다.

실행:

```bash
python3 scripts/run_evals.py --validate
python3 scripts/run_evals.py --json
python3.11 -m unittest discover -s scripts/tests -v
```

## 기준 (Criteria)

1. **package-validator-pass** (`command`) — `scripts/validate-skill-package.py`가 이 skill directory를 통과해야 한다.
2. **eval-runner-validate-pass** (`command`) — `scripts/run_evals.py --validate`가 이 eval spec과 golden input 존재를 통과해야 한다.
3. **upstream-regression-tests-pass** (`command`) — `/Users/stark/practice/agent-skill-creator/scripts/tests`에서 가져온 local regression tests가 통과해야 한다.
4. **creator-workflow-contract** (`llm-judge`) — 생성/수정/quality-review-only workflow가 승인 경계, eval emission, feedback logging, quality-rubric gate를 유지하는지 agent가 read-back 근거로 확인한다.

## 골든 케이스 (Golden cases)

- `create-new-skill`: 새 skill package 생성 요청에서 eval spec과 runner를 포함해야 하는지 확인한다.
- `modify-existing-skill`: 기존 skill 수정 요청에서 기존 eval을 보존·갱신하고 검증 절차를 실행해야 하는지 확인한다.
- `quality-review-only`: read-only 품질 검토 요청에서 파일을 쓰지 않고 scorecard/검증 가능성만 보고해야 하는지 확인한다.

`expected` baseline은 아직 없다. 이 spec의 자동 criteria는 output baseline 비교가 아니라 현재 package의 command criteria 통과 여부를 본다.

## JSON 명세 (Spec)

```json
{
  "skill": "skill-creator-for-stark",
  "criteria": [
    {
      "id": "package-validator-pass",
      "text": "The package validator passes for the skill-creator-for-stark directory.",
      "type": "command",
      "cmd": "python3 scripts/validate-skill-package.py . >/dev/null"
    },
    {
      "id": "eval-runner-validate-pass",
      "text": "The eval runner validates this eval spec and golden inputs.",
      "type": "command",
      "cmd": "python3 scripts/run_evals.py --validate >/dev/null"
    },
    {
      "id": "upstream-regression-tests-pass",
      "text": "The imported upstream regression tests pass in the local skill package layout.",
      "type": "command",
      "cmd": "python3.11 -m unittest discover -s scripts/tests >/dev/null"
    },
    {
      "id": "creator-workflow-contract",
      "text": "Read SKILL.md and support files to confirm the creator keeps approval boundaries, eval emission, feedback logging, and quality-rubric gates aligned across create, modify, and quality-review-only modes.",
      "type": "llm-judge"
    }
  ],
  "golden": [
    {
      "id": "create-new-skill",
      "input": "golden/create-new-skill/input.json",
      "expected": null,
      "split": "val",
      "expected_status": "pending-first-green"
    },
    {
      "id": "modify-existing-skill",
      "input": "golden/modify-existing-skill/input.json",
      "expected": null,
      "split": "val",
      "expected_status": "pending-first-green"
    },
    {
      "id": "quality-review-only",
      "input": "golden/quality-review-only/input.json",
      "expected": null,
      "split": "val",
      "expected_status": "pending-first-green"
    }
  ]
}
```
