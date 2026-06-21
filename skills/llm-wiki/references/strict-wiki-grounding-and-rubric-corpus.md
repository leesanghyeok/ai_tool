# Strict wiki grounding and rubric-calibrated corpus building

Use this reference when the user says answers must use only a specific LLM wiki, or asks to collect web material into `raw/` and ingest enough knowledge to satisfy a rubric.

## Strict wiki-only answers

When the user says “이 위키 내용만”, “여기에 있는 내용만”, “llmwiki 안에 있는 내용만”, or equivalent:

1. Treat the target wiki’s actual pages as the only answer evidence.
2. Do not use the `llm-wiki` skill text itself as domain evidence. The skill is procedure, not content.
3. Do not expand from `SCHEMA.md` taxonomy into concrete recommendations. Schema/domain/tags can only establish topical relevance.
4. If `index.md` has no relevant page, answer that the wiki lacks sufficient evidence.
5. Cite the actual wiki pages used; if only `SCHEMA.md`/`index.md` exists, say so explicitly.

Bad pattern:
- User asks a B2B SaaS or marketplace question with “wiki only”. Agent reads only schema tags like `funnel`, `retention`, `go-to-market`, then produces a general strategy answer.

Correct pattern:
- “현재 wiki에는 이 질문에 답할 충분한 근거가 없습니다. 확인된 근거는 `SCHEMA.md`의 도메인/태그뿐이며, 구체 진단·개선안 페이지는 없습니다.”

## Corpus building for rubric-gated answers

When the user asks to gather internet materials into `raw/` and ingest so that answers pass a rubric:

1. Read the rubric first and identify hard caps/gates.
2. Read all question files and cluster them by domain.
3. Use parallel subagents for source discovery only when useful; parent should verify and write/ingest.
4. Store web sources under `raw/articles/<cluster>/` with frontmatter: `source_url`, `fetched_via` if used, `ingested`, `sha256`, `cluster`, `questions`, `title`.
5. Ingest into class-level concept/comparison/query pages, not one narrow page per source.
6. Add a source manifest and fetch report under `_meta/` so collection is auditable.
7. Generate validation scripts/reports for mechanical gates, but do not confuse keyword checks with real rubric pass.
8. Run an independent strict review when possible.
9. If the rubric requires company-specific baselines, unit economics, experiments, or competitive data that public internet sources cannot provide, report the blocker honestly instead of inventing numbers.
10. Create a “required data for rubric pass” checklist when rubric goals cannot be honestly met from public sources alone.

## Termination-condition honesty

If a user sets an ambitious termination condition like “keep learning internet sources until all 20 answers score 90+,” do not claim completion just because a generated answer includes the right headings or keywords. For strict rubrics, completion requires semantic review against the rubric’s hard caps. If the hard caps require missing private/company data, the correct outcome is a blocker report plus the best completed artifacts, not fabricated pass/fail numbers.
