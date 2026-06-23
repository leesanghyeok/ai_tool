# Hermes Persona/System-Prompt Evaluation Playbook (Live Session)

Use this reference when evaluating a `system_prompt.md` that will be installed into the
Hermes default profile persona path (typically `~/.hermes/SOUL.md`).

## 1) Source alignment

- Keep canonical prompt text in one source file (for example:
  `/path/to/persona/system_prompt.md`).
- Before evaluation, ensure the active prompt source equals applied prompt:
  - compare hash or bytes between source and `~/.hermes/SOUL.md`.
  - For default profile, prefer `SOUL.md` as the identity source.
  - `~/.hermes/config.yaml` `agent.system_prompt` is optional and not required for
    SOUL-centric default identity.

## 2) Scenario-driven evaluation workflow

1. Prepare/confirm fixed validation scenarios file.
2. Feed each scenario to a **new Hermes session** so cached persona state cannot
   leak from the current editing session:
   - `hermes chat --source cli -Q -q "<scenario prompt>"`
3. Capture each response (include scenario ID)
4. Score each scenario on `{1, 0.5, 0}`, then aggregate by rubric group weights.

Recommended group weights for persona prompts (adapt as needed):
- A: 승인/실행 경계 15
- B: 검증/완료 기준 15
- C: 커뮤니케이션 10
- D: 위험/보안/프라이버시 10
- E: 코드 설계/구현 15
- F: 대규모 분석/툴링 10
- G: 충돌/모순 처리 15
- H: 법률/재무/의료 제외 10

## 3) Scoring artifacts to keep separate

- `system_prompt.md` (canonical)
- `validation_scenarios.md` (scenario spec)
- `evaluation_rubric.md` (reusable rubric)
- `live_validation_responses_*.md/.json` (fresh responses)
- `scorecard.md/.json` (applied result)

Keep reusable rubric separate from one-off scorecard/results.

## 4) Required reporting for `v2`-style rubric

For each scoring run, include:
- Static dimension score
- Scenario group score + final scenario score
- global cap/penalty check (and reason)
- strengths / weaknesses / patch list
- machine-readable JSON summary

## 5) Practical guardrails

- If output has a warning or environment/toolset noise (`Warning: Unknown toolsets...`),
  do not fail the scenario score unless it changes judgment logic.
- If any scenario is graded 0/0.5, preserve that snippet in evidence.
- Cross-check prior cross-language targets if requested (e.g. translation-equivalence
  scorecard); do not regress below user threshold (commonly 95+).
