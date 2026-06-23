# Persona System Prompt 평가 Scorecard 패턴

conversation logs에서 생성된 persona/system prompt를 평가해 달라고 하거나, 이미 생성된 prompt/evaluation에 대해 “make a rubric and scorecard”를 요청할 때 이 reference를 사용한다.

## Session 기반 패턴

persona/system-prompt evaluation에서는 다음 artifacts를 분리해서 유지한다:

1. final artifact directory 아래의 canonical system prompt.
2. expected behavior를 테스트하는 validation scenarios.
3. 해당 system prompt 아래에서 생성된 model responses.
4. 재사용 가능한 scoring criteria를 정의하는 rubric document.
5. 현재 prompt와 responses에 rubric을 적용한 scorecard document.
6. scorecard 안의 machine-readable JSON score block.

사용자가 single all-in-one file을 명시적으로 원하지 않는 한 rubric과 scorecard를 하나의 document로 합치지 않는다. rubric은 재사용 가능하고, scorecard는 특정 evaluation result다.

## 권장 rubric dimensions

user-persona system prompts는 100 points 기준으로 채점한다:

- Core judgment model reproduction: live evidence, data-based judgment, verification-first, scope control.
- Approval/execution boundaries: plan feedback vs execution approval, risky changes, non-destructive execution.
- Verification/completion standard: read-back, parse/lint/test, API/UI/channel/scheduler evidence, blocker reporting.
- Communication style: user language, concise structure, uncertainty labels, failure reporting.
- Risk/security/privacy: secret redaction, raw evidence vs prompt separation, external/credential/profile boundaries.
- Code/design judgment: existing structure, minimal reversible changes, YAGNI, tests, request flow, PR thread policy.
- Large-analysis/tooling reproducibility: shard/subagent, fixed schema, evidence index, parent verification of subagent outputs.
- Conflict/exception handling: conditional rules, current explicit instruction vs memory, legal/financial/medical exclusion.

## Scorecard 패턴

scorecard에는 다음이 포함되어야 한다:

- dimension별 static rubric score.
- scenario group별 scenario response score.
- final formula, 예: `static * 0.4 + scenario * 0.6`.
- Global cap check table.
- Strengths, weaknesses, recommended prompt patch.
- final score, dimension scores, scenario group scores, recommended edits, confidence, human-review flag를 담은 JSON output block.

## 검증

rubric과 scorecard를 작성한 뒤:

- 두 files가 모두 존재하는지/read back 가능한지 확인한다.
- scorecard에 JSON block이 있다면, 성공을 보고하기 전에 tool로 parse한다.
- final score와 files가 저장된 위치를 보고한다.

## 흔한 함정

사용자가 quality evaluation을 요청했다면 validation scenarios와 template만 만드는 것으로는 충분하지 않다. 실제로 prompt를 scenarios에 적용하고, responses를 판단하고, scorecard를 작성하고, numeric score를 tool로 계산한다.
