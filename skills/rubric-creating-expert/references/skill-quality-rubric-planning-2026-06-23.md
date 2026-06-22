# Skill 품질 루브릭 계획 참고

## 맥락

사용자가 Hermes/Codex 계열 skill library를 평가하기 위한 루브릭 계획을 요청했다. 선호 참조군은 gstack, superpower, mattpocock류 skill repo였고, 저장 대상은 `/Users/stark/project/jarvis/ai_tool/rubric`였다.

## durable learning

Skill 평가 루브릭은 일반 문서 품질보다 “에이전트 행동을 실제로 개선하는가”를 중심으로 설계해야 한다.

좋은 skill의 핵심 신호:

- activation trigger가 명확하다.
- when-not-to-use / scope boundary가 있다.
- agent가 바로 실행할 수 있는 numbered workflow가 있다.
- prerequisite discovery와 execution이 분리된다.
- approval boundary, destructive/external/persistent/cost/credential gate가 명시된다.
- verification/read-back/test/API response/UI confirmation 같은 evidence gate가 있다.
- common pitfalls와 recovery path가 있다.
- templates, schemas, command snippets, linked references가 재사용 가능하다.
- Hermes tool/subagent/memory/skill/profile boundary와 사용자 선호를 반영한다.

## 권장 100점 차원

- D1 Activation & Scope Fit — 15
- D2 Actionability & Workflow — 20
- D3 Verification & Evidence Discipline — 15
- D4 Safety, Approval & Boundary Handling — 15
- D5 Reusability & Artifact Quality — 10
- D6 Failure Modes & Pitfalls — 10
- D7 Integration with Hermes/User Conventions — 10
- D8 Maintainability & Concision — 5

## cap/gate 후보

- 실행 절차가 거의 없고 설명/개념 위주이면 최대 65점.
- verification 없이 완료를 주장하도록 유도하면 최대 70점.
- destructive/external/persistent action에 대한 approval boundary가 없으면 최대 75점.
- trigger가 모호해서 아무 작업에나 남용될 수 있으면 최대 80점.
- Hermes skill frontmatter/metadata가 깨져 로드 불가능하면 최대 60점.
- secret/credential 평문 저장이나 노출을 유도하면 최대 50점.

## artifact shape

루브릭 기준과 실행 설정은 분리한다.

```text
/Users/stark/project/jarvis/ai_tool/rubric/skill/
  skill-quality-rubric-v1.md
  check_skill_quality.py                  # 선택: deterministic check 가능 항목만
  calibration/
    run-config.md
    samples/
    scores/
```

Deterministic checker는 정성 judge를 대체하지 않고 preflight만 담당한다. 예: `SKILL.md` 존재, frontmatter parse, 필수 metadata, section 존재, linked file resolve, code fence 균형, checklist/command block 존재.

## 적용 메모

Skill 품질 루브릭을 만들 때는 `rubric-design`으로 기준을 작성하되, `rubric-creating-expert` 원칙에 따라 샘플 skill로 calibration한다. gstack/superpower/mattpocock류는 참조 감각으로만 쓰고, 실제 채점 기준은 사용자의 Hermes workflow 선호(evidence-first, narrow scope, approval separation, verification before completion)를 반영한다.
