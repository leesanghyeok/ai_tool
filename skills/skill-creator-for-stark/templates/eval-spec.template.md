# Eval Spec: <skill-name>

이 eval spec은 `<skill-name>`의 loss function이다. `command` criteria는 자동 채점하고, `llm-judge` criteria는 현재 checklist로만 출력한다.

실행:

```bash
python3 scripts/run_evals.py --validate
python3 scripts/run_evals.py --rollout --json
```

## 기준 (Criteria)

1. **<criterion-id>** (`command`) — <관찰 가능한 binary 조건>.
2. **<criterion-id>** (`command`) — <관찰 가능한 binary 조건>.
3. **<criterion-id>** (`llm-judge`) — <자동 command로 보기 어려운 의미/품질 조건>.

## 골든 케이스 (Golden cases)

- `case-1`: <대표 입력과 기대 동작>
- `case-2`: <edge 또는 변형 입력과 기대 동작>
- `case-3`: <실패하기 쉬운 입력과 기대 동작>

`expected` baseline이 아직 없으면 `expected: null`, `expected_status: "pending-first-green"`으로 둔다. 첫 passing rollout을 baseline으로 저장하려면 사용자 승인 후 `python3 scripts/run_evals.py --rollout --promote`를 실행한다.

## JSON 명세 (Spec)

```json
{
  "skill": "<skill-name>",
  "run": "python3 scripts/run_pipeline.py --input {input} --output {output}",
  "criteria": [
    {
      "id": "<criterion-id>",
      "text": "<binary criterion text>",
      "type": "command",
      "cmd": "<command using {output}>"
    },
    {
      "id": "<judge-criterion-id>",
      "text": "<llm judge checklist text>",
      "type": "llm-judge"
    }
  ],
  "golden": [
    {
      "id": "case-1",
      "input": "golden/case-1/input.json",
      "expected": null,
      "split": "val",
      "expected_status": "pending-first-green"
    },
    {
      "id": "case-2",
      "input": "golden/case-2/input.json",
      "expected": null,
      "split": "val",
      "expected_status": "pending-first-green"
    },
    {
      "id": "case-3",
      "input": "golden/case-3/input.json",
      "expected": null,
      "split": "val",
      "expected_status": "pending-first-green"
    }
  ]
}
```
