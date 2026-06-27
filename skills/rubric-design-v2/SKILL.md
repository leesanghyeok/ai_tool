---
name: rubric-design-v2
description: 재사용 가능한 평가 루브릭을 새로 설계하거나 기존 루브릭을 개선할 때 사용합니다. 점수 구조, 관찰 가능한 기준, 상한 규칙, clean judge 실행, 보정 산출물을 분리해야 할 때 쓰며, 단순 채점 적용만 필요한 경우에는 쓰지 않습니다.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  tags: [rubric, evaluation, llm-as-judge, scoring, calibration]
  related_skills: [rubric-design, writing-plans, test-driven-development]
---

# 루브릭 설계 v2

## 개요

이 스킬은 AI 출력, 연구 요약, 문서, 모델 응답, 코드/에이전트 작업처럼 반복 평가가 필요한 대상을 위한 재사용 루브릭을 설계한다. 핵심 산출물은 사람이 읽는 루브릭 문서, clean judge가 사용할 evaluation packet, 기계 판독 가능한 scorecard schema, 그리고 보정 계획이다.

v2의 목표는 기존 `rubric-design`의 긴 본문 지식을 `references/`, 복사 가능한 골격을 `templates/`, 결정적 검사를 `scripts/`로 분리하는 것이다. `SKILL.md`는 trigger, 승인 경계, workflow, 검증만 조율한다.

## 사용 판단

### 사용한다

- 사용자가 새 평가 루브릭, 채점 기준, LLM-as-a-Judge 기준, scorecard schema, 보정 절차를 설계해 달라고 요청한다.
- 기존 루브릭을 더 엄격하게 만들거나, checklist item, local/global cap, calibration sample, judge prompt를 개선해야 한다.
- 평가 대상이 장문·다차원·high-stakes라 clean subagent 또는 parallel clean subagents 판정 구조가 필요하다.
- 예시: “이 문서 평가 루브릭을 100점 기준으로 만들어줘.”
- 예시: “기존 루브릭이 너무 관대해. cap과 calibration까지 v2로 고쳐줘.”
- 예시: “LLM judge가 쓸 JSON scorecard schema까지 포함해줘.”

### 사용하지 않는다

- 사용자가 이미 확정한 루브릭으로 단순 채점만 요청한 경우. 이때는 제공된 루브릭 적용 workflow를 사용한다.
- 평가 기준 설계가 아니라 사실 조회, 요약, 번역, 문장 다듬기만 필요한 경우.
- 법률·의료·금융 판단처럼 사용자를 대신해 최종 결정을 내려야 하는 경우.
- 외부 게시, production 변경, credential 사용이 필요한 경우. 별도 승인과 해당 전용 skill이 필요하다.

## 입력 변수

| 변수 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `INPUT_EVALUATION_GOAL` | required | 없음 | 루브릭이 평가해야 하는 대상과 점수가 지원할 의사결정이다. 없으면 차원, 가중치, cap을 정할 수 없어 fast fail한다. |
| `INPUT_TARGET_ARTIFACT_TYPE` | required | 없음 | 평가 대상의 유형이다. 예: `LLM response`, `research briefing`, `agent task result`, `skill package`. 유형에 따라 차원 후보와 검증 근거가 달라진다. |
| `INPUT_USER_PRIORITIES` | optional | 현재 요청과 사용자 고정 규칙 | 어떤 품질을 더 보상할지에 대한 우선순위다. 없으면 요청 본문과 사용자의 language/evidence/verification 선호를 근거로 추정하고 표시한다. |
| `INPUT_OUTPUT_DESTINATION` | optional | 채팅 응답 또는 승인된 파일 경로 | 루브릭을 어디에 둘지 정한다. 파일 작성, overwrite, repo metadata 변경은 명시 승인된 경로에서만 수행한다. |
| `INPUT_CALIBRATION_SCOPE` | optional | `plan-only` | sample output 채점까지 할지, calibration plan만 만들지 정한다. 실제 sample 생성·저장은 별도 비용/파일 쓰기/실행 범위를 바꿀 수 있다. |
| `INPUT_JUDGING_MODE` | optional | `clean_subagent` | 루브릭 적용 판정을 어떻게 실행할지 정한다. `clean_subagent`, `parallel_clean_subagents`, `same_context_exception` 중 하나이며 high-stakes 또는 긴 대상은 parallel을 우선한다. |

## 출력 변수

| 변수 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `OUTPUT_RUBRIC_DOCUMENT` | required | 없음 | 사람이 읽는 루브릭 본문 또는 저장 경로다. 평가 목적, 대상, 차원, 체크리스트, cap, 채점 절차를 포함해야 완료로 본다. |
| `OUTPUT_SCORE_SCHEMA` | required | 없음 | judge 결과를 검증할 JSON schema 또는 scorecard skeleton이다. 누락되면 LLM-as-a-Judge 재사용성이 낮아진다. |
| `OUTPUT_EVALUATION_PACKET_GUIDE` | required | 없음 | clean judge에게 제공할 included/excluded context, evidence bundle, shard 경계를 설명한 산출물이다. |
| `OUTPUT_CAPS_AND_CALIBRATION` | required | 없음 | local/global cap, 감점 규칙, calibration sample family 또는 실제 calibration 결과다. |
| `OUTPUT_VERIFICATION_RESULT` | required | 없음 | read-back, schema parse, 점수 합계, `scripts/validate-rubric-artifact.py`, 파일 write 검증 같은 실제 결과다. |
| `OUTPUT_OPEN_QUESTIONS` | optional | `[]` | 우선순위, 저장 위치, sample output, judge 실행 범위, 승인 경계 중 미확인 항목이다. |

## 필수 환경

| 환경 항목 | 필수 | 기본값 | 설명 |
|---|---:|---|---|
| `ENV_SOURCE_ACCESS` | required | 현재 workspace와 제공 자료 | 기존 루브릭, 평가 대상, source bundle을 읽을 수 있어야 한다. 읽을 수 없으면 근거 기반 차원 설계와 read-back 검증이 불가능하다. |
| `ENV_WRITE_APPROVAL` | optional | 채팅 응답만 작성 | 파일 저장, history, scorecard, sample artifact 생성은 사용자가 승인한 경로에서만 수행한다. 승인이 없으면 응답 본문으로만 산출한다. |
| `ENV_CLEAN_JUDGE_SURFACE` | optional | subagent 또는 새 session | 실제 채점/보정이 필요한 경우 clean context가 필요하다. 없으면 `same_context_exception`으로 낮추고 오염 위험을 보고한다. |
| `ENV_JSON_PARSE_RUNTIME` | required | `python3` | scorecard schema, sample score, cap 적용 결과를 parse하고 점수 합계를 검증하기 위한 runtime이다. |

## 하드 게이트 (Hard Gates)

- 목적 정합성 gate: 루브릭은 평가 대상, 점수 사용 의사결정, 탁월한 출력의 정의를 명시해야 한다.
- 관찰 가능성 gate: 각 차원은 독립 채점 가능한 checklist item으로 나뉘어야 하며, 넓은 range anchor만으로 점수를 정하지 않는다.
- 상한 규칙 gate: 치명적 누락, 조작된 근거, safety/privacy 위반, off-topic 출력에는 global cap 또는 local cap이 있어야 한다.
- clean judging gate: LLM judge 사용이 예상되면 evaluation packet 경계와 포함/제외 context를 명시하고, 현재 대화·memory를 근거로 쓰지 않게 한다.
- 구조화 출력 gate: 사람이 읽는 루브릭과 machine-readable score schema를 함께 제공한다.
- 보정 분리 gate: canonical rubric과 calibration results/history를 같은 기준 문서에 섞지 않는다.

## 빠른 중단 조건 (Fast Fail)

- `INPUT_EVALUATION_GOAL` 또는 `INPUT_TARGET_ARTIFACT_TYPE`이 없어 평가 범위를 정할 수 없다.
- 사용자가 요구한 파일 저장, overwrite, 외부 게시, credential 사용, production 변경에 대한 승인이 없다.
- 평가 대상 또는 source bundle을 읽을 수 없는데 사실성·근거 품질을 평가하라고 요청한다.
- 사용자가 sample score를 canonical rubric 안에 영구 기준처럼 섞으라고 요구해 보정 분리 gate와 충돌한다.
- JSON schema나 점수 합계를 검증할 runtime이 없는데 LLM judge용 scorecard 완료를 주장해야 한다.

## 작업 절차 (Workflow)

1. 입력과 승인 범위를 확정한다. `INPUT_` 값이 명시인지, source에서 확인됨인지, 추정인지 라벨링한다.
2. 평가 목적을 한 문장으로 고정한다: 무엇을 평가하고, 누가 점수를 쓰며, 어떤 결정을 지원하는지 적는다.
3. 평가 대상과 허용 근거를 정의한다. packet에 포함할 자료와 제외할 context를 분리한다.
4. 사용자 우선순위에 따라 5–8개 차원을 고르고, 핵심 차원 60–75점과 보조 차원 25–40점으로 가중치를 배정한다.
5. 각 차원을 1–5점 단위의 관찰 가능한 checklist item으로 쪼갠다. 기준마다 인정 근거를 적는다.
6. local cap, global cap, 감점 규칙을 설계한다. 중요한 것은 point로, 치명적인 것은 cap으로 처리한다.
7. `templates/rubric-document.template.md`와 `templates/judge-scorecard.schema.json`를 기준으로 루브릭과 score schema를 작성한다.
8. LLM judge가 사용할 `templates/evaluation-packet.template.md` 구조로 included evidence, excluded context, judging mode, shard boundary를 정의한다.
9. 긴 평가 대상 또는 high-stakes 평가는 `parallel_clean_subagents`로 차원 shard를 나누고 parent가 JSON parse, 누락/중복 기준, score bounds, cap 적용을 중앙 검증한다.
10. read-only discovery, file inspection, parsing, score 합계 검증은 불필요하게 묻지 않고 수행한다. 파일 write, overwrite, 외부 게시, credential 사용은 승인된 범위에서만 수행한다.
11. 파일을 썼다면 read-back하고 `scripts/validate-rubric-artifact.py <rubric.md>`, `scripts/validate-scorecard.py <scorecard.json>`, `scripts/check-korean-first.py <path>` 또는 동등한 ad-hoc check를 실행한다. 채팅 응답만이면 구조 checklist와 JSON parse 가능성을 확인한다.
12. calibration이 승인됐으면 강한/보통/약한/tricky sample을 채점해 점수 순위, cap trigger, judge variance를 확인한다. 승인되지 않았으면 calibration plan만 분리 보고한다.
13. 최종 보고에는 `OUTPUT_` 산출물, 검증 결과, 미확인 항목, 다음 승인점을 대응시킨다.

## Subagent 병렬화

- 병렬화 가능한 구간: domain별 차원 후보 조사, 기존 루브릭 gap review, sample family 설계, score schema review, Korean-first language review.
- 직렬 구간: 평가 목적 확정, 파일 write 승인 확인, 최종 가중치 합계 조정, global cap 최종 적용, 완료 보고.
- parent 검증: subagent self-report를 그대로 믿지 않고 산출물 파일, JSON parse 결과, 점수 합계, 중복 기준, cap 적용 결과를 직접 확인한다.

## 출력 템플릿

- 사람이 읽는 루브릭은 `templates/rubric-document.template.md`를 사용한다.
- clean judge packet은 `templates/evaluation-packet.template.md`를 사용한다.
- JSON scorecard는 `templates/judge-scorecard.schema.json`의 key와 enum을 유지한다.
- 스킬 사용 불만족 raw log는 `templates/feedback-log.template.md`를 사용한다.

## 피드백 로깅 (Feedback Logging)

- 사용자가 이 스킬 사용 중 “기대와 다르다”, “이 실패를 기록해”, “스킬 피드백으로 남겨”처럼 명시하면 skill-dissatisfaction incident로 본다.
- raw log는 이 스킬 디렉터리 내부 `feedback/YYYY-MM-DD/{HHMMSS}-{session_id}-{short-slug}.md`에 새 파일로 남긴다.
- 가능하면 `feedback-ai-logging-v2` 호환 포맷, 중복 검사, body-only `sha256`, read-back 검증을 사용한다.
- raw feedback에는 처리 상태나 TODO를 쓰지 않고, 개선 patch와 feedback log를 같은 파일에 섞지 않는다.
- secret, token, cookie, private URL, credential 원문은 redaction한 뒤 저장한다.

## 커밋 주의사항 (Commit Pitfalls)

- generated rubric artifact, calibration result, skill package source를 한 commit에 무리하게 섞지 않는다.
- unrelated worktree changes를 포함하지 않는다.
- sample score나 one-off judge result를 canonical rubric 기준으로 커밋하지 않는다.
- 검증 실패 또는 `same_context_exception` 미표시 상태의 scorecard를 release artifact처럼 커밋하지 않는다.

## 검증 체크리스트 (Verification Checklist)

- [ ] `INPUT_EVALUATION_GOAL`과 `INPUT_TARGET_ARTIFACT_TYPE`이 확인됐다.
- [ ] 평가 목적, 평가 대상, 점수 사용 의사결정이 루브릭에 있다.
- [ ] 총점이 100점 또는 사용자가 요청한 척도로 정규화됐다.
- [ ] 각 차원이 관찰 가능한 checklist item으로 분해됐다.
- [ ] local cap과 global cap이 checklist 채점 이후 적용되도록 정의됐다.
- [ ] judge prompt가 total score 선결정을 금지하고 evidence 기반 채점을 요구한다.
- [ ] scorecard schema가 parse 가능하고 점수 합계 검증이 가능하다.
- [ ] evaluation packet이 included evidence와 excluded context를 분리한다.
- [ ] calibration result와 canonical rubric이 분리됐다.
- [ ] 파일을 쓴 경우 read-back과 `scripts/validate-rubric-artifact.py`를 실행했다.
- [ ] 스킬 사용 불만족을 `feedback/`에 기록하는 절차와 중복/read-back 기준이 있다.

## 최종 응답 체크리스트 (Final Response Checklist)

- 상태: `completed`, `partial`, `blocked`, `unverified` 중 하나.
- `OUTPUT_RUBRIC_DOCUMENT`, `OUTPUT_SCORE_SCHEMA`, `OUTPUT_EVALUATION_PACKET_GUIDE`, `OUTPUT_CAPS_AND_CALIBRATION` 대응 산출물.
- 실행한 검증 command/tool과 실제 결과.
- 사용한 judging mode와 clean/parallel/same-context 예외 사유.
- 미확인 priority, source, destination, sample, approval boundary.
- 의도적으로 유지한 영어 identifier: `INPUT_`, `OUTPUT_`, `ENV_`, JSON key, enum, file path, command.
