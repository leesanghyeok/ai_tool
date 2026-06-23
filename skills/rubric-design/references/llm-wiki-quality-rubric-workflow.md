# LLM Wiki Quality Rubric Workflow

Use this reference when designing or revising rubrics for `llm-wiki` health checks and quality certification.

## Core pattern

- Use a 100-point rubric with a high passing baseline, usually 95/100 for certification.
- Separate hard-gated structural/source-integrity dimensions from softer corpus/synthesis quality dimensions.
- Score checklist items first; apply local caps, global caps, then the certification rule.
- Store the reusable rubric separately from per-wiki scorecards or calibration results.

## Recommended hard gates

For llm-wiki certification, these dimensions should require full marks:

1. Wiki Structure & Navigation
   - required root files and directories
   - index count consistency
   - every compiled page indexed
   - populated log
2. Page-Level Schema Compliance
   - valid frontmatter
   - required fields
   - valid type enum
   - taxonomy-valid tags
   - human-facing title language appropriate to the wiki
3. Link Graph & Knowledge Connectivity
   - no broken compiled-page wikilinks
   - minimum outbound links
   - no unexplained orphan pages
   - query/comparison pages connect back to concepts/entities
4. Source Integrity & Provenance
   - raw frontmatter
   - raw `source_url` or documented `source_ref`
   - raw `sha256`
   - compiled pages cite sources
   - source references resolve
   - multi-source synthesis has clickable provenance links

If any hard gate loses points, certification should fail even if the raw score is 90+.

## Provenance rule

Do not award full provenance credit for plain raw paths such as:

```markdown
- `raw/articles/source.md`
```

Require clickable Markdown/Obsidian links, for example:

```markdown
- [raw/articles/source.md](../raw/articles/source.md)
- [[raw/articles/source]]
```

For paragraph-level claims, provenance markers such as `^[raw/articles/source.md]` are also acceptable if the wiki convention makes them navigable.

## Korean wiki title rule

For Korean-language wikis:

- Descriptive concept/comparison/query page titles should be Korean-first in frontmatter `title:` and H1.
- Stable filenames/slugs, YAML keys, enum values, tags, raw paths, commands, and API identifiers should stay machine-compatible.
- Proper nouns may remain English: `Google`, `Meta`, `Airbnb`, `OpenView`, `Bessemer`, etc.
- English-only non-proper-noun titles should trigger a hard-gate issue or cap when they exceed the configured threshold.

## Deterministic checker guidance

A checker can reliably verify:

- required file/directory existence
- index count and membership
- frontmatter presence and required fields
- enum values and tag taxonomy
- compiled-page wikilink graph
- orphan pages
- raw frontmatter and hash drift
- source path resolution
- clickable provenance links
- title-language heuristics
- log entries and `_meta` artifact presence

Keep judge-only/heuristic parts explicit. If a checker uses heuristics for quality dimensions, label them as heuristics in comments and evidence.

## Scorecard shape

A useful scorecard includes:

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

## Common pitfalls

- Treating source-trace paths as sufficient when they are not clickable.
- Letting hard-gate dimensions pass with partial credit because the total score is high.
- Penalizing proper-noun English titles in Korean wikis; only descriptive/non-proper titles should be Korean-first.
- Mixing raw source link noise into compiled-page broken-link checks.
- Saving a baseline scorecard as if it were part of the canonical rubric.
