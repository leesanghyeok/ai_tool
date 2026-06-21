# Korean Wiki Generation

Use this reference when updating or verifying the `llm-wiki` skill's Korean localization behavior.

## Goal

When the conversation is Korean, or the user explicitly asks for Korean output, newly initialized wiki files should be human-readable in Korean by default:

- `SCHEMA.md`: headings, explanatory prose, comments, examples that are not machine identifiers
- `index.md`: title, guidance block, section headings, comments
- `log.md`: title, guidance block, initial log subject/body
- Future wiki pages under `entities/`, `concepts/`, `comparisons/`, `queries/`: body prose, section headings, index summaries, log descriptions

## Preserve for compatibility

Do not translate machine-readable or integration-sensitive surfaces unless the user explicitly asks:

- Environment variables: `WIKI_PATHS`, `WIKI_DEFAULT`, `WIKI_PATH`
- File and directory names: `SCHEMA.md`, `index.md`, `log.md`, `raw/`, `entities/`, `concepts/`, `comparisons/`, `queries/`
- YAML/frontmatter keys: `title`, `created`, `updated`, `type`, `tags`, `sources`, `confidence`, `source_url`, `sha256`
- Enum/action values: `entity`, `concept`, `comparison`, `query`, `summary`, `high`, `medium`, `low`, `ingest`, `update`, `query`, `lint`, `create`, `archive`, `delete`
- Code blocks, commands, paths, URLs, placeholders, and tag values used by the taxonomy

`title:` is a human-facing field and may be Korean. Structural fields such as `type`, `tags`, and `sources` must follow the schema.

## Verification checklist

After localization changes:

1. Run `git diff --check`.
2. Count Markdown fences and ensure the count is even.
3. Search for leftover English template phrases that should not appear in generated Korean templates:
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
4. Search for required compatibility terms and confirm they remain:
   - `WIKI_PATHS`
   - `WIKI_DEFAULT`
   - `WIKI_PATH`
   - `type: entity | concept | comparison | query | summary`
   - `confidence: high | medium | low`
   - `source_url`
   - `sha256`
   - `ingest, update, query, lint, create, archive, delete`
5. Check frontmatter still has required skill metadata keys.
