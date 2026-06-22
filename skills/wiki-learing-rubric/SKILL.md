---
name: wiki-learing-rubric
description: 루브릭 목표 평균점수에 미달한 wiki를 raw 자료 수집과 wiki ingest 반복 루프로 전문화하고, 매 반복 새 질문으로 재평가하는 워크플로우.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [wiki, rubric, corpus, research, evaluation, subagents]
---

# 위키 학습 루브릭

## 개요

이 스킬은 특정 도메인의 wiki가 루브릭 평가에서 목표 평균점수를 넘지 못할 때 사용하는 폐루프 워크플로우를 정의한다.

핵심 목적은 단순히 소스를 많이 모으는 것이 아니다. 루브릭 기준을 통과하지 못한 원인을 질문·답변·채점 결과로 찾고, 부족한 근거 자료를 `raw/` 아래에만 수집한 뒤, 그 raw 자료를 기반으로 wiki를 전문화하고, 매 반복마다 새 질문으로 다시 평가하는 것이다.

한 줄 요약:

```text
새 질문 평가 → 평균 점수 확인 → 미달 시 gap 분석 → 병렬 자료 수집 → raw-only 저장 → wiki ingest → 새 질문 재평가를 반복한다.
```

## 언제 사용하나

다음 요청에 사용한다.

- “wiki가 루브릭 90점을 넘을 때까지 자료를 보강해줘”
- “현재 wiki가 전문가 평가 기준을 통과하지 못하니 raw 자료를 수집해서 전문화해줘”
- “질문을 새로 만들고 wiki 답변을 채점해서 부족한 자료를 채워줘”
- “논문, PDF, 보고서, 제품 문서까지 수집해서 wiki를 고도화해줘”
- “평균 점수가 기준 미달이면 다시 수집하고 ingest하는 루프를 돌려줘”

## 언제 사용하지 않나

다음에는 이 스킬을 단독으로 사용하지 않는다.

- 단순히 URL 몇 개를 찾아달라는 요청
- wiki 없이 일반 답변만 평가하는 요청
- raw 자료 수집 없이 일반 지식으로 답변을 개선하려는 요청
- 이미 충분한 corpus가 있고 단일 질문만 답하면 되는 요청
- 법률, 금융, 의료 판단처럼 실제 사용자 또는 전문가 결정이 필요한 영역

## 변수

| 변수 | 기본값 | 설명 |
|---|---:|---|
| `domain` | 사용자 요청에서 결정 | wiki와 루브릭이 다루는 도메인 |
| `wiki_path` | 사용자 지정 | 대상 wiki root |
| `rubric_path` 또는 `rubric_text` | 사용자 지정 | 평가 루브릭 |
| `question_count` | 10 | 반복마다 새로 생성할 질문 수 |
| `target_average` | 90 | 종료 기준 평균 점수 |
| `max_iterations` | 10 | 무한 반복 방지용 최대 반복 수 |
| `source_batch_size` | 상황별 결정 | gap 보강을 위해 한 번에 수집할 후보 규모 |

`target_average`와 `question_count`는 기본값일 뿐이다. 사용자가 다른 값을 지정하면 그 값을 사용한다.

## 핵심 원칙

1. 질문은 매 반복마다 새로 생성한다.
2. 같은 질문을 재사용해서 평균점수를 올리지 않는다.
3. 현재 wiki에 있는 내용만 근거로 답변한다.
4. wiki에 없는 내용을 일반 지식으로 보충하지 않는다.
5. 평균 점수가 `target_average` 이상이면 종료한다.
6. 평균 점수가 `target_average` 미만이면 gap 분석 후 자료 수집과 wiki 보강을 진행한다.
7. 원본 자료는 반드시 `<wiki_path>/raw/*` 아래에만 저장한다.
8. `raw/` 외부에 원본 데이터를 저장하지 않는다.
9. raw 자료를 wiki 본문으로 반영할 때는 `llm-wiki` ingest 방식을 사용한다.
10. subagent 결과는 후보와 초안으로만 취급하고, 부모 에이전트가 검증한다.
11. 평균 계산은 반드시 도구로 수행한다.
12. keyword coverage만으로 루브릭 통과를 주장하지 않는다.

## 에이전트 격리 규칙

질문 생성, wiki 답변, 루브릭 채점은 반드시 서로 다른 신규 서브에이전트가 수행한다.

금지:

- 한 에이전트가 질문 생성 후 같은 컨텍스트에서 답변하는 것
- 한 에이전트가 질문 생성, 답변, 채점을 모두 수행하는 것
- 답변 에이전트가 루브릭을 보고 답변을 조정하는 것
- 답변 에이전트가 자기 답변을 채점하는 것
- 질문 생성 에이전트가 예상 답변이나 채점 기준을 함께 만드는 것
- 채점 에이전트가 답변을 수정하거나 새 근거를 추가하는 것
- 부모 에이전트가 편의를 위해 질문/답변/채점을 직접 한 번에 처리하는 것

허용:

- 부모 에이전트가 질문/답변/채점 산출물을 검증하는 것
- 부모 에이전트가 `final_score`를 파싱하고 평균을 계산하는 것
- 부모 에이전트가 gap을 종합하는 것
- 부모 에이전트가 다음 source discovery 계획을 세우는 것

이 규칙의 이유:

```text
질문 설계, 답변 생성, 판정이 같은 컨텍스트에 섞이면 평가가 오염된다.
종료조건은 독립적인 새 질문, 독립적인 답변, 독립적인 채점으로만 검증한다.
```

## 전체 루프

```text
1. 도메인 관련 질문 N개를 새로 생성한다.
2. 현재 wiki만 근거로 질문에 답변한다.
3. 답변을 루브릭으로 채점하고 평균을 계산한다.
4. 평균 점수가 target_average 이상이면 종료한다.
5. 평균 점수가 target_average 미만이면 부족한 근거/gap을 분석한다.
6. 질문에 답변할 수 있는 데이터를 raw/ 아래에만 수집한다.
7. 수집된 raw 자료를 ingest하여 wiki를 생성/보강한다.
8. 다시 새 질문 N개를 생성한다.
9. 새 질문으로 다시 답변/채점한다.
10. 3~9를 반복한다.
```

## 단계 0. 대상 wiki와 루브릭 확인

목적:

- 어떤 wiki를 전문화할지 확인한다.
- 어떤 루브릭으로 평가할지 확인한다.
- 현재 wiki 구조와 작성 규칙을 파악한다.

해야 할 일:

1. `wiki_path`를 확인한다.
2. `SCHEMA.md`, `index.md`, `log.md`가 있으면 먼저 읽는다.
3. wiki 구조가 없거나 대상이 모호하면 사용자에게 확인한다.
4. 루브릭 파일 또는 루브릭 텍스트를 확인한다.
5. `domain`, `question_count`, `target_average`, `max_iterations`를 확정한다.
6. 이전 반복 질문이 있다면 다음 질문 생성에서 제외할 수 있도록 목록화한다.

금지:

- wiki 구조를 모른 채 자료를 저장하지 않는다.
- `_meta` 사용을 기본 후보 관리 방식으로 확정하지 않는다.
- `_archive` 사용을 기본 동작으로 확정하지 않는다.
- schema 변경, archive, delete는 별도 승인 없이 수행하지 않는다.

## 단계 1A. 질문 생성 subagent 실행

질문 생성은 신규 서브에이전트 1개가 전담한다.

입력:

- `domain`
- `question_count`
- 이전 반복 질문 목록
- 현재 wiki의 넓은 범위 요약 또는 index 수준 정보

출력:

- Q01~QNN 질문
- 각 질문의 평가 의도
- 하위 도메인 커버리지
- 이전 질문과 중복되지 않는다는 자체 점검

규칙:

- 매 반복마다 새 질문을 생성한다.
- 질문 본문에는 루브릭 기준을 노출하지 않는다.
- 질문은 실제 실무자나 전문가가 물을 법해야 한다.
- 질문은 일반론 답변과 전문가 답변의 차이를 드러내야 한다.
- 질문 생성 에이전트는 답변하지 않는다.
- 질문 생성 에이전트는 채점하지 않는다.

## 단계 1B. 부모 에이전트의 질문 검증

부모 에이전트는 질문 생성 결과를 검증한다.

확인 항목:

- 질문 수가 `question_count`와 일치하는가
- 이전 반복 질문과 중복되지 않는가
- 도메인 하위 영역이 지나치게 편중되지 않았는가
- 질문 본문에 루브릭 기준이나 정답 힌트가 노출되지 않았는가

문제가 있으면 질문 생성 subagent를 다시 실행하거나 수정 요청한다. 부모 에이전트가 직접 질문을 완성하지 않는다.

## 단계 2A. Wiki 답변 subagent 실행

답변은 질문별 신규 서브에이전트가 전담한다.

기본 구조:

```text
Q01 → Wiki Answer Agent 01
Q02 → Wiki Answer Agent 02
...
Q10 → Wiki Answer Agent 10
```

도구 제한으로 모든 질문을 동시에 실행할 수 없으면 가능한 최대 병렬 수로 batch 처리한다.

입력:

- 질문 1개
- `wiki_path`
- wiki-only 답변 지침

출력:

- 질문별 답변
- 사용한 wiki 페이지 목록
- 사용한 source/provenance 목록
- 근거 부족 여부

규칙:

- 답변 에이전트는 질문 하나만 처리한다.
- 답변 에이전트는 루브릭을 보지 않는다.
- 답변 에이전트는 채점하지 않는다.
- wiki 밖 일반지식을 사용하지 않는다.
- raw에만 있고 wiki 본문으로 ingest되지 않은 내용은 최종 답변 근거로 사용하지 않는다.
- 근거가 부족하면 부족하다고 명시한다.

## 단계 2B. 부모 에이전트의 답변 검증

부모 에이전트는 답변 산출물을 검증한다.

확인 항목:

- 질문별 답변이 모두 존재하는가
- 각 답변이 해당 질문 하나에만 답했는가
- wiki 근거가 명시되어 있는가
- 근거 부족 답변은 부족하다고 표시했는가
- 루브릭이나 채점 내용이 답변에 섞이지 않았는가

서브에이전트의 “완료” 보고를 그대로 믿지 않는다. 파일 read-back, JSON/Markdown parse, 경로 확인 등으로 검증한다.

## 단계 3A. 루브릭 판정 subagent 실행

채점은 답변별 신규 서브에이전트가 전담한다.

기본 구조:

```text
Q01 답변 → Judge Agent 01
Q02 답변 → Judge Agent 02
...
Q10 답변 → Judge Agent 10
```

입력:

- 질문 1개
- 해당 질문의 답변
- 루브릭

출력:

- `final_score`
- 적용된 cap/gate
- 감점 사유
- evidence gap
- 다음 수집에 필요한 source type 제안

규칙:

- 채점 에이전트는 답변을 수정하지 않는다.
- 채점 에이전트는 새 근거를 추가하지 않는다.
- 채점 에이전트는 평균을 계산하지 않는다.
- 루브릭의 cap/gate를 엄격히 적용한다.
- `final_score`를 반드시 포함한다.

## 단계 3B. 부모 에이전트의 점수 검증 및 평균 계산

부모 에이전트가 수행한다.

해야 할 일:

1. 모든 점수 파일 또는 점수 결과가 존재하는지 확인한다.
2. 각 결과에서 `final_score`를 파싱한다.
3. 점수 범위와 숫자 타입을 검증한다.
4. 평균을 도구로 계산한다.
5. `average_score`와 `target_average`를 비교한다.
6. 결과를 기록한다.

종료조건:

```text
if average_score >= target_average:
    종료
else:
    단계 4로 진행
```

암산하거나 대략 계산하지 않는다.

## 단계 4. Gap 분석

목적:

- wiki가 왜 목표 평균점수를 넘지 못했는지 밝힌다.
- 낮은 점수를 만든 증거 부족 유형을 수집 가능한 source type으로 변환한다.

Gap 분류 예:

- 기본 개념 정의 부족
- 전문가 실무 디테일 부족
- 논문/학술 근거 부족
- 제품 문서/공식 문서 부족
- 수치 benchmark 부족
- case study 부족
- 비교/반례 부족
- 최신성 부족
- 루브릭 hard gate 충족 실패
- 질문에 직접 답하는 corpus 부재
- 회사별/도메인별 baseline 부재
- operational workflow 또는 implementation detail 부재

산출물:

- 질문별 gap
- 루브릭 cap/gate 실패 이유
- 필요한 source type
- 다음 source discovery shard 계획

## 단계 5. 병렬 source discovery

자료 조사는 병렬 subagent를 기본으로 한다.

원칙:

- 각 subagent는 파일을 쓰지 않는다.
- 각 subagent는 특정 shard만 조사한다.
- subagent 결과는 후보로만 취급한다.
- 부모 에이전트가 URL, 접근 가능성, 중복, source type을 검증한다.

권장 shard:

- academic papers
- arXiv / SSRN / NBER 등 공개 논문
- PDF
- industry reports
- official documentation
- product docs
- vendor docs
- public guides
- books / open textbooks
- annual reports
- benchmark reports
- standards / regulatory docs
- case studies
- transcripts / presentations

Source discovery 결과 schema:

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

## 단계 6. raw-only 자료 저장

절대 규칙:

```text
원본 자료는 반드시 <wiki_path>/raw/* 아래에만 저장한다.
raw/ 외부에 원본 데이터 저장 금지.
```

추가 품질 규칙:

- `saved` 파일도 부모 에이전트가 본문 품질을 검증한다.
- 404/page-not-found, SPA shell, CSS/JS dump, cookie wall, pricing shell처럼 관련 claim이 없는 저장물은 `invalid_content`로 분류하고 compiled page 근거로 쓰지 않는다.
- fetch report는 가능하면 `saved`, `exists`, `failed`, `invalid_content`를 분리한다.

저장 전 확인:

1. `wiki_path`가 맞는지 확인한다.
2. `SCHEMA.md`가 raw 구조를 정의하는지 확인한다.
3. 기존 `raw/` 하위 폴더를 확인한다.
4. 기존 구조가 있으면 따른다.
5. 구조가 없으면 사용자 승인 또는 최소 구조를 확인한다.

일반적 분류 예시:

- 웹 글: `raw/articles/`
- 보고서/guide/product docs: `raw/reports/`
- 논문/PDF/book: `raw/papers/`
- transcript: `raw/transcripts/`
- asset: `raw/assets/`

단, 이 하위 폴더 체계도 해당 wiki 구조를 확인한 뒤 사용한다.

금지:

- raw 자료를 `concepts/`, `entities/`, `queries/`, `comparisons/`에 직접 저장하지 않는다.
- `_meta`를 기본 후보 관리 폴더로 지정하지 않는다.
- `_archive`를 자동으로 사용하지 않는다.
- 수집하지 않은 자료를 수집한 것처럼 기록하지 않는다.
- title/abstract만 보고 raw 수집 완료로 간주하지 않는다.

Raw 저장 시 권장 frontmatter:

```yaml
---
source_url: https://example.com/source
ingested: YYYY-MM-DD
sha256: <body_sha256>
source_type: paper | report | product-doc | official-doc | article | book | case-study | transcript
questions: [Q01, Q03]
rubric_gaps: [evidence-gap-slug]
---
```

## 단계 7. wiki ingest / 생성 / 보강

수집된 raw 자료를 wiki 본문으로 반영할 때는 `llm-wiki` ingest 방식을 사용한다.

작업 원칙:

- 직접 지식을 생성하지 않는다.
- raw 자료 기반으로만 wiki 본문을 생성하거나 수정한다.
- 기존 페이지를 먼저 검색해 중복 생성을 막는다.
- 필요한 경우 concept/entity/comparison/query page를 생성한다.
- 기존 페이지에 새 근거를 추가할 때 `updated` 날짜를 갱신한다.
- 문단별 provenance marker를 사용한다.
- 여러 소스가 충돌하면 양쪽을 기록하고 confidence 또는 contested 상태로 표시한다.
- index와 log를 업데이트한다.

권장 provenance marker:

```text
주장 문장 또는 문단 끝에 ^[raw/.../source.md]
```

주의:

- raw에 저장된 자료를 읽지 않고 wiki 본문을 만들지 않는다.
- wiki에 없는 내용을 일반 지식으로 보강하지 않는다.
- 루브릭 점수를 맞추기 위해 근거 없는 내용을 추가하지 않는다.

## 단계 8. 새 질문으로 재평가

wiki ingest 후에는 다시 단계 1A로 돌아간다.

규칙:

- 이전 질문을 재사용하지 않는다.
- 새 질문 생성 subagent가 새 질문 N개를 만든다.
- 새 질문으로 wiki 답변을 생성한다.
- 새 판정 subagent가 채점한다.
- 부모 에이전트가 평균을 계산한다.
- `average_score >= target_average`이면 종료한다.
- 미달이면 다음 반복을 진행한다.

## 프롬프트 템플릿

### 질문 생성 subagent

```text
너는 질문 생성 전용 서브에이전트다.

도메인: {domain}
질문 개수: {question_count}
이전 질문 목록: {previous_questions}

새 질문 {question_count}개를 생성하라.

규칙:
- 절대 답변하지 마라.
- 절대 채점하지 마라.
- source discovery를 하지 마라.
- 이전 질문과 중복하지 마라.
- 질문 본문에 루브릭 기준이나 정답 힌트를 노출하지 마라.
- 도메인 하위 영역을 골고루 다뤄라.
- 일반론 답변과 전문가 답변의 차이가 드러나게 설계하라.

출력:
- Q번호
- 제목
- 질문
- 평가 의도
- 다루는 하위 영역
- 이전 질문과의 중복 회피 근거
```

### 위키 답변 subagent

```text
너는 wiki 답변 전용 서브에이전트다.

질문:
{question}

wiki_path:
{wiki_path}

규칙:
- 질문 하나에만 답하라.
- 루브릭을 보지 마라.
- 채점하지 마라.
- wiki 밖 일반지식을 사용하지 마라.
- raw에만 있고 wiki 본문으로 ingest되지 않은 내용은 최종 답변 근거로 사용하지 마라.
- 근거가 부족하면 충분한 근거가 없다고 명시하라.
- 사용한 wiki 페이지와 근거를 나열하라.

출력:
- 답변
- 사용한 wiki 페이지
- 근거 부족 여부
- 불확실한 부분
```

### 루브릭 판정 subagent

```text
너는 채점 전용 서브에이전트다.

질문:
{question}

답변:
{answer}

루브릭:
{rubric}

규칙:
- 답변을 수정하지 마라.
- 새 근거를 추가하지 마라.
- 평균을 계산하지 마라.
- 루브릭의 cap/gate를 엄격히 적용하라.
- 답변에 명시된 내용만 인정하라.
- final_score를 반드시 출력하라.

출력:
- final_score
- 적용된 cap/gate
- 주요 감점 사유
- evidence gap
- 다음 수집에 필요한 source type
```

### Source discovery subagent

```text
너는 source discovery 전용 서브에이전트다.

도메인: {domain}
담당 shard: {source_shard}
보강해야 할 gap: {gap_summary}
대상 질문: {target_questions}

규칙:
- 파일을 생성하거나 수정하지 마라.
- URL 후보와 근거 요약만 반환하라.
- 논문, PDF, report, product docs, official docs, book, benchmark, case study를 폭넓게 고려하라.
- 접근 불가, 403, paywall, 404, PDF 추출 실패 가능성을 표시하라.
- source title만 보고 충분하다고 판단하지 마라.

출력 schema:
- title
- source
- url
- source_type
- why_useful
- claim_snippet
- target_questions
- expected_rubric_gap
- access_status
- notes
```

## Source type 전략

루브릭 점수가 낮을 때 웹 글만 추가하면 wiki가 전문화되지 않는다. gap 유형에 따라 source type을 다양화한다.

> 참고: `references/rubric-v3-company-data-blocker-and-raw-validation.md`에는 marketing-expert-rubric-v3처럼 회사별 baseline/재무/실험 데이터 없이는 90점 통과를 주장할 수 없는 루브릭에서의 blocker 처리와 raw fetch 품질 검증 체크가 정리되어 있다.

- 정의/개념 부족: 교과서, open textbook, 표준 문서, 공식 docs
- 실무 운영 부족: product docs, vendor docs, implementation guide, case study
- 학술 근거 부족: peer-reviewed paper, arXiv, SSRN, NBER, 학회 발표자료
- 수치/benchmark 부족: industry report, benchmark report, annual report, dataset documentation
- 비교/반례 부족: analyst report, competing product docs, case comparison
- 최신성 부족: 최신 공식 release note, public roadmap, 최근 survey/report

## 승인 경계

읽기, 평가, 질문 생성, 계획 수립은 보통 승인 없이 수행할 수 있다.

다음은 사용자가 scope를 승인한 경우 진행할 수 있다.

- `raw/` 아래 자료 저장
- wiki 본문 ingest/update
- 질문/답변/채점 반복 실행

다음은 별도 explicit approval이 필요하다.

- `raw/` 외부에 원본 자료 저장
- schema 변경
- archive/delete
- cron/scheduler 등록
- external posting/delivery
- credential 사용
- paid/cost-incurring source 접근
- 대규모 구조 변경

## 검증 체크리스트

실행 중 또는 종료 전 반드시 확인한다.

- [ ] `wiki_path`가 명확하다.
- [ ] 루브릭이 명확하다.
- [ ] `target_average`가 설정됐다. 기본값은 90이다.
- [ ] `question_count`가 설정됐다. 기본값은 10이다.
- [ ] 이번 반복 질문은 새 질문 생성 subagent가 생성했다.
- [ ] 질문 생성 에이전트는 답변/채점을 하지 않았다.
- [ ] 질문은 이전 반복 질문과 중복되지 않는다.
- [ ] 답변은 질문별 신규 Wiki 답변 subagent가 생성했다.
- [ ] 답변 에이전트는 루브릭을 보지 않았다.
- [ ] 답변은 wiki 근거만 사용했다.
- [ ] 근거 부족 답변은 부족하다고 표시했다.
- [ ] 채점은 답변별 신규 판정 subagent가 수행했다.
- [ ] 채점 에이전트는 답변을 수정하지 않았다.
- [ ] 모든 score에 `final_score`가 있다.
- [ ] 평균은 도구로 계산했다.
- [ ] `average_score`와 `target_average`를 비교했다.
- [ ] 미달 시 gap 분석을 했다.
- [ ] 자료 조사는 병렬 source discovery subagent로 수행했다.
- [ ] subagent 결과를 부모가 검증했다.
- [ ] 원본 자료는 `raw/` 아래에만 저장했다.
- [ ] `_meta`, `_archive`를 기본 경로로 사용하지 않았다.
- [ ] wiki 본문은 raw 기반으로만 ingest했다.
- [ ] index/log 업데이트를 확인했다.
- [ ] 다음 반복에서는 새 질문을 생성했다.

## 흔한 함정

1. 한 에이전트가 질문 생성, 답변, 채점을 모두 수행하는 것
   - 평가 오염이 발생한다. 반드시 신규 서브에이전트를 분리한다.

1-1. target_average 미달을 공개 자료 수집만으로 억지 통과 처리하는 것
   - 루브릭이 회사별 baseline, 재무 수치, 경쟁자별 win/loss, 실험 표본/MDE 같은 private/company-specific data를 요구하면 공개 corpus 보강 후에도 `pass=false`로 보고한다. 필요한 데이터 체크리스트를 산출하고, 실제/익명화 baseline data 또는 명시 승인된 가상 baseline scenario 없이는 90점 통과를 주장하지 않는다.

1-2. raw fetch 성공을 본문 품질 성공으로 간주하는 것
   - 200 응답이나 파일 저장은 충분하지 않다. 404 page, SPA shell, CSS/JS dump, generic landing page가 저장될 수 있다. 부모 에이전트가 샘플 read-back, error 문자열 검색, claim 존재 확인으로 `invalid_content`를 분리한 뒤 compiled page에 반영한다.

2. 같은 질문으로 반복 평가하는 것
   - 종료조건 검증은 항상 새 질문 세트로 한다.

3. wiki 밖 일반 지식으로 답변을 보강하는 것
   - 이 workflow의 목적은 wiki 전문화다. 근거가 없으면 raw 수집과 ingest로 해결한다.

4. raw 외부에 원본 자료를 저장하는 것
   - 원본 데이터는 반드시 `raw/` 아래에만 저장한다.

5. source title이나 abstract만 보고 충분하다고 판단하는 것
   - 실제 접근 가능성과 본문 claim을 확인한다.

6. subagent 결과를 그대로 믿는 것
   - 부모가 URL, 파일, 점수, 평균을 직접 검증한다.

7. keyword coverage로 90점 통과를 주장하는 것
   - 루브릭의 cap/gate와 실제 답변 품질로 판단한다.

8. `_meta` 또는 `_archive`를 관성적으로 사용하는 것
   - 해당 wiki의 schema나 사용자 승인 없이 기본 workflow로 확정하지 않는다.

9. 평균을 암산하는 것
   - 평균은 반드시 도구로 계산한다.

## 보고 형식

최종 보고는 간결하게 작성한다.

```text
결론:
- average_score: X
- target_average: Y
- 상태: 통과 / 미달 / max_iterations 도달

수행한 것:
- 질문 생성: N개, 신규 여부 확인
- wiki 답변: N개
- 채점: N개
- 자료 수집: raw 아래 N개
- wiki ingest/update: 파일 목록

검증 결과:
- final_score 파싱 여부
- 평균 계산 방법
- raw-only 저장 확인
- index/log 업데이트 확인

남은 문제:
- 부족한 source type
- 루브릭 hard gate 미충족 항목
- 사용자 승인 필요 사항

다음 단계:
- 종료 / 다음 iteration / 추가 자료 수집 / schema 승인 필요
```

## 기억할 것

```text
질문 생성, 답변, 채점은 절대 한 에이전트에서 하지 않는다.
매 반복마다 새 질문을 만든다.
원본 자료는 raw/ 아래에만 저장한다.
wiki 본문은 raw 근거로만 ingest한다.
평균은 도구로 계산한다.
목표 평균점수는 변수이며 기본값은 90이다.
질문 수는 변수이며 기본값은 10이다.
```
