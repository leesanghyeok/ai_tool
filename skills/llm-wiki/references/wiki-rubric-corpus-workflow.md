# Wiki 기반 리서치 corpus 구축 + 루브릭 종료조건 처리

이 참고 파일은 사용자가 특정 wiki의 내용만으로 고품질 답변을 만들라고 하면서, 외부 자료 수집과 평가 루브릭/종료조건을 함께 준 경우의 운영 패턴이다.

## 핵심 원칙

1. **wiki-only 답변과 skill 지식 구분**
   - `llm-wiki` 스킬은 절차 지식이다. 도메인 근거가 아니다.
   - `SCHEMA.md` taxonomy도 답변 근거가 아니라 분류/범위 정보다.
   - 실제 답변 근거는 `concepts/`, `entities/`, `comparisons/`, `queries/`의 본문과 그 sources뿐이다.

2. **근거가 없으면 먼저 부족하다고 말한다**
   - index가 비어 있거나 관련 페이지가 없으면 구체 전략을 추론하지 않는다.
   - 사용자가 외부 자료 수집을 승인하면 그때 raw 수집→ingest→답변으로 진행한다.

3. **대량 자료 수집은 manifest 중심**
   - `_meta/source-manifest-*.json`에 `cluster`, `questions`, `title`, `url`을 둔다.
   - fetch script는 URL을 `raw/articles/<cluster>/slug.md`에 저장한다.
   - raw frontmatter: `source_url`, `fetched_via`, `ingested`, `sha256`, `cluster`, `questions`, `title`.
   - 실패 URL은 `_meta/*fetch-report*.json`와 `_meta/fetch-failures/`에 남긴다.

4. **subagent는 후보/초안 생산자, 부모가 검증자**
   - subagent에는 “파일 쓰기 금지” 리서치 워커를 보내 URL 후보와 핵심 claim만 받는다.
   - 답변 초안 워커가 파일을 쓰게 할 수 있지만, 부모가 반드시 읽고 최종 `queries/`에 병합한다.
   - child summary는 성공 증거가 아니므로, 부모가 파일 존재·내용·링크·검증 report를 확인한다.

5. **루브릭 점수 목표의 정직한 한계**
   - 루브릭이 회사별 baseline, CAC/LTV/payback, 표본/MDE, 경쟁자별 battlecard, 실제 cohort 데이터를 요구하면 공개 자료만으로 엄격한 90점 달성을 선언하지 않는다.
   - 산출물을 세 가지로 분리한다:
     - 공개 근거 corpus: raw + concept/comparison pages
     - wiki 기반 답변 템플릿/초안: `queries/`
     - 90점 달성용 실제 데이터 체크리스트: `_meta/required-data-*.md`
   - 허위 수치나 임의 baseline을 만들어 종료조건을 만족한 것처럼 말하지 않는다.

## 권장 검증

- raw 저장 수와 실패 수 확인.
- `index.md` page count 업데이트.
- wikilink broken link 검사.
- 각 답변에 decision question, numeric rule, unit economics, experiment design, risk/pivot, segment, competition/alternative, do-not-do, wiki citation이 있는지 자동 검사.
- 자동 검사는 hard-cap 누락 감지용일 뿐, 루브릭 90점 판정은 별도 의미 리뷰가 필요하다.

## 보고 형식

- “완료”와 “달성 불가/추가 데이터 필요”를 분리한다.
- 예: “raw 110개, concept 15개, query 1개 생성 및 링크 검증 완료. 다만 루브릭 v3가 회사별 baseline을 요구하므로 공개 자료만으로 20문항 모두 90점 달성은 선언할 수 없음.”
