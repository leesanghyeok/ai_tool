# 한국어 compiled filename/slug rename runbook

한국어 wiki에서 사용자가 파일 탐색성/직관성을 문제 삼으면 `title:`/H1만 한국어화하지 말고 compiled page filename/slug까지 확인한다.

## 적용 범위

- Rename 대상: 설명형 compiled page
  - `concepts/*.md`
  - `comparisons/*.md`
  - `queries/*.md`
- 보통 유지:
  - proper noun entity filename: `entities/google.md`, `entities/meta.md`, `entities/airbnb.md`
  - raw source path: `raw/articles/...`, `raw/reports/...`, `raw/papers/...`
  - YAML/frontmatter key, enum, tag, JSON key, command

## 절차

1. Orientation: `SCHEMA.md`, `index.md`, 최근 `log.md`를 읽는다.
2. compiled page 목록과 각 page의 `title:`을 추출한다.
3. old path → new Korean slug path mapping을 만든다.
   - 예: `concepts/b2b-saas-funnel-economics.md` → `concepts/b2b-saas-퍼널-경제성과-gtm-진단.md`
   - 약어/고유 technical term은 혼합 허용: `b2b-saas`, `gtm`, `plg`, `pql`, `dtc`.
4. rename 전에 non-raw markdown에서 old `[[wikilink]]`를 new `[[wikilink]]`로 바꾼다.
5. 파일을 rename한다.
6. `index.md`를 새 slug로 갱신한다.
7. `SCHEMA.md` 작성 규칙에 한국어 compiled filename 정책을 반영한다.
8. compiled page가 아닌 초안/질문 artifact가 `queries/`에 있으면 `_meta/drafts/`로 옮긴다. `queries/`는 frontmatter/source가 있는 compiled query만 둔다.
9. `log.md`에 rename과 보존/이동 사항을 기록한다.
10. checker를 재실행하고 D1-D4 hard gate가 모두 통과하는지 확인한다.

## 검증 포인트

- old slug wikilink 검색 결과 0건.
- `index.md` declared page count와 실제 compiled page count 일치.
- D2 `korean_first_compiled_filename_slug` 통과.
- D3 broken link/orphan 0건.
- D4 raw provenance는 rename과 무관하게 계속 clickable이어야 한다.

## Pitfalls

- `title:`만 한국어화하면 Obsidian/file explorer에서 영어 slug가 그대로 보여 사용자가 원하는 탐색성 개선이 안 된다.
- `queries/`에 frontmatter 없는 질문 초안이 있으면 checker가 compiled page로 잡아 D1/D2/D3/D4를 망가뜨린다. 이런 파일은 `_meta/drafts/`로 이동한다.
- checker 내부에 특정 old slug를 하드코딩한 heuristic이 있으면 rename 후 실패한다. page count/type/content 기반 heuristic으로 바꾼다.
