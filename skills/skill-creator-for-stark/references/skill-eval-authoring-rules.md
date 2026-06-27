# 스킬 eval 작성 규칙

## 목적

생성되는 skill package가 처음부터 regression 가능한 loss function을 갖도록 `agent-skill-creator` eval 모델을 따른다. 이 문서는 `/Users/stark/practice/agent-skill-creator`의 `phase2-eval-assessment.md`, `phase5-orchestration.md`, `scripts/run_evals_template.py` 구조를 Stark용 스킬 생성 절차에 맞춰 정리한 것이다.

## 기본 원칙

- eval generation은 기본값으로 켠다. 사용자가 명시적으로 원하지 않거나 skill이 eval에 부적합할 때만 생략한다.
- eval은 “더 좋아졌는가” 비교가 아니라 “의도한 대로 동작하는가”를 검증하는 binary contract다.
- 가능한 criterion은 `command`로 만든다. 의미·톤·판단처럼 command로 확인하기 어려운 항목만 `llm-judge`로 둔다.
- `llm-judge`는 이번 모델에서 자동 채점하지 않는다. `run_evals.py`가 checklist로 출력하며, 자동 judge adapter는 추후 개선 항목이다.
- 생성된 skill이 deterministic happy path를 가지면 `scripts/run_pipeline.py`를 single entrypoint로 두고 eval spec의 `run` field에서 호출한다.

## Phase 2 — Eval Criteria Definition

SKILL.md를 쓰기 전에 다음을 정한다.

1. 3–6개 binary criteria를 만든다.
   - yes/no로 판단 가능해야 한다.
   - output을 읽거나 command를 실행해 관찰 가능해야 한다.
   - 서로 다른 실패 차원을 검증해야 한다.
   - 문구를 parroting하는 것만으로 통과할 수 없어야 한다.
2. 각 criterion의 `type`을 정한다.
   - `command`: `cmd`를 실행하고 exit code 0이면 pass.
   - `llm-judge`: 자동 채점하지 않고 checklist로 출력.
3. golden case를 3개 이상 만든다.
   - 사용자 제공 artifact가 있으면 그 artifact를 primary golden case로 쓴다.
   - 없으면 input-only case를 합성하고 `expected: null`, `expected_status: "pending-first-green"`으로 둔다.
   - first green output을 baseline으로 승격할 때는 `--promote`가 파일을 쓰므로 사용자 승인 또는 승인된 eval workspace가 필요하다.

## Phase 5 — Eval emission

생성되는 skill 안에 다음 구조를 둔다.

```text
<skill>/
  scripts/run_pipeline.py        # deterministic happy-path entrypoint, 필요한 경우
  scripts/run_evals.py           # scripts/run_evals_template.py 복사본
  evals/
    <skill-name>.eval.md         # prose + fenced JSON spec
    golden/
      case-1/input.*
      case-1/expected.*          # optional
      case-2/input.*
      case-3/input.*
```

`evals/<skill-name>.eval.md`는 사람이 읽는 설명과 하나의 fenced `json` block을 포함한다. `input`과 `expected` path는 `evals/` 기준 상대 경로다.

```json
{
  "skill": "example-skill",
  "run": "python3 scripts/run_pipeline.py --input {input} --output {output}",
  "criteria": [
    {"id": "valid-json", "text": "Output parses as JSON", "type": "command", "cmd": "python3 -c 'import json,sys; json.load(open(sys.argv[1]))' {output}"},
    {"id": "captures-risk", "text": "Output names the key risk", "type": "llm-judge"}
  ],
  "golden": [
    {"id": "case-1", "input": "golden/case-1/input.json", "expected": null, "split": "val", "expected_status": "pending-first-green"},
    {"id": "case-2", "input": "golden/case-2/input.json", "expected": null, "split": "val", "expected_status": "pending-first-green"},
    {"id": "case-3", "input": "golden/case-3/input.json", "expected": null, "split": "val", "expected_status": "pending-first-green"}
  ]
}
```

## run_evals.py 사용법

생성된 skill root에서 실행한다.

```bash
python3 scripts/run_evals.py --validate
python3 scripts/run_evals.py
python3 scripts/run_evals.py --output OUT [--case ID]
python3 scripts/run_evals.py --rollout [--promote] [--timeout N] [--case ID]
python3 scripts/run_evals.py --json
```

- `--validate`: spec shape와 golden file 존재를 검증한다. delivery gate로 사용한다.
- default run: golden expected baseline에 대해 `command` criteria를 실행한다.
- `--output`: 실제 produced output 하나를 criteria로 채점한다.
- `--rollout`: spec의 `run` command를 golden input별로 실행하고 produced output을 채점한다.
- `--promote`: pending-first-green output을 expected baseline으로 저장한다.

Exit code:

- `0`: 통과 또는 rollout unavailable.
- `1`: malformed spec, command failure, rollout error.
- `2`: eval spec 없음.

## run_pipeline.py와 연결

- 2개 이상 script가 고정 순서로 실행되어야 하면 `scripts/run_pipeline.py`를 만든다.
- SKILL.md에는 happy-path command를 하나만 적는다.
- step 간 data handoff는 agent prose가 아니라 `run_pipeline.py` code가 수행한다.
- eval spec의 `run` field는 가능하면 `python3 scripts/run_pipeline.py --input {input} --output {output}` 형태로 둔다.
- `run`이 있으면 `{output}` placeholder는 필수다.

## 기본 3종 case 적용

`skill-creator-for-stark`가 만드는 skill에는 최소 다음 성격의 case를 설계한다.

1. 새 skill 생성: eval spec, `scripts/run_evals.py`, 3개 이상 golden case가 생성되는지 확인한다.
2. 기존 skill 수정: 기존 eval spec을 보존·갱신하고 새 behavior에 맞춰 criteria/golden case가 변하는지 확인한다.
3. 다른 skill의 Stark 포맷 업데이트: source workflow를 보존하면서 Stark format과 eval structure를 함께 심는지 확인한다.

## 검증 체크리스트

- [ ] `evals/<skill-name>.eval.md`가 존재한다.
- [ ] fenced `json` block이 정확히 하나 이상 있고 parse된다.
- [ ] `criteria`가 non-empty이며 각 항목에 `id`, `text`, `type`이 있다.
- [ ] `command` criterion은 `cmd`가 있다.
- [ ] `golden` case가 3개 이상이다.
- [ ] golden `input` file이 존재한다.
- [ ] `expected: null`이면 `expected_status: "pending-first-green"`이 있다.
- [ ] `run`이 있으면 `{output}` placeholder가 있다.
- [ ] deterministic happy path가 있으면 `scripts/run_pipeline.py`가 있다.
- [ ] `python3 scripts/run_evals.py --validate`가 exit 0이다.
- [ ] 가능하면 `python3 scripts/run_evals.py --rollout --json`까지 실행해 real output을 검증한다.
