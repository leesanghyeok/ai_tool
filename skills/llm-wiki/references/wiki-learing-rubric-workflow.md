# Wiki 학습 루브릭 워크플로우

루브릭 목표 평균점수에 미달한 wiki를 전문 corpus로 성장시키는 반복 워크플로우다. 특정 도메인이나 marketing에 한정하지 않는다.

## 기본 변수

- `domain`: 대상 도메인
- `wiki_path`: 대상 wiki 경로
- `rubric_path` 또는 `rubric_text`: 평가 루브릭
- `question_count`: 기본 10
- `target_average`: 기본 90
- `max_iterations`: 기본 10 또는 사용자 지정

## 핵심 루프

1. 도메인 관련 새 질문 `question_count`개를 생성한다.
2. 현재 wiki만 근거로 질문에 답변한다.
3. 답변을 루브릭으로 채점하고 평균을 도구로 계산한다.
4. 평균이 `target_average` 이상이면 종료한다.
5. 평균이 미달이면 질문별 gap을 분석한다.
6. gap에 필요한 자료를 병렬 subagent로 조사한다.
7. 검증된 원본 자료를 `<wiki_path>/raw/*` 아래에만 저장한다.
8. raw 자료를 기반으로 wiki 본문을 ingest/update한다.
9. 다음 반복에서는 반드시 새 질문을 생성해 다시 평가한다.

## 에이전트 격리 규칙

질문 생성, wiki 답변, 루브릭 채점은 반드시 서로 다른 신규 subagent가 수행한다. 한 에이전트가 질문을 만들고, 답변하고, 채점까지 이어서 하면 평가가 오염된다.

- 질문 생성 에이전트: 새 질문과 평가 의도만 생성한다. 답변/채점 금지.
- Wiki 답변 에이전트: 질문별 신규 agent가 wiki-only 답변만 작성한다. 루브릭 참조/채점 금지.
- 루브릭 판정 에이전트: 답변별 신규 agent가 루브릭으로 채점만 한다. 답변 수정/새 근거 추가/평균 계산 금지.
- 부모 에이전트: orchestration, 산출물 read-back 검증, `final_score` 파싱, 평균 계산, gap 종합만 수행한다.

## Raw-only 원본 규칙

원본 데이터는 반드시 `<wiki_path>/raw/*` 아래에만 저장한다. `raw/` 외부에 원본 자료를 저장하지 않는다.

하위 폴더는 먼저 wiki의 `SCHEMA.md`와 기존 구조를 확인해 따른다. 구조가 없을 때의 일반적인 후보는 다음과 같다.

- 웹 글: `raw/articles/`
- 보고서, public guide, product docs: `raw/reports/`
- 논문, PDF, book/open textbook: `raw/papers/`
- transcript: `raw/transcripts/`
- asset: `raw/assets/`

`_meta` 또는 `_archive` 사용은 이 워크플로우의 기본값이 아니다. 해당 wiki schema나 사용자가 명시적으로 요구할 때만 사용한다.

## Source discovery 전략

평균점수가 미달하면 루브릭 gap별로 source shard를 나누고 병렬 조사한다.

권장 source type:

- academic paper, arXiv, SSRN, NBER
- PDF, book, open textbook
- industry report, benchmark report, annual report
- official documentation, product documentation, vendor docs
- public guide, case study, presentation, transcript
- standard/regulatory docs

Subagent는 파일을 쓰지 않는다. 후보만 고정 schema로 반환한다.

```text
title
source
url
source_type
why_useful
claim_snippet
target_questions
expected_rubric_gap
access_status
notes
```

부모 agent가 URL 접근성, 본문 추출 가능 여부, 중복, source quality를 검증한 뒤 raw 저장과 wiki ingest를 수행한다.

## Wiki 답변 규칙

평가 답변은 현재 wiki 본문만 근거로 한다. raw에 저장됐지만 아직 wiki 본문으로 ingest되지 않은 내용은 최종 답변 근거로 쓰지 않는다. 일반 지식이나 skill 본문으로 보충하지 않는다. 근거가 부족하면 부족하다고 명시한다.

## 채점 규칙

채점 agent는 루브릭의 hard gate/cap을 엄격 적용하고 `final_score`를 반드시 출력한다. 평균은 부모 agent가 도구로 계산한다. keyword coverage만으로 `target_average` 달성을 주장하지 않는다.

## 검증 체크리스트

- [ ] `wiki_path`, `domain`, 루브릭이 명확하다.
- [ ] `question_count` 기본값 10 또는 사용자 지정값을 사용했다.
- [ ] `target_average` 기본값 90 또는 사용자 지정값을 사용했다.
- [ ] 이번 반복 질문은 새로 생성됐고 이전 질문과 중복되지 않는다.
- [ ] 질문 생성/답변/채점이 서로 다른 신규 subagent에서 수행됐다.
- [ ] wiki 답변은 wiki 본문 근거만 사용했다.
- [ ] 모든 score에 `final_score`가 있다.
- [ ] 평균을 도구로 계산했다.
- [ ] 미달 시 gap 분석과 source discovery 계획을 만들었다.
- [ ] 원본 자료는 `raw/` 아래에만 저장했다.
- [ ] wiki 본문은 raw 기반 ingest/update로만 보강했다.
- [ ] 같은 질문 재사용으로 종료조건을 맞추지 않았다.
