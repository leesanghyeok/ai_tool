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
- 외부 배포, 자동 설치, registry publish.
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

5. **validator/script draft agent**
   - deterministic validator 또는 반복 workflow script 초안을 작성한다.

6. **trigger example draft agent**
   - `should_trigger` / `should_not_trigger` 예시를 작성한다.

7. **review agents**
   - 구조 review.
   - 한국어/식별자 보존 review.
   - verification coverage review.
   - portability review.

## Subagent prompt skeleton 작성 예시

```text
너는 skill package 작성 보조 subagent다.

입력:
- INPUT_SKILL_NAME: <name>
- INPUT_SKILL_GOAL: <goal>
- INPUT_CONSTRAINTS: <constraints>
- INPUT_ASSIGNED_OUTPUT: <assigned artifact>

규칙:
- 설명 prose는 한국어로 작성한다.
- INPUT_, OUTPUT_, ENV_ 변수 규칙을 지킨다.
- SKILL.md는 workflow 중심이어야 하며, 세부사항은 references/templates/scripts/history로 분리한다.
- 가능한 deterministic workflow는 scripts/로 분리할 수 있게 설계한다.
- should_trigger / should_not_trigger 예시는 현실적인 사용자 요청으로 작성한다.
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
- `INPUT_`, `OUTPUT_`, `ENV_`가 실제 본문에 table로 정의되고 각 항목에 필수/기본값/설명이 있는지 확인한다.
- `Hard Gates`, `Commit Pitfalls`, `Verification Checklist`가 있는지 확인한다.
- `SKILL.md`가 지나치게 상세해져 references 분리 원칙을 어기지 않는지 확인한다.
- deterministic 반복 작업이 문서 prose에만 남아 있지 않은지 확인한다.
- `git diff --check`와 `git status --short`를 확인한다.

## 병렬 review checklist

각 review agent는 다음 중 하나의 관점만 맡는다.

### 구조 review

- 필수 섹션이 있는가.
- workflow가 순서대로 실행 가능한가.
- hard gate, fast-fail, verification이 분리되어 있는가.

### 언어/identifier review

- 설명 문장이 한국어 중심인가.
- `INPUT_`, `OUTPUT_`, `ENV_`, YAML/JSON key, command, path 등 identifier가 보존됐는가.

### 검증 coverage review

- 실제 실행 가능한 검증 명령이 있는가.
- 검증 실패 시 영향과 recovery가 설명되는가.
- 크기 제한과 trigger example 조건을 확인하는가.

### 이식성 review

- 특정 에이전트 실행 환경, 설치 방식, 외부 배포 방식에 불필요하게 종속되지 않는가.
- support file 구조가 portable한가.
- 현재 세션에서 바로 load 가능하다고 과장하지 않는가.


## 품질 루브릭 평가 subagent 패턴

`skill-quality-rubric-v1.md` 평가는 clean context를 기본으로 한다.

- `create`: quality judge를 반드시 실행한다.
- `modify`: 사용자가 품질 검증, 95점, 릴리즈 가능 여부를 요구하거나 workflow/approval/verification/trigger/scope/template/validator 변경이 크면 실행한다. 그 외에는 생략할 수 있지만 parent가 생략 사유를 보고한다.
- `quality-review-only`: 파일 수정 없이 quality judge를 실행한다.

큰 skill package나 high-stakes 평가는 D1-D8을 shard로 나눈 `parallel_clean_subagents`를 사용할 수 있다. shard judge는 자기 dimension만 채점하고 최종 pass/fail, global cap, 95점 통과 여부를 확정하지 않는다.

Parent agent는 다음을 중앙에서 검증한다.

- JSON scorecard가 parse되는가.
- D1-D8 점수 합계가 `raw_total_score`와 일치하는가.
- D1-D5 hard gate threshold를 모두 통과했는가.
- local cap과 global cap이 한 번만 적용됐는가.
- `certification_score >= 95`인지 확인했는가.
- evidence path가 packet 안 파일에 근거하는가.
- `quality-review-only`에서 파일 수정이 발생하지 않았는가.
