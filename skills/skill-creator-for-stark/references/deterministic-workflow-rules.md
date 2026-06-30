# 결정론적 workflow 규칙

## 목적

스킬 안의 작업을 비결정적 판단과 결정적 반복 작업으로 나누고, 반복 가능한 부분은 `scripts/`로 분리해 재사용 가능하게 만든다.

## 분류 기준

### 결정론적 workflow

다음 조건을 만족하면 script 후보로 본다.

- 입력과 출력 형식이 명확하다.
- 같은 입력에 대해 같은 결과가 기대된다.
- 사람이 판단해야 하는 부분보다 변환, 수집, 검증, 정규화가 핵심이다.
- 실패 조건을 exit code나 structured output으로 표현할 수 있다.

예:

- frontmatter parse.
- Markdown fence balance check.
- JSON/YAML schema check.
- quality scorecard 점수 합계, hard gate, minimum score 검증.
- 파일 tree consistency check.
- 반복 데이터 변환.
- report skeleton 생성.

### 비결정론적 workflow

다음 조건이면 문서화된 판단 workflow로 둔다.

- 사용자의 취향, 정책 판단, domain judgment가 필요하다.
- 입력이 모호하고 agent가 가설을 세워야 한다.
- 정답이 하나가 아니며 사람이 review해야 한다.

다만 비결정적 workflow 안에서도 deterministic 하위 단계가 있으면 script로 분리한다.

## Script 작성 규칙

- script는 `scripts/` 아래에 둔다.
- 실행 방법과 입력/출력 파일을 `SKILL.md` 또는 `references/`에 적는다.
- 가능한 경우 stdout은 machine-readable하게 만든다.
- 실패 시 non-zero exit code와 명확한 error message를 낸다.
- secret, credential, external mutation은 기본 script에 넣지 않는다.

## 검증 보고

최종 보고에는 다음을 구분한다.

- 실행한 deterministic script.
- 사람이 판단한 non-deterministic review.
- 아직 script로 분리하지 않은 반복 작업과 이유.


## 파이프라인 오케스트레이션 (Pipeline orchestration)

2개 이상 script가 고정 순서로 연결되면 agent가 prose를 해석해 순서를 맞추게 하지 않고 `scripts/run_pipeline.py`를 만든다.

규칙:

- `scripts/run_pipeline.py`는 deterministic happy-path의 single entrypoint다.
- step 간 data handoff는 agent가 복사하지 않고 code가 함수 return 값이나 output file path를 연결한다.
- 각 step script는 개별 `main()`을 유지할 수 있지만 SKILL.md의 happy-path command는 `python3 scripts/run_pipeline.py ...` 하나로 둔다.
- third-party dependency가 있으면 `requirements.txt`에 선언한다.
- interactive/branching skill은 무리하게 pipeline으로 만들지 않는다. deterministic 부분만 script로 분리한다.

검증:

```bash
python3 scripts/check_pipeline.py <skill-dir>
```

`check_pipeline.py`는 `scripts/`와 `shared/` 아래 Python compile, third-party import 선언, 2개 이상 runnable step이 있을 때 `scripts/run_pipeline.py` 존재 여부를 확인한다. orchestrator wiring의 실제 정합성은 case-based eval suite의 각 `case.yaml`에서 `run.command`로 검증한다.

## Eval 연결

생성되는 skill이 deterministic happy path를 가지면 해당 eval case의 `run.command`에서 `scripts/run_pipeline.py`를 호출한다.

```yaml
run:
  command: python3 scripts/run_pipeline.py --input {input} --output {output}
  timeout_sec: 120
```

그 다음 `python3 scripts/run_evals.py --json`으로 `eval.yaml`에 declared된 case를 실행하고 produced output을 `command`/`llm-judge` assertion으로 채점한다. `llm-judge` adapter의 canonical CLI는 `run_llm_judge.py output --input input.json --output primary-output.json`와 `run_llm_judge.py assertion --input assertion-input.json --output assertion-output.json`다. 기존 runner가 top-level `judge.command`로 실행하는 `run_llm_judge.py --input {judge_packet}` 경로는 migration alias이며, `{judge_packet}` public JSON은 `schema_version`과 `prompt`만 가진다.
