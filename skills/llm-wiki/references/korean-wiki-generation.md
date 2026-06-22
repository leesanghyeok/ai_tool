# 한국어 Wiki·Skill·Rubric 생성/번역

`llm-wiki` 관련 생성물이나 운영 문서를 한국어화할 때 사용한다. 적용 대상은 wiki 초기화 문서뿐 아니라 skill reference, 품질 루브릭, scorecard 설명 문서까지 포함한다.

## 목표

대화가 한국어이거나 사용자가 한국어 출력을 명시적으로 요청한 경우, 사람이 읽는 부분은 한국어로 작성한다.

- `SCHEMA.md`: heading, 설명 prose, comment, machine identifier가 아닌 예시
- `index.md`: title, guidance block, section heading, comment
- `log.md`: title, guidance block, 초기 log subject/body
- `entities/`, `concepts/`, `comparisons/`, `queries/` 아래 wiki page: 본문 prose, section heading, index summary, log description, 설명형 compiled page filename/slug
- skill/reference 문서: 설명 prose, heading, pitfall, 절차 설명
- rubric 문서: 평가 목적, 평가 대상, 통과 기준, 채점 기준 설명, cap 규칙, score interpretation, judge 지침

## 호환성을 위해 유지할 것

사용자가 명시적으로 요구하지 않는 한 machine-readable 또는 integration-sensitive surface는 번역하지 않는다.

- 환경변수: `WIKI_PATHS`, `WIKI_DEFAULT`, `WIKI_PATH`
- root 파일/디렉터리명: `SCHEMA.md`, `index.md`, `log.md`, `raw/`, `entities/`, `concepts/`, `comparisons/`, `queries/`, `_meta/`
- YAML/frontmatter key: `title`, `created`, `updated`, `type`, `tags`, `sources`, `confidence`, `source_url`, `sha256`
- enum/action 값: `entity`, `concept`, `comparison`, `query`, `summary`, `high`, `medium`, `low`, `ingest`, `update`, `query`, `lint`, `create`, `archive`, `delete`
- JSON schema key와 enum 값: `wiki_path`, `raw_total_score`, `certification_score`, `dimension_scores`, `hard_gates`, `criterion_id`, `grade`, `excellent | strong_not_passing | adequate | weak | unacceptable`
- code block, command, path, URL, placeholder, taxonomy에서 사용하는 tag 값
- `source discovery`, `subagent`, `hard gate`, `final_score`처럼 workflow identifier 성격이 강한 technical term은 필요하면 영어를 유지한다.

`title:`은 human-facing field이므로 한국어로 쓸 수 있다. 한국어 wiki의 설명형 compiled page filename/slug도 한국어 우선으로 쓴다. `type`, `tags`, `sources` 같은 구조 field는 schema를 따른다.


## 한국어 compiled filename/slug 규칙

한국어 wiki에서는 설명형 compiled page의 파일명도 독자가 바로 의미를 이해할 수 있어야 한다.

- `concepts/`, `comparisons/`, `queries/` 아래 page filename/slug는 한국어를 포함한다.
- 약어와 고유 technical term은 섞어 쓸 수 있다. 예: `b2b-saas-퍼널-경제성과-gtm-진단.md`.
- `entities/` 아래 Google, Meta, Airbnb 같은 proper noun entity filename은 영어를 허용한다.
- `raw/` source filename/path는 재현성과 source traceability를 위해 기존 영어 slug를 유지할 수 있다.
- filename rename 시 모든 `[[wikilink]]`, `index.md`, 필요 시 checker alias를 함께 갱신하고 검증한다.
- 루브릭/체커 반영 시 title/H1 검사와 filename/slug 검사를 분리한다. title이 한국어여도 filename이 English-only면 D2 hard gate 실패로 잡아야 한다.

## 루브릭 번역 규칙

1. 루브릭 prose는 한국어로 번역하되 checker/scorecard와 연결되는 identifier는 유지한다.
2. D1-D7 같은 dimension ID와 score 값은 절대 바꾸지 않는다.
3. JSON scorecard schema는 key를 번역하지 않는다.
4. `pass`, `grade`, `gate_type`, `severity`, `priority` 같은 machine enum은 유지한다.
5. 번역 후 실제 checker로 대상 wiki를 다시 검증해, 번역이 절차/해석을 깨지 않았는지 확인한다.
6. read-only 검증 요청이면 scorecard를 임시 경로에만 만들고 `_meta/` 저장이나 `log.md` append는 하지 않는다.

## Clickable raw source 규칙

`## 출처 추적`뿐 아니라 `## 출처 보강` 같은 supplemental source section도 raw path가 클릭 가능해야 한다.

불충분:

```markdown
추가 근거: raw/articles/source.md
추가 근거: `raw/articles/source.md`
```

권장:

```markdown
추가 근거: [raw/articles/source.md](../raw/articles/source.md)
```

checker는 compiled page body 안의 plain/backticked `raw/...md`를 D4 issue로 잡아야 한다. 단, frontmatter `sources:` field의 raw path는 machine-readable source list이므로 clickable body link 검사 대상에서 제외한다.

## 검증 체크리스트

localization 변경 후 다음을 확인한다.

1. Markdown code fence 개수를 세고 짝수인지 확인한다.
2. `git diff --check`로 whitespace error를 확인한다.
3. 생성된 한국어 template에 남아 있으면 안 되는 영어 template phrase를 검색한다.
   - `# Wiki Schema`
   - `# Wiki Index`
   - `# Wiki Log`
   - `Content catalog`
   - `Chronological record`
   - `Every wiki page starts`
   - `Actions: ingest`
   - `Wiki initialized`
   - `Page Title`
   - `from taxonomy below`
   - `Optional quality signals`
   - `Page Thresholds`
   - `Update Policy`
   - `Evaluation Purpose`
   - `Evaluation Target`
   - `Passing Standard`
   - `Dimension Summary`
   - `Detailed Scoring Criteria`
   - `Scoring Procedure`
   - `Judge Instructions`
   - `Score Interpretation`
4. 필수 호환성 term이 남아 있는지 확인한다.
   - `WIKI_PATHS`
   - `WIKI_DEFAULT`
   - `WIKI_PATH`
   - `type: entity | concept | comparison | query | summary`
   - `confidence: high | medium | low`
   - `source_url`
   - `sha256`
   - `wiki_path`
   - `raw_total_score`
   - `certification_score`
   - `dimension_scores`
   - `hard_gates`
   - `criterion_id`
5. frontmatter에 필요한 skill metadata key가 유지되는지 확인한다.
6. 루브릭 번역 후에는 checker를 실제 대상 wiki에 실행하고 `pass`, `certification_score`, hard gate 결과를 보고한다.
