# LLM Wiki 품질 루브릭 게이트 감사

사용자가 `llm-wiki`를 ad-hoc health check가 아니라 재사용 가능한 품질 기준으로 점검, 인증, 강화, 개선해 달라고 요청할 때 이 참고 문서를 사용한다.

## 핵심 교훈

wiki 상태점검은 자유 형식 narrative가 되어서는 안 된다. 먼저 고정 루브릭을 정의하고, 구조/source integrity gate는 deterministic check로 검사한 뒤, 완전히 자동화할 수 없는 차원에만 정성 리뷰를 적용한다.

이 사용자의 `llm-wiki` 품질 통과 기준은 높고 gate 기반이다.

- baseline passing score: `95 / 100`
- hard gate는 “괜찮음”이 아니라 만점이어야 한다.
  - D1 Wiki Structure & Navigation: `15 / 15`
  - D2 Page-Level Schema Compliance: `15 / 15`
  - D3 Link Graph & Knowledge Connectivity: `15 / 15`
  - D4 Source Integrity & Provenance: `20 / 20`
- D1-D4 중 하나라도 감점되면 원점수가 90점 이상이어도 인증 실패다.
- cap/gate가 적용되면 raw score와 certification score를 모두 보고한다.

## 권장 루브릭 차원

1. Wiki Structure & Navigation — 15 hard-gate points
   - 필수 root file과 directory.
   - index page count 일치.
   - 모든 compiled page가 `index.md`에 등재됨.
   - stale/extra index link 없음.
   - `log.md`가 비어 있지 않음.

2. Page-Level Schema Compliance — 15 hard-gate points
   - 유효한 frontmatter.
   - 필수 field: `title`, `created`, `updated`, `type`, `tags`, `sources`.
   - 유효한 `type` enum.
   - tag는 `SCHEMA.md` taxonomy에 있어야 함.
   - source field는 비어 있지 않고 구조적으로 유효해야 함.
   - 한국어 wiki의 non-proper-noun 제목은 한국어 우선이어야 함.

3. Link Graph & Knowledge Connectivity — 15 hard-gate points
   - graph에는 `entities/`, `concepts/`, `comparisons/`, `queries/` 아래 compiled page만 포함한다.
   - source-text noise를 피하기 위해 `raw/`, `_meta/`, schema 예시는 broken-link/orphan 검사에서 제외한다.
   - compiled-page broken wikilink가 없어야 한다.
   - 모든 compiled page는 최소 2개 outbound wikilink를 가져야 한다.
   - 설명 없는 orphan compiled page가 없어야 한다.
   - query/comparison page는 concept/entity/comparison으로 다시 연결되어야 한다.

4. Source Integrity & Provenance — 20 hard-gate points
   - 모든 raw markdown source에 frontmatter가 있어야 한다.
   - 필수 raw field: `ingested`, `sha256`, 그리고 `source_url` 또는 문서화된 local/manual `source_ref`.
   - raw hash는 frontmatter 뒤의 project-normalized body로 재계산한다. marketing wiki에서는 `body.lstrip("\n")`가 맞는 normalization이었다.
   - scalar `sha256` 값은 비교 전에 quote를 제거한다.
   - compiled page는 source를 인용해야 한다.
   - multi-source compiled page에는 추적성이 필요하다. `^[raw/...]` 같은 paragraph marker 또는 raw file로 클릭 가능한 link를 포함한 `## 출처 추적`/`## 출처 보강` 섹션을 둔다.
   - fetch failure/exclusion은 `log.md` 또는 `_meta` report에 기록해야 한다.

5. Corpus Coverage & Domain Fit — 15 quality points
   - `SCHEMA.md`와 domain alignment.
   - raw cluster가 compiled page에 반영됨.
   - 반복 등장하는 decision-relevant entity/concept가 승격되었거나 명시적으로 보류됨.
   - page type mix가 설명 가능함.
   - 주요 use case/question에 evidence coverage가 있음.
   - corpus gap이 문서화됨.

6. Synthesis Quality & Non-Generic Knowledge — 10 quality points
   - page가 source dump가 아니라 재사용 가능한 knowledge unit임.
   - multi-source synthesis와 decision rule/tradeoff가 드러남.
   - uncertainty, limitation, confidence, contested claim이 필요할 때 드러남.
   - 긴 query/deep-dive page는 탐색 가능하거나 분할됨.

7. Maintenance, Auditability & Evolution — 10 quality points
   - operation이 log에 기록됨.
   - log rotation이 건강함.
   - `_meta` 재현 artifact가 있음.
   - weak/contested/stale review surface가 있음.
   - large ingest에 validation report가 있음.
   - audit output이 path-specific recommendation을 제공함.

## Deterministic checker 패턴

최소한 다음 field를 갖는 stable JSON scorecard를 출력하는 checker를 만들거나 재사용한다.

```json
{
  "wiki_path": "string",
  "evaluated_at": "YYYY-MM-DDTHH:mm:ssZ",
  "read_only": true,
  "rubric_version": "llm-wiki-quality-v1",
  "baseline_passing_score": 95,
  "raw_total_score": 0,
  "certification_score": 0,
  "max_score": 100,
  "pass": false,
  "hard_gates": [],
  "dimension_scores": [],
  "counts": {},
  "issues": [],
  "unverified": [],
  "next_actions": []
}
```

checker는 기본적으로 read-only여야 한다. 사용자가 통과할 때까지 고치라고 요청한 경우에만 wiki를 수정하고, checker를 재실행하며, 최종 scorecard를 `_meta/` 아래에 저장한다.

## Gate 통과를 위한 흔한 수정

- D1 index mismatch: compiled page 추가/삭제 후 `index.md` entry와 page count를 갱신한다.
- D2 taxonomy failure: 반복적으로 필요하고 정당한 tag라면 `SCHEMA.md` taxonomy에 추가하고, 그렇지 않으면 기존 taxonomy tag로 교체한다.
- D2 English-only title: 한국어 wiki의 설명형 page title/H1은 한국어 우선으로 바꾼다. filename/slug는 별도 기준으로 함께 점검한다.
- D2 English-only descriptive filename: 한국어 wiki의 설명형 `concepts/`, `comparisons/`, `queries/` filename/slug는 한국어를 포함하도록 rename하고, 모든 `[[wikilink]]`와 `index.md`를 함께 갱신한다. Proper noun entity filename은 영어 허용이다.
- D3 orphan page: concept/comparison/query page에서 의미 있는 inbound link를 추가한다. checker만 만족시키기 위한 random link는 금지한다.
- D3 large raw corpus인데 `entities/`가 비어 있음: 반복 등장 company/platform/source를 위한 core entity page를 소수 생성하거나 deliberate concept-first policy를 문서화한다.
- D4 raw hash drift: 먼저 normalization을 확인한다. body가 그대로인데 stored hash metadata만 stale이면 raw frontmatter hash를 업데이트한다. 명시 요청 없이 raw body content를 수정하지 않는다.
- D4 multi-source provenance: 3개 이상 source를 종합한 compiled page에 `## 출처 추적` section을 추가하거나 paragraph-level provenance marker를 사용한다. raw path는 반드시 clickable link여야 한다.
- D4 supplemental source section: `## 출처 보강` 같은 섹션의 raw path도 clickable Markdown/Obsidian link로 바꾼다.
- D6 long query page: 유지한다면 강한 section structure를 보장하고, 아니면 더 작은 query/comparison page로 분할한다.

## 검증 절차

1. checker를 실행하고 baseline을 캡처한다.
2. 가장 우선순위가 높은 failing gate만 먼저 고친다: D1 → D2 → D3 → D4.
3. 각 batch 후 checker를 다시 실행한다.
4. hard gate가 통과한 뒤에만 D5-D7을 작업한다.
5. 최종 scorecard를 `_meta/llm-wiki-quality-score-YYYY-MM-DD.json`에 저장한다.
6. 사용자가 read-only를 명시하지 않았다면 `lint` 또는 `update` log entry를 append한다.
7. 최종 보고에는 다음을 포함한다.
   - 생성/수정한 path
   - final total/certification score
   - hard-gate table
   - issue count
   - scorecard path
   - 한계 또는 heuristic assumption

## 주의사항

- raw source 안의 `[[...]]` 문자열을 compiled-page broken-link 검사에 섞지 않는다.
- `entities/` = 0 자체를 구조 오류로 취급하지 않는다. schema/purpose가 entity page를 요구하지 않는 한 coverage gap으로 다룬다. 단, 사용자가 95점 gate를 설정하면 entity coverage 수정이 필요할 수 있다.
- narrative review만으로 인증을 주장하지 않는다. machine-readable checker output 또는 stable scorecard를 요구한다.
- 사용자가 rubric을 외부에 유지하라고 한 상태에서는 `llm-wiki` skill 자체를 업데이트하지 않는다. 사용자가 나중에 skill library 업데이트를 요청하거나 rubric 검증 후 반영을 승인한 때만 skill reference를 추가한다.
