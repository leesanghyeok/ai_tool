# Subagent 병렬화 패턴

## 목적

이 문서는 스킬 작성 workflow에서 subagent를 언제, 어떻게 병렬로 사용할지 정의한다. 목표는 전체 workflow를 보고 병렬 처리 이득이 있는 구간을 찾아 처리하되, parent agent가 최종 검증 책임을 유지하는 것이다.

## 병렬화 판단 기준

병렬화에 적합한 작업은 다음 조건을 만족한다.

- 입력이 독립적이다.
- 결과가 파일 write 전에 review 가능한 초안이다.
- 실패해도 전체 작업을 망가뜨리지 않는다.
- parent가 read-back, diff, parse check로 검증할 수 있다.
- 다른 subagent 결과에 의존하지 않는다.

병렬화하면 안 되는 작업:

- 사용자 승인 확인.
- destructive overwrite.
- 최종 file write.
- credential 사용.
- production 또는 외부 system mutation.
- 최종 완료 판정.

## 권장 sharding

복합 스킬 작성 시 다음 단위로 나눌 수 있다.

1. **기존 사례 조사 agent**
   - 유사 스킬의 구조, section, support files를 조사한다.

2. **SKILL.md workflow draft agent**
   - orchestration 중심 `SKILL.md` 초안을 작성한다.

3. **references draft agent**
   - 세부 규칙, pitfalls, checklist, domain runbook을 작성한다.

4. **templates draft agent**
   - 출력 템플릿과 skeleton 파일을 작성한다.

5. **validator draft agent**
   - deterministic validator script 초안을 작성한다.

6. **review agents**
   - 구조 review.
   - 한국어/identifier 보존 review.
   - verification coverage review.
   - portability review.

## Subagent prompt skeleton

```text
너는 skill package 작성 보조 subagent다.

입력:
- INPUT_SKILL_NAME: <name>
- INPUT_SKILL_GOAL: <goal>
- INPUT_TARGET_RUNTIME: <runtime>
- INPUT_CONSTRAINTS: <constraints>
- INPUT_ASSIGNED_OUTPUT: <assigned artifact>

규칙:
- 설명 prose는 한국어로 작성한다.
- INPUT_, OUTPUT_, ENV_ 변수 규칙을 지킨다.
- SKILL.md는 workflow 중심이어야 하며, 세부사항은 references/templates/scripts로 분리한다.
- machine-readable identifier는 번역하지 않는다.
- 결과는 Markdown 초안 또는 review finding으로만 반환한다.
- 파일을 직접 썼다고 주장하지 말고, parent가 검증할 수 있는 내용만 반환한다.

출력:
- OUTPUT_DRAFT_SUMMARY
- OUTPUT_DRAFT_CONTENT
- OUTPUT_VERIFICATION_NOTES
- OUTPUT_OPEN_RISKS
```

## Parent 검증 규칙

Parent agent는 subagent 결과를 self-report로 취급한다. 다음을 직접 확인한다.

- 파일이 실제로 존재하는지 read-back한다.
- YAML/JSON은 parse한다.
- Markdown code fence balance를 확인한다.
- `INPUT_`, `OUTPUT_`, `ENV_`가 실제 본문에 정의되어 있는지 확인한다.
- `Commit Pitfalls`, `Verification Checklist`가 있는지 확인한다.
- `SKILL.md`가 지나치게 상세해져 references 분리 원칙을 어기지 않는지 확인한다.
- `git diff --check`와 `git status --short`를 확인한다.

## 병렬 review checklist

각 review agent는 다음 중 하나의 관점만 맡는다.

### 구조 review

- 필수 섹션이 있는가.
- workflow가 순서대로 실행 가능한가.
- fast-fail과 verification이 분리되어 있는가.

### 언어/identifier review

- 설명 문장이 한국어 중심인가.
- `INPUT_`, `OUTPUT_`, `ENV_`, YAML/JSON key, command, path 등 identifier가 보존됐는가.

### 검증 coverage review

- 실제 실행 가능한 검증 명령이 있는가.
- 검증 실패 시 영향과 recovery가 설명되는가.

### portability review

- Hermes/Codex에 과하게 종속되지 않는가.
- support file 구조가 portable한가.
- runtime reload 필요 여부를 과장하지 않는가.
