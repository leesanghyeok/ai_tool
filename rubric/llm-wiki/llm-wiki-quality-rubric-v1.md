# LLM Wiki Quality Rubric v1

## 1. Evaluation Purpose

This rubric evaluates whether an `llm-wiki` knowledge base is safe to rely on as a maintained, source-grounded, navigable, reusable knowledge system.

It is designed to prevent ad-hoc wiki health checks by defining:

- a fixed 100-point scoring model,
- hard gate requirements,
- deterministic checks where possible,
- judge-only checks where qualitative judgment is required,
- a stable JSON scorecard shape.

## 2. Evaluation Target

A single `llm-wiki` root directory containing, at minimum:

- `SCHEMA.md`
- `index.md`
- `log.md`
- compiled wiki pages under `entities/`, `concepts/`, `comparisons/`, `queries/`
- immutable source material under `raw/`
- optional reproducibility artifacts under `_meta/`
- human-facing titles and headings in the wiki language; in Korean-language wikis, descriptive concept/comparison/query titles should be Korean-first while stable slugs, YAML keys, enum values, file paths, tags, and proper nouns may remain English

## 3. Passing Standard

Baseline passing score: **95 / 100**.

A wiki only passes if both conditions are true:

1. `total_score >= 95`
2. all hard-gated dimensions score full points:
   - D1 Wiki Structure & Navigation: 15 / 15
   - D2 Page-Level Schema Compliance: 15 / 15
   - D3 Link Graph & Knowledge Connectivity: 15 / 15
   - D4 Source Integrity & Provenance: 20 / 20

If any of D1–D4 loses points, the wiki must **not** pass, even if the numeric total would otherwise be 90+.

Hard-gate cap rule:

- If any D1–D4 dimension is below full score, `pass = false` and `certification_score_cap = 89`.
- The reported `raw_total_score` may still be shown for diagnostics, but the certification result fails.

## 4. Dimension Summary

| ID | Dimension | Points | Gate Type | Evaluation Focus |
|---|---:|---:|---|---|
| D1 | Wiki Structure & Navigation | 15 | Hard gate | Required structure, index consistency, log presence |
| D2 | Page-Level Schema Compliance | 15 | Hard gate | Frontmatter, type enum, tags, source references |
| D3 | Link Graph & Knowledge Connectivity | 15 | Hard gate | Broken links, orphan pages, meaningful connectivity |
| D4 | Source Integrity & Provenance | 20 | Hard gate | Raw frontmatter, sha256 integrity, provenance traceability |
| D5 | Corpus Coverage & Domain Fit | 15 | Quality | Domain coverage, entity/concept balance, cluster coverage |
| D6 | Synthesis Quality & Non-Generic Knowledge | 10 | Quality | Reusable judgment, tradeoffs, source synthesis |
| D7 | Maintenance, Auditability & Evolution | 10 | Quality | Logs, manifests, validation artifacts, reviewability |
| **Total** |  | **100** |  |  |

## 5. Detailed Scoring Criteria

### D1. Wiki Structure & Navigation — 15 points — Hard Gate

| Criterion | Points | Recognition Standard | Deterministic? |
|---|---:|---|---|
| Required root files exist | 3 | `SCHEMA.md`, `index.md`, and `log.md` exist at wiki root | Yes |
| Required directories exist | 2 | `entities/`, `concepts/`, `comparisons/`, `queries/`, and `raw/` exist | Yes |
| Index count matches compiled page count | 3 | `index.md` declared page count equals actual count under compiled page dirs | Yes |
| Every compiled page appears in index | 3 | Every page stem under compiled dirs has a matching `[[wikilink]]` in `index.md` | Yes |
| No stale/extra index links | 2 | Every compiled-page wikilink in `index.md` resolves to an actual compiled page | Yes |
| Log is present and populated | 2 | `log.md` contains at least one `## [YYYY-MM-DD]` entry | Yes |

Local caps:

- If `SCHEMA.md` or `index.md` is missing, D1 is capped at 6.
- If `log.md` is missing or has no dated entries, D1 is capped at 12.
- Any D1 score below 15 fails the hard gate.

### D2. Page-Level Schema Compliance — 15 points — Hard Gate

| Criterion | Points | Recognition Standard | Deterministic? |
|---|---:|---|---|
| Valid YAML-like frontmatter block | 3 | Every compiled page starts with `---`, has a closing `---`, and contains key-value frontmatter | Yes |
| Required fields present | 3 | Every compiled page has `title`, `created`, `updated`, `type`, `tags`, `sources` | Yes |
| Valid `type` enum | 1 | `type` is one of `entity`, `concept`, `comparison`, `query`, `summary` | Yes |
| Human-readable title language | 2 | In a Korean wiki, non-proper-noun page titles in frontmatter and H1 are Korean-first; proper nouns may remain English | Mostly yes |
| Tags are in taxonomy | 3 | Every tag in compiled pages appears in `SCHEMA.md` taxonomy | Mostly yes |
| Source paths are structurally valid | 2 | `sources` is a list-like field; non-empty source entries point to `raw/` or a documented non-raw source path | Mostly yes |
| Date fields are valid ISO dates | 1 | `created` and `updated` use `YYYY-MM-DD` | Yes |

Local caps:

- If any compiled page lacks frontmatter, D2 is capped at 10.
- If required fields are missing from any compiled page, D2 is capped at 11.
- If taxonomy violations exist, D2 is capped at 12.
- If more than 10% of non-proper-noun compiled pages have English-only human-facing titles in a Korean wiki, D2 is capped at 12.
- Any D2 score below 15 fails the hard gate.

### D3. Link Graph & Knowledge Connectivity — 15 points — Hard Gate

| Criterion | Points | Recognition Standard | Deterministic? |
|---|---:|---|---|
| No broken compiled-page wikilinks | 4 | Wikilinks in compiled pages resolve to compiled page stems or accepted root docs | Yes |
| Minimum outbound links | 3 | Every compiled page has at least 2 outbound wikilinks, except explicitly exempted pages | Yes |
| No unexplained orphan compiled pages | 3 | Every compiled page has inbound links, or is explicitly exempted as a top-level query/index artifact | Yes + policy |
| Query/comparison pages connect back to concepts/entities | 2 | Query/comparison pages link to relevant concept/entity/comparison pages | Yes |
| Cross-links are semantically relevant | 2 | Links represent meaningful relationships, not random padding | Judge |
| No link noise from raw files included in graph | 1 | Link graph excludes `raw/` source artifacts to avoid false positives | Yes |

Local caps:

- If any compiled-page broken link exists, D3 is capped at 11.
- If more than 10% of compiled pages are orphan pages without explicit exemption, D3 is capped at 10.
- If outbound link requirement is broadly violated, D3 is capped at 10.
- Any D3 score below 15 fails the hard gate.

### D4. Source Integrity & Provenance — 20 points — Hard Gate

| Criterion | Points | Recognition Standard | Deterministic? |
|---|---:|---|---|
| Raw frontmatter exists | 4 | Every raw `.md` file has a frontmatter block | Yes |
| Required raw fields exist | 4 | Every raw source has `source_url`, `ingested`, and `sha256` unless documented as a local/manual source | Yes |
| Raw sha256 matches body | 4 | Stored `sha256` matches the body after frontmatter using the project-defined normalization | Yes |
| Compiled pages cite sources | 3 | Every compiled page has non-empty `sources` | Yes |
| Source references resolve | 2 | Source paths in compiled page frontmatter resolve or are explicitly documented external references | Mostly yes |
| Clickable raw provenance/source links | 2 | Pages synthesizing 3+ sources and any supplemental source sections such as `## 출처 보강` use clickable links to raw files; plain/backticked `raw/...md` paths do not receive credit | Judge + partial regex |
| Fetch failures/exclusions recorded | 1 | Failed or excluded sources are documented in `log.md`, `_meta`, or fetch reports | Yes + judge |

Hash normalization rule:

- The default deterministic checker hashes the text after the closing raw frontmatter delimiter, with leading blank newlines stripped (`body.lstrip("\n")`).
- If a wiki uses another normalization rule, it must document that rule in `SCHEMA.md` or `_meta/` and the checker must be configured accordingly.

Local caps:

- If any raw source lacks `sha256`, D4 is capped at 14.
- If any raw source has unexplained sha256 drift, D4 is capped at 16.
- If compiled pages have empty or missing `sources`, D4 is capped at 15.
- If raw provenance is mostly absent, D4 is capped at 12.
- If any compiled-page body contains plain or backticked `raw/...md` source paths that are not clickable Markdown/Obsidian links, D4 is capped at 18.
- Any D4 score below 20 fails the hard gate.

### D5. Corpus Coverage & Domain Fit — 15 points — Quality Dimension

| Criterion | Points | Recognition Standard | Deterministic? |
|---|---:|---|---|
| Domain alignment | 2 | Sources and compiled pages match the domain in `SCHEMA.md` | Judge |
| Raw clusters reflected in compiled pages | 3 | Major raw clusters have corresponding concept/entity/comparison/query coverage | Partial |
| Repeated entities/concepts are promoted | 3 | High-frequency, decision-relevant entities/concepts are compiled into pages or explicitly deferred | Judge + partial |
| Page type mix is justified | 2 | Entities/concepts/comparisons/queries ratio matches wiki purpose and is explained if unusual | Judge |
| Key use cases have evidence coverage | 3 | Main questions/use cases can be answered from compiled pages and sources | Judge |
| Known corpus gaps are documented | 2 | Missing data, private-data requirements, and coverage gaps are recorded | Judge + search |

Local caps:

- If raw corpus is large but compiled coverage is sparse and unexplained, D5 is capped at 10.
- If `entities/` is empty while the schema requires entity pages and repeated entities exist, D5 is capped at 12 unless a concept-first policy is documented.
- If one vendor/source family dominates without caveat, D5 is capped at 12.

### D6. Synthesis Quality & Non-Generic Knowledge — 10 points — Quality Dimension

| Criterion | Points | Recognition Standard | Deterministic? |
|---|---:|---|---|
| Pages separate definition, claims, implications, and limits | 2 | Page structure supports reuse and review | Judge |
| Multi-source synthesis | 3 | Pages compare or synthesize sources rather than copying summaries | Judge |
| Decision-relevant knowledge | 2 | Pages contain conditions, tradeoffs, metrics, or decision rules | Judge |
| Uncertainty and contradictions handled | 2 | Limitations, contested points, or confidence are explicit where relevant | Judge |
| Long-form answers remain navigable | 1 | Long query pages are split or structured well enough to review | Judge + line count |

Local caps:

- If pages are mostly copied source summaries, D6 is capped at 6.
- If unsupported recommendations are common, D6 is capped at 7.
- If generic advice dominates, D6 is capped at 7.

### D7. Maintenance, Auditability & Evolution — 10 points — Quality Dimension

| Criterion | Points | Recognition Standard | Deterministic? |
|---|---:|---|---|
| Operations are logged | 2 | Ingest/update/query/lint work appears in `log.md` | Yes + judge |
| Log rotation healthy | 1 | `log.md` is below rotation threshold or has documented yearly rotation | Yes |
| Reproducibility artifacts exist | 2 | `_meta` contains manifests, fetch reports, validation reports, or equivalent artifacts | Yes |
| Low-confidence/contested/stale review surfaces exist | 2 | The wiki can identify weak or disputed pages | Partial |
| Large ingest has validation reports | 2 | Bulk source collection or answer generation has reports/checks | Yes + judge |
| Recommendations are path-specific | 1 | Audit output names paths, evidence, and fixes | Judge |

Local caps:

- If recent bulk changes have no log or manifest, D7 is capped at 6.
- If no validation or reproducibility artifacts exist, D7 is capped at 7.

## 6. Global Caps and Certification Rules

Apply checklist scoring first, then local caps, then global caps, then certification rules.

Global caps:

- If the target is not an llm-wiki root, total score is capped at 40.
- If both `SCHEMA.md` and `index.md` are missing, total score is capped at 40.
- If most compiled pages lack frontmatter, total score is capped at 60.
- If raw source provenance is mostly absent, total score is capped at 65.
- If a Korean-language wiki uses English-only non-proper-noun titles for more than 10% of compiled pages, total score is capped at 85.
- If source-trace or supplemental raw paths are not clickable links, total score is capped at 90.
- If compiled-page broken links or index mismatches are widespread, total score is capped at 70.
- If major claims are repeatedly unsupported by source references, total score is capped at 70.
- If raw source drift exists without explanation, total score is capped at 75.
- If the actual corpus does not match the schema domain, total score is capped at 75.

Certification rule:

- `pass = total_score >= 95 AND D1 = 15 AND D2 = 15 AND D3 = 15 AND D4 = 20`.
- If any hard-gated dimension fails, `pass = false`, even when `raw_total_score >= 95`.
- Report both `raw_total_score` and `certification_score` when caps are applied.

## 7. Score Interpretation

| Score | Interpretation |
|---:|---|
| 95–100 and all hard gates pass | Production-quality llm-wiki; safe for repeated wiki-only use with normal caveats |
| 90–94 | Strong but not passing baseline; improve quality dimensions or hard-gate gaps |
| 80–89 | Healthy structure but meaningful gaps remain; not certified |
| 70–79 | Partially usable; important coverage, source, or navigation issues remain |
| 60–69 | Weak wiki; likely a source dump or incomplete compilation |
| 0–59 | Not reliable as llm-wiki; rebuild structure/provenance first |

## 8. Scoring Procedure

1. Confirm target path and read-only mode.
2. Read `SCHEMA.md`, `index.md`, and recent `log.md`.
3. Run deterministic checks for D1–D4 and deterministic parts of D5–D7.
4. Score checklist items independently.
5. Apply local caps.
6. Apply global caps.
7. Apply hard-gate certification rule.
8. Produce a JSON scorecard and a short human summary.
9. Do not update `log.md` during read-only audit.

## 9. Judge Instructions

Use these instructions when an LLM or human reviewer evaluates non-deterministic criteria:

1. Use only evidence from the wiki files and deterministic checker output.
2. Do not infer quality from file count alone.
3. Do not reward long pages unless they are navigable and source-grounded.
4. Do not give credit for taxonomy intent unless it appears in `SCHEMA.md` or compiled pages.
5. Treat raw sources as evidence only if provenance and supplemental source references are traceable through clickable Markdown/Obsidian links, not merely plain-text raw paths.
6. Score checklist items before deciding the total.
7. Apply D1–D4 hard gates strictly.
8. If a criterion cannot be verified, mark it as `unverified` and give only partial or zero credit as appropriate.
9. Report concrete paths and evidence for every issue.

## 10. JSON Scorecard Schema

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
  "grade": "excellent | strong_not_passing | adequate | weak | unacceptable",
  "hard_gates": [
    {
      "dimension_id": "D1",
      "required_score": 15,
      "actual_score": 0,
      "passed": false,
      "blocking_issues": ["string"]
    }
  ],
  "global_caps_applied": [
    {
      "rule_id": "string",
      "cap": 0,
      "reason": "string",
      "evidence": ["string"]
    }
  ],
  "dimension_scores": [
    {
      "dimension_id": "D1",
      "dimension": "Wiki Structure & Navigation",
      "score": 0,
      "max_score": 15,
      "gate_type": "hard | quality",
      "checklist": [
        {
          "criterion_id": "string",
          "score": 0,
          "max_score": 0,
          "deterministic": true,
          "evidence": ["string"],
          "paths": ["string"],
          "comment": "string"
        }
      ],
      "local_caps_applied": [],
      "summary": "string",
      "recommended_fixes": [
        {
          "priority": "high | medium | low",
          "path": "string",
          "action": "string"
        }
      ]
    }
  ],
  "counts": {
    "md_total": 0,
    "compiled_pages": 0,
    "entities": 0,
    "concepts": 0,
    "comparisons": 0,
    "queries": 0,
    "raw_sources": 0,
    "meta_files": 0,
    "log_entries": 0
  },
  "issues": [
    {
      "id": "string",
      "severity": "critical | high | medium | low | info",
      "dimension_id": "string",
      "rule": "string",
      "path": "string",
      "evidence": "string",
      "recommendation": "string"
    }
  ],
  "unverified": [
    {
      "area": "string",
      "reason": "string"
    }
  ],
  "next_actions": [
    {
      "priority": "high | medium | low",
      "action": "string",
      "paths": ["string"]
    }
  ]
}
```
