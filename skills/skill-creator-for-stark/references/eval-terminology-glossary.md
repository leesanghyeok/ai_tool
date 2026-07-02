# eval.yaml 용어 사전

## 목적

`skill-creator-for-stark`의 eval 문서, template, runner 주석, test docstring에서 같은 artifact를 같은 이름으로 부르도록 공통 용어를 고정한다. 사람이 읽는 설명은 실제 파일명인 `eval.yaml`과 `case.yaml`을 우선 사용하고, `manifest`는 legacy/internal 맥락으로만 제한한다.

## Canonical terms

| 용어 | 의미 | 사용 위치 |
|---|---|---|
| `eval.yaml` | `evals/<skill-name>.eval.yaml` 파일을 가리키는 사용자-facing 표준 용어다. runner가 읽는 eval suite의 title, policy, case 목록을 담는다. | README, SKILL.md, reference, template, test docstring, runner 주석 |
| `case.yaml` | `eval.yaml`의 case entry가 `path`로 선언한 case file이다. 단일 executable case 또는 `cases[]` case group을 정의한다. | README, reference, template, runner/test 설명 |
| `eval suite` | 하나의 `eval.yaml`과 그 파일이 선언한 `case.yaml` 파일들의 전체 검증 묶음이다. | 사용자-facing 개요, 검증 보고 |
| `case entry` | `eval.yaml entries[]` 또는 legacy `cases[]` 안의 항목이다. `id`, `type`, `path`를 통해 실행할 `case.yaml`을 선언한다. | schema 설명, runner validation error, reference |
| `case file` | `evals/<case-id>/case.yaml` 같은 declared `case.yaml` 파일이다. | validation error, 문서 설명 |
| `entries[]` | canonical `eval.yaml` case 목록 key다. 각 entry는 declared `case.yaml` 파일을 가리킨다. | 새 template, 새 reference, runner 설명 |
| `cases[]` | `case.yaml` 내부에서 여러 executable subcase를 담는 key다. `eval.yaml cases[]`는 legacy compatibility로만 언급한다. | migration/compatibility 설명, runner 내부 |

## Legacy/internal terms

| 용어 | 허용 범위 | 대체 표현 |
|---|---|---|
| `manifest` | `_manifest_entries` 같은 기존 내부 함수명, 과거 history, legacy compatibility 설명에만 허용한다. 사용자-facing 문서에서 `eval.yaml`을 뜻하는 단독 표현으로 쓰지 않는다. | `eval.yaml`, `eval.yaml suite file`, `case entry` |
| `spec` | `parse_spec`, `validate_spec` 같은 내부 function/API 이름과 generic parser error에서만 허용한다. 사용자-facing artifact 이름으로 쓰지 않는다. | `eval.yaml`, `case.yaml`, `eval suite` |
| `suite manifest` / `eval manifest` | 과거 history나 legacy 설명에만 남긴다. 새 문서와 template에서는 사용하지 않는다. | `eval.yaml`, `eval.yaml suite file` |

## `eval.yaml entries[]`와 `case.yaml cases[]` 관계

1. `eval.yaml entries[]`가 validate/run 대상의 source of truth다.
2. 각 `entries[]` item은 declared `case.yaml` 파일 하나를 가리키는 `case entry`다.
3. `case.yaml`은 단일 executable case를 직접 정의하거나, 내부 `cases[]`로 여러 executable subcase를 정의할 수 있다.
4. runner는 `eval.yaml entries[]`에 없는 leftover case directory를 validate/run 대상에서 제외한다.
5. declared `case.yaml` 파일이 없으면 validation error다.
6. `eval.yaml cases[]`는 이전 구조를 읽기 위한 legacy compatibility로만 유지하며, 새 template과 새 문서는 `entries[]`를 사용한다.

## Schema validation 용어

- `nested schema validation`: `eval.yaml` top-level만이 아니라 `test_policy`, `entries[]`, declared `case.yaml`, `case.yaml cases[]`, `run`, `setup`, `judge`, `assertions[]`까지 허용 field set, required field, type, enum, placeholder 조건을 검증하는 runner 계약이다.
- `unknown field`: schema에 없는 YAML key다. 특정 key blacklist가 아니라 `additionalProperties: false` 성격으로 처리한다.
- `schema source of truth`: `scripts/run_evals.py`와 `scripts/run_evals_template.py`의 validation constants/helper다. 문서와 template은 이 구현 기준을 설명하고, dependency 없는 in-repo validator를 사용한다.

## 작성 규칙

- 새 사용자-facing 문서에서는 `manifest` 단독 표현을 쓰지 않는다.
- `manifest`가 꼭 필요하면 `legacy manifest term` 또는 `internal function name`처럼 범위를 함께 쓴다.
- test docstring은 “검증한다”만 쓰지 말고 기대 동작을 단정한다.
  - 좋은 예: “`eval.yaml`에 선언되지 않은 leftover case directory는 validate/run 대상에서 제외되어야 한다.”
  - 좋은 예: “`eval.yaml`에 선언된 `case.yaml` 파일이 없으면 validation error를 반환해야 한다.”
- file path, YAML key, function name 같은 machine identifier는 원문을 유지한다.
