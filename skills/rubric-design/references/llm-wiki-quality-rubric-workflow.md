# LLM Wiki 품질 루브릭 워크플로우

`llm-wiki` health checks와 quality certification을 위한 rubrics를 설계하거나 개정할 때 이 reference를 사용한다.

## 핵심 패턴

- 100-point rubric을 사용하고, certification에는 보통 95/100처럼 높은 passing baseline을 둔다.
- hard-gated structural/source-integrity dimensions와 더 부드러운 corpus/synthesis quality dimensions를 분리한다.
- checklist items를 먼저 채점한 뒤 local caps, global caps, certification rule 순서로 적용한다.
- 재사용 가능한 rubric은 per-wiki scorecards나 calibration results와 별도로 저장한다.

## 권장 hard gates

llm-wiki certification에서는 다음 dimensions가 full marks를 요구해야 한다:

1. Wiki Structure & Navigation
   - 필수 root files와 directories
   - index count consistency
   - 모든 compiled page가 indexed됨
   - populated log
2. Page-Level Schema Compliance
   - valid frontmatter
   - required fields
   - valid type enum
   - taxonomy-valid tags
   - wiki에 적합한 human-facing title language
3. Link Graph & Knowledge Connectivity
   - broken compiled-page wikilinks 없음
   - minimum outbound links
   - unexplained orphan pages 없음
   - query/comparison pages가 concepts/entities로 다시 연결됨
4. Source Integrity & Provenance
   - raw frontmatter
   - raw `source_url` 또는 문서화된 `source_ref`
   - raw `sha256`
   - compiled pages가 sources를 cite함
   - source references가 resolve됨
   - multi-source synthesis에 clickable provenance links가 있음

hard gate 중 하나라도 points를 잃으면, raw score가 90+라도 certification은 fail이어야 한다.

## 출처 추적 규칙

다음과 같은 단순 raw paths만으로는 full provenance credit을 주지 않는다:

```markdown
- `raw/articles/source.md`
```

예를 들어 다음과 같은 clickable Markdown/Obsidian links를 요구한다:

```markdown
- [raw/articles/source.md](../raw/articles/source.md)
- [[raw/articles/source]]
```

paragraph-level claims의 경우, wiki convention상 navigable하다면 `^[raw/articles/source.md]` 같은 provenance markers도 허용할 수 있다.

## 한국어 wiki 제목 규칙

Korean-language wikis의 경우:

- Descriptive concept/comparison/query page titles는 frontmatter `title:`와 H1에서 Korean-first여야 한다.
- Stable filenames/slugs, YAML keys, enum values, tags, raw paths, commands, API identifiers는 machine-compatible 상태로 유지해야 한다.
- Proper nouns는 English로 남겨도 된다: `Google`, `Meta`, `Airbnb`, `OpenView`, `Bessemer` 등.
- English-only non-proper-noun titles가 configured threshold를 초과하면 hard-gate issue 또는 cap을 유발해야 한다.

## Deterministic checker 지침

checker가 안정적으로 검증할 수 있는 항목:

- required file/directory existence
- index count와 membership
- frontmatter presence와 required fields
- enum values와 tag taxonomy
- compiled-page wikilink graph
- orphan pages
- raw frontmatter와 hash drift
- source path resolution
- clickable provenance links
- title-language heuristics
- log entries와 `_meta` artifact presence

judge-only/heuristic parts는 명시적으로 유지한다. checker가 quality dimensions에 heuristics를 사용한다면 comments와 evidence에 heuristics라고 label한다.

## Scorecard 구조

유용한 scorecard에는 다음이 포함된다:

```json
{
  "wiki_path": "string",
  "rubric_version": "llm-wiki-quality-v1",
  "baseline_passing_score": 95,
  "raw_total_score": 0,
  "certification_score": 0,
  "pass": false,
  "hard_gates": [],
  "dimension_scores": [],
  "issues": [],
  "counts": {},
  "unverified": [],
  "next_actions": []
}
```

## 흔한 함정

- clickable하지 않은 source-trace paths를 충분하다고 취급하는 것.
- total score가 높다는 이유로 hard-gate dimensions를 partial credit 상태에서 통과시키는 것.
- Korean wikis에서 proper-noun English titles를 감점하는 것; descriptive/non-proper titles만 Korean-first여야 한다.
- raw source link noise를 compiled-page broken-link checks에 섞는 것.
- baseline scorecard를 canonical rubric의 일부인 것처럼 저장하는 것.
