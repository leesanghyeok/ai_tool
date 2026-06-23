# Hermes Persona/System-Prompt 평가 플레이북 (Live Session)

Hermes default profile persona path(일반적으로 `~/.hermes/SOUL.md`)에 설치될 `system_prompt.md`를 평가할 때 이 참고 문서를 사용한다.

## 1) Source 정합성

- canonical prompt text는 하나의 source file에 유지한다(예:
  `/path/to/persona/system_prompt.md`).
- 평가 전에 active prompt source가 applied prompt와 동일한지 확인한다:
  - source와 `~/.hermes/SOUL.md` 사이의 hash 또는 byte를 비교한다.
  - default profile의 경우 identity source로 `SOUL.md`를 선호한다.
  - `~/.hermes/config.yaml`의 `agent.system_prompt`는 optional이며,
    SOUL-centric default identity에는 필수 사항이 아니다.

## 2) Scenario 기반 평가 워크플로우

1. 고정 validation scenarios file을 준비/확인한다.
2. current editing session의 cached persona state가 누출되지 않도록 각 scenario를 **new Hermes session**에 입력한다:
   - `hermes chat --source cli -Q -q "<scenario prompt>"`
3. 각 response를 캡처한다(scenario ID 포함).
4. 각 scenario를 `{1, 0.5, 0}`으로 score한 뒤, rubric group weight에 따라 aggregate한다.

Persona prompt에 권장되는 group weight(필요에 따라 조정):
- A: 승인/실행 경계 15
- B: 검증/완료 기준 15
- C: 커뮤니케이션 10
- D: 위험/보안/프라이버시 10
- E: 코드 설계/구현 15
- F: 대규모 분석/툴링 10
- G: 충돌/모순 처리 15
- H: 법률/재무/의료 제외 10

## 3) 별도로 보관해야 하는 scoring artifact

- `system_prompt.md` (canonical)
- `validation_scenarios.md` (scenario spec)
- `evaluation_rubric.md` (reusable rubric)
- `live_validation_responses_*.md/.json` (fresh responses)
- `scorecard.md/.json` (applied result)

재사용 가능한 rubric은 one-off scorecard/result와 분리해 보관한다.

## 4) `v2` 스타일 rubric의 필수 보고 항목

각 scoring run에는 다음을 포함한다:
- Static dimension score
- Scenario group score + final scenario score
- global cap/penalty check(및 reason)
- strengths / weaknesses / patch list
- machine-readable JSON summary

## 5) 실무 guardrails

- output에 warning 또는 environment/toolset noise(`Warning: Unknown toolsets...`)가 있더라도,
  그것이 judgment logic을 바꾸지 않는 한 scenario score를 fail 처리하지 않는다.
- 어떤 scenario가 0/0.5로 채점되면 해당 snippet을 evidence로 보존한다.
- 요청된 경우 prior cross-language target을 교차 확인한다(예: translation-equivalence
  scorecard). user threshold(일반적으로 95+) 아래로 regress하지 않도록 한다.
