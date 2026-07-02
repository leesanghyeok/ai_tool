# 스킬 품질 루브릭 평가 규칙

## 목적

이 문서는 `skill-creator-for-stark`가 `/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md`를 사용해 skill package 품질을 평가하는 방식을 정의한다. 구조 validator는 형식 검증이고, 품질 루브릭 평가는 agent 행동 품질, 승인 경계, 검증 규율, 재사용성을 판단하는 별도 gate다.

## Mode별 적용 정책

| mode | 파일 수정 | 품질 루브릭 평가 | 완료 기준 |
|---|---|---|---|
| `create` | 승인된 범위에서 허용 | 필수 | `certification_score >= 95` AND D1-D5 hard gate 통과 |
| `modify` | 승인된 범위에서 허용 | 선택 | 평가를 실행했으면 95점 기준을 보고하고, 생략했으면 생략 사유를 보고 |
| `quality-review-only` | 금지 | 필수 | JSON scorecard 산출과 pass/fail 보고 |

`modify`에서도 다음 조건이면 품질 평가를 필수로 승격한다.

- 사용자가 품질 검증, 95점 이상, release 가능, production-quality, rubric 기준 평가를 요구한다.
- workflow, approval boundary, verification rule, trigger/scope, template, validator를 크게 바꾼다.
- 변경이 기존 skill의 D1-D5 hard gate에 영향을 줄 수 있다.

## 95점 기준

Canonical rubric의 기본 통과 기준은 90점이지만, 이 creator workflow의 release 기준은 95점이다.

- `create`: 95점 미만이면 완료가 아니라 수정 loop 대상이다.
- `modify`: 평가를 실행한 경우 95점 미만을 명확히 보고하고, 사용자가 품질 통과를 요구했다면 완료로 보고하지 않는다.
- `quality-review-only`: 요청이 단순 점수 확인이면 scorecard 산출이 완료지만, 통과 여부는 95점 기준으로 판정한다.

D1-D5 hard gate 중 하나라도 실패하면 numeric total과 무관하게 품질 통과 실패다.

## 평가 packet 구성 (Evaluation packet)

Quality judge에는 현재 대화나 작성자 self-report가 아니라 다음 packet만 제공한다.

- `target_skill_path`: 평가 대상 skill directory.
- `included_files`: `SKILL.md`, 관련 `references/`, `templates/`, `scripts/` 목록.
- `rubric_path`: `/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md`.
- `deterministic_checker_output`: validator 출력, file counts, word counts, markdown fence/link check 결과.
- `allowed_evidence`: packet 내부 파일과 deterministic checker output만 허용.
- `scorecard_schema`: rubric의 JSON Scorecard 스키마 또는 `templates/skill-quality-scorecard.template.json`.
- `scorecard_validator`: 가능한 경우 `scripts/validators/validate-quality-scorecard.py <scorecard.json> 95` 실행 결과.
- `workflow_mode`: `create`, `modify`, `quality-review-only`.
- `minimum_certification_score`: `95`.

## 판정자 실행 규칙 (Judge)

- 기본은 `clean_subagent`다.
- 긴 package 또는 high-stakes 평가에서는 D1-D8 shard를 나눈 `parallel_clean_subagents`를 사용한다.
- `same_context_exception`은 clean subagent가 불가능한 low-stakes quick check에서만 허용하고, scorecard에 contamination risk를 기록한다.
- Judge는 packet 밖 memory, 현재 대화, 작성자 의도, 이전 self-report를 점수 근거로 쓰면 안 된다.
- 특정 repository, source family, 유명 skill 이름값을 점수 보상 근거로 쓰지 않는다.

## Parent 검증 규칙

Parent agent는 judge 결과를 그대로 믿지 않는다. 다음을 직접 확인한다.

1. JSON scorecard가 parse되는가. 가능하면 `scripts/validators/validate-quality-scorecard.py`로 점수 합계, D1-D5 hard gate, 95점 기준을 검증했는가.
2. D1-D8 dimension score가 각 max score를 넘지 않는가.
3. D1-D8 합계와 `raw_total_score`가 일치하는가.
4. D1-D5 hard gate threshold가 모두 통과했는가.
5. local cap과 global cap이 적용됐고 `certification_score`에 반영됐는가.
6. `certification_score >= 95` 여부를 확인했는가.
7. `contract_checks`의 네 key가 모두 boolean이며, `input_contract_minimal`, `output_contract_actionable`, `env_contract_separated`, `variable_table_columns_valid`가 rubric의 `INPUT_`/`OUTPUT_`/`ENV_` 기준과 일치하는가.
8. issue와 recommended fix가 구체적 path와 evidence를 포함하는가.
9. `quality-review-only`에서 target skill, rubric, scorecard 파일을 쓰지 않았는가.

## 실패와 수정 loop

- `create`에서 95점 미만이면 가장 큰 blocker부터 수정한다.
- D1-D5 hard gate 실패는 critical blocker로 우선 처리한다.
- 수정 후 structural validator와 quality evaluation을 다시 실행한다.
- 반복 평가 결과는 `OUTPUT_QUALITY_FIXES`와 `OUTPUT_NEXT_ACTIONS`에 반영한다.
- 검증을 실행하지 못하면 `blocked` 또는 `unverified`로 보고하고 완료를 주장하지 않는다.

## 검증 전용 mode 금지 사항

`quality-review-only`에서는 다음을 하지 않는다.

- target skill file 수정.
- rubric file 수정.
- history 또는 scorecard 파일 저장. 단, 사용자가 저장을 승인하면 지정된 경로에만 쓴다.
- 점수 향상을 위한 자동 patch.
- packet 밖 정보를 evidence로 사용.
