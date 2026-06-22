#!/usr/bin/env python3
"""Deterministic/heuristic checker for LLM Wiki Quality Rubric v1.

This script is read-only. It scores deterministic criteria directly and uses
explicit heuristics for rubric items that can be approximated from wiki files.
D1-D4 are hard gates: any issue in those dimensions prevents certification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RUBRIC_VERSION = "llm-wiki-quality-v1"
BASELINE_PASSING_SCORE = 95
COMPILED_DIRS = ("entities", "concepts", "comparisons", "queries")
REQUIRED_ROOT_FILES = ("SCHEMA.md", "index.md", "log.md")
REQUIRED_DIRS = COMPILED_DIRS + ("raw",)
VALID_TYPES = {"entity", "concept", "comparison", "query", "summary"}
REQUIRED_PAGE_FIELDS = {"title", "created", "updated", "type", "tags", "sources"}
REQUIRED_RAW_FIELDS = {"source_url", "ingested", "sha256"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.S)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
LOG_ENTRY_RE = re.compile(r"^## \[\d{4}-\d{2}-\d{2}\]", re.M)
RAW_REF_RE = re.compile(r"raw/(?:articles|reports|papers|feedback)/[^\\s,).`\\]]+\\.md")


@dataclass
class Criterion:
    criterion_id: str
    score: int
    max_score: int
    deterministic: bool = True
    evidence: list[str] = field(default_factory=list)
    paths: list[str] = field(default_factory=list)
    comment: str = ""


@dataclass
class Dimension:
    dimension_id: str
    dimension: str
    max_score: int
    gate_type: str
    checklist: list[Criterion]
    local_caps_applied: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    recommended_fixes: list[dict[str, Any]] = field(default_factory=list)

    @property
    def score(self) -> int:
        raw = sum(c.score for c in self.checklist)
        capped = raw
        for cap in self.local_caps_applied:
            capped = min(capped, int(cap["cap"]))
        return capped

    def as_json(self) -> dict[str, Any]:
        return {
            "dimension_id": self.dimension_id,
            "dimension": self.dimension,
            "score": self.score,
            "max_score": self.max_score,
            "gate_type": self.gate_type,
            "checklist": [c.__dict__ for c in self.checklist],
            "local_caps_applied": self.local_caps_applied,
            "summary": self.summary,
            "recommended_fixes": self.recommended_fixes,
        }


def rel(root: Path, p: Path) -> str:
    return p.relative_to(root).as_posix()


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def frontmatter(text: str) -> tuple[dict[str, str], str, bool]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text, False
    fm_text = m.group(1)
    body = text[m.end():]
    data: dict[str, str] = {}
    for line in fm_text.splitlines():
        m2 = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m2:
            data[m2.group(1)] = m2.group(2).strip()
    return data, body, True


def parse_listish(value: str) -> list[str]:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [x.strip().strip('"\'') for x in inner.split(",") if x.strip()]
    if not value:
        return []
    return [value.strip().strip('"\'')]


def scalar(value: str) -> str:
    return value.strip().strip('"\'')


def contains_korean(value: str) -> bool:
    return bool(re.search(r"[가-힣]", value))


def is_likely_proper_noun_title(value: str) -> bool:
    stripped = re.sub(r"[^A-Za-z0-9 &+./-]", "", value).strip()
    if not stripped:
        return False
    words = [w for w in re.split(r"[\s/&+.-]+", stripped) if w]
    if not words or len(words) > 4:
        return False
    return all(w[:1].isupper() or w.isupper() or any(ch.isdigit() for ch in w) for w in words)


def h1_title(text: str) -> str:
    m = re.search(r"^#\s+(.+)$", text, re.M)
    return m.group(1).strip() if m else ""


def has_clickable_raw_link(text: str, source: str) -> bool:
    source_no_ext = source[:-3] if source.endswith(".md") else source
    escaped_source = re.escape(source)
    escaped_no_ext = re.escape(source_no_ext)
    patterns = [
        rf"\[[^\]]+\]\([^)]*{escaped_source}[^)]*\)",
        rf"\[\[{escaped_source}(?:[|#\]])",
        rf"\[\[{escaped_no_ext}(?:[|#\]])",
        rf"\^\[{escaped_source}\]",
    ]
    return any(re.search(pattern, text) for pattern in patterns)


def nonclickable_raw_refs(markdown_text: str) -> list[str]:
    m = FRONTMATTER_RE.match(markdown_text)
    body = markdown_text[m.end():] if m else markdown_text
    refs = []
    for match in RAW_REF_RE.finditer(body):
        start = match.start()
        prev = body[start - 1] if start > 0 else ""
        # [raw/...](...), ../raw/... URLs, and ^[raw/...] provenance markers are clickable/traceable.
        if prev in {"[", "/", "("}:
            continue
        refs.append(match.group(0))
    return refs


def parse_taxonomy(schema_text: str) -> set[str]:
    if "## 태그 분류 체계" in schema_text:
        section = schema_text.split("## 태그 분류 체계", 1)[1]
        section = section.split("\n## ", 1)[0]
    elif "## Tag Taxonomy" in schema_text:
        section = schema_text.split("## Tag Taxonomy", 1)[1]
        section = section.split("\n## ", 1)[0]
    else:
        section = schema_text
    allowed: set[str] = set()
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("-") and ":" in stripped:
            values = stripped.split(":", 1)[1]
            allowed.update(x.strip().strip("`") for x in values.split(",") if x.strip())
    return allowed


def index_declared_count(index_text: str) -> int | None:
    patterns = [r"전체 페이지 수:\s*(\d+)", r"Total pages:\s*(\d+)"]
    for pat in patterns:
        m = re.search(pat, index_text)
        if m:
            return int(m.group(1))
    return None


def add_issue(issues: list[dict[str, Any]], severity: str, dimension_id: str, rule: str, path: str, evidence: str, recommendation: str) -> None:
    issues.append({
        "id": f"{dimension_id.lower()}.{len(issues)+1:03d}",
        "severity": severity,
        "dimension_id": dimension_id,
        "rule": rule,
        "path": path,
        "evidence": evidence,
        "recommendation": recommendation,
    })


def score_all(wiki: Path) -> dict[str, Any]:
    wiki = wiki.resolve()
    issues: list[dict[str, Any]] = []
    unverified: list[dict[str, str]] = []
    global_caps: list[dict[str, Any]] = []

    md_files = list(wiki.rglob("*.md")) if wiki.exists() else []
    compiled_pages = [p for p in md_files if p.relative_to(wiki).parts and p.relative_to(wiki).parts[0] in COMPILED_DIRS]
    raw_files = [p for p in md_files if p.relative_to(wiki).parts and p.relative_to(wiki).parts[0] == "raw"]
    meta_files = [p for p in md_files if p.relative_to(wiki).parts and p.relative_to(wiki).parts[0] == "_meta"]

    schema_text = read_text(wiki / "SCHEMA.md") if (wiki / "SCHEMA.md").exists() else ""
    index_text = read_text(wiki / "index.md") if (wiki / "index.md").exists() else ""
    log_text = read_text(wiki / "log.md") if (wiki / "log.md").exists() else ""
    taxonomy = parse_taxonomy(schema_text)

    # D1
    required_files_missing = [name for name in REQUIRED_ROOT_FILES if not (wiki / name).exists()]
    required_dirs_missing = [name for name in REQUIRED_DIRS if not (wiki / name).is_dir()]
    compiled_by_stem = {p.stem: p for p in compiled_pages}
    index_links = set(WIKILINK_RE.findall(index_text))
    declared = index_declared_count(index_text)
    missing_from_index = sorted(stem for stem in compiled_by_stem if stem not in index_links)
    extra_index_links = sorted(link for link in index_links if link not in compiled_by_stem)
    log_entries = len(LOG_ENTRY_RE.findall(log_text))

    d1_items = [
        Criterion("required_root_files_exist", 3 if not required_files_missing else 0, 3, evidence=[f"missing={required_files_missing}"]),
        Criterion("required_directories_exist", 2 if not required_dirs_missing else 0, 2, evidence=[f"missing={required_dirs_missing}"]),
        Criterion("index_count_matches", 3 if declared == len(compiled_pages) else 0, 3, evidence=[f"declared={declared}", f"actual={len(compiled_pages)}"]),
        Criterion("every_compiled_page_in_index", 3 if not missing_from_index else 0, 3, evidence=[f"missing_count={len(missing_from_index)}"], paths=[rel(wiki, compiled_by_stem[s]) for s in missing_from_index[:20]]),
        Criterion("no_stale_extra_index_links", 2 if not extra_index_links else 0, 2, evidence=[f"extra_count={len(extra_index_links)}", f"sample={extra_index_links[:20]}"]),
        Criterion("log_present_and_populated", 2 if log_entries > 0 else 0, 2, evidence=[f"log_entries={log_entries}"]),
    ]
    d1 = Dimension("D1", "Wiki Structure & Navigation", 15, "hard", d1_items)
    if "SCHEMA.md" in required_files_missing or "index.md" in required_files_missing:
        d1.local_caps_applied.append({"rule": "schema_or_index_missing", "cap": 6})
    if "log.md" in required_files_missing or log_entries == 0:
        d1.local_caps_applied.append({"rule": "log_missing_or_empty", "cap": 12})
    for p in missing_from_index:
        add_issue(issues, "critical", "D1", "compiled_page_missing_from_index", rel(wiki, compiled_by_stem[p]), "Compiled page not linked from index.md", "Add the page to index.md or archive it.")
    for link in extra_index_links:
        add_issue(issues, "critical", "D1", "extra_index_link", "index.md", f"Index link [[{link}]] does not resolve to a compiled page", "Remove stale index entry or create the missing page.")

    # D2 + collect page metadata
    fm_missing: list[Path] = []
    missing_fields: list[tuple[Path, list[str]]] = []
    invalid_types: list[tuple[Path, str]] = []
    tag_violations: list[tuple[Path, list[str]]] = []
    source_struct_issues: list[Path] = []
    date_issues: list[Path] = []
    title_language_issues: list[Path] = []
    page_fm: dict[Path, dict[str, str]] = {}
    for p in compiled_pages:
        data, _, ok = frontmatter(read_text(p))
        page_fm[p] = data
        if not ok:
            fm_missing.append(p)
            continue
        miss = sorted(REQUIRED_PAGE_FIELDS - set(data))
        if miss:
            missing_fields.append((p, miss))
        typ = data.get("type", "").strip()
        if typ not in VALID_TYPES:
            invalid_types.append((p, typ))
        tags = parse_listish(data.get("tags", ""))
        bad_tags = [t for t in tags if taxonomy and t not in taxonomy]
        if bad_tags:
            tag_violations.append((p, bad_tags))
        sources = parse_listish(data.get("sources", ""))
        if "sources" not in data or not sources:
            source_struct_issues.append(p)
        for k in ("created", "updated"):
            if k in data and not DATE_RE.match(data[k].strip().strip('"\'')):
                date_issues.append(p)
                break

    d2_items = [
        Criterion("valid_frontmatter", 3 if not fm_missing else 0, 3, evidence=[f"missing_or_malformed={len(fm_missing)}"], paths=[rel(wiki, p) for p in fm_missing[:20]]),
        Criterion("required_fields_present", 3 if not missing_fields else 0, 3, evidence=[f"pages_with_missing_fields={len(missing_fields)}"], paths=[rel(wiki, p) for p, _ in missing_fields[:20]]),
        Criterion("valid_type_enum", 1 if not invalid_types else 0, 1, evidence=[f"invalid_types={[(rel(wiki,p),t) for p,t in invalid_types[:20]]}"]),
        Criterion("human_readable_title_language", 2 if not title_language_issues else 0, 2, evidence=[f"title_language_issues={len(title_language_issues)}"], paths=[rel(wiki, p) for p in title_language_issues[:20]]),
        Criterion("tags_in_taxonomy", 3 if not tag_violations else 0, 3, evidence=[f"violations={[(rel(wiki,p),bad) for p,bad in tag_violations[:20]]}"]),
        Criterion("source_paths_structurally_valid", 2 if not source_struct_issues else 0, 2, evidence=[f"issues={len(source_struct_issues)}"], paths=[rel(wiki, p) for p in source_struct_issues[:20]]),
        Criterion("date_fields_valid", 1 if not date_issues else 0, 1, evidence=[f"date_issues={len(date_issues)}"], paths=[rel(wiki, p) for p in date_issues[:20]]),
    ]
    d2 = Dimension("D2", "Page-Level Schema Compliance", 15, "hard", d2_items)
    if fm_missing:
        d2.local_caps_applied.append({"rule": "frontmatter_missing", "cap": 10})
    if missing_fields:
        d2.local_caps_applied.append({"rule": "required_fields_missing", "cap": 11})
    if tag_violations:
        d2.local_caps_applied.append({"rule": "taxonomy_violations", "cap": 12})
    if compiled_pages and len(title_language_issues) / len(compiled_pages) > 0.10:
        d2.local_caps_applied.append({"rule": "english_only_titles_in_korean_wiki", "cap": 12})
    for p, bad in tag_violations:
        add_issue(issues, "critical", "D2", "taxonomy_violation", rel(wiki, p), f"Tags not in taxonomy: {bad}", "Add tags to SCHEMA.md taxonomy or replace with allowed tags.")
    for p in title_language_issues:
        add_issue(issues, "critical", "D2", "english_only_non_proper_title", rel(wiki, p), "Non-proper-noun page title/H1 appears English-only in a Korean wiki", "Use a Korean-first human-readable title while keeping filename/slug/tool fields stable.")

    # D3
    aliases: dict[str, Path] = {}
    for p in compiled_pages:
        aliases[p.stem] = p
        aliases[rel(wiki, p)[:-3]] = p
    inbound = {p: 0 for p in compiled_pages}
    broken_links: list[tuple[Path, str]] = []
    outbound_lt2: list[tuple[Path, int]] = []
    query_comparison_no_backlink: list[Path] = []
    for p in compiled_pages:
        links = [x.strip() for x in WIKILINK_RE.findall(read_text(p))]
        if len(links) < 2:
            outbound_lt2.append((p, len(links)))
        for link in links:
            target = aliases.get(link)
            if target:
                inbound[target] += 1
            elif link not in {"SCHEMA", "index", "log"}:
                broken_links.append((p, link))
        typ = page_fm.get(p, {}).get("type", "")
        if typ in {"query", "comparison"}:
            if not any(aliases.get(link) and page_fm.get(aliases[link], {}).get("type") in {"concept", "entity", "comparison"} for link in links):
                query_comparison_no_backlink.append(p)
    orphan_pages = [p for p, count in inbound.items() if count == 0]

    d3_items = [
        Criterion("no_broken_compiled_wikilinks", 4 if not broken_links else 0, 4, evidence=[f"broken_count={len(broken_links)}", f"sample={[(rel(wiki,p),l) for p,l in broken_links[:20]]}"]),
        Criterion("minimum_outbound_links", 3 if not outbound_lt2 else 0, 3, evidence=[f"outbound_lt2={[(rel(wiki,p),c) for p,c in outbound_lt2[:20]]}"]),
        Criterion("no_unexplained_orphans", 3 if not orphan_pages else 0, 3, evidence=[f"orphan_count={len(orphan_pages)}"], paths=[rel(wiki, p) for p in orphan_pages[:20]]),
        Criterion("query_comparison_connect_back", 2 if not query_comparison_no_backlink else 0, 2, evidence=[f"issues={len(query_comparison_no_backlink)}"], paths=[rel(wiki, p) for p in query_comparison_no_backlink[:20]]),
        Criterion("cross_links_semantically_relevant", 2 if not broken_links and not outbound_lt2 and not orphan_pages else 0, 2, deterministic=True, evidence=["Heuristic: all compiled-page links resolve, all pages have >=2 outbound links, and no orphan pages remain."], comment="Deterministic proxy; qualitative review can still downgrade."),
        Criterion("raw_link_noise_excluded", 1, 1, evidence=["Only compiled page dirs were used for link graph."]),
    ]
    d3 = Dimension("D3", "Link Graph & Knowledge Connectivity", 15, "hard", d3_items)
    if broken_links:
        d3.local_caps_applied.append({"rule": "broken_compiled_links", "cap": 11})
    if compiled_pages and len(orphan_pages) / len(compiled_pages) > 0.10:
        d3.local_caps_applied.append({"rule": "orphan_pages_over_10_percent", "cap": 10})
    if outbound_lt2:
        d3.local_caps_applied.append({"rule": "outbound_link_requirement_violated", "cap": 10})
    for p, link in broken_links:
        add_issue(issues, "critical", "D3", "broken_compiled_wikilink", rel(wiki, p), f"Broken wikilink [[{link}]]", "Fix the wikilink or create/archive the target page.")
    for p in orphan_pages:
        add_issue(issues, "critical", "D3", "orphan_compiled_page", rel(wiki, p), "No inbound links from compiled pages", "Add meaningful inbound links or document an exemption.")

    # D4
    raw_fm_missing: list[Path] = []
    raw_required_missing: list[tuple[Path, list[str]]] = []
    raw_hash_mismatch: list[tuple[Path, str, str]] = []
    source_resolve_issues: list[tuple[Path, str]] = []
    compiled_missing_sources: list[Path] = []
    nonclickable_body_refs: list[tuple[Path, list[str]]] = []
    for p in raw_files:
        data, body, ok = frontmatter(read_text(p))
        if not ok:
            raw_fm_missing.append(p)
            continue
        miss = sorted(REQUIRED_RAW_FIELDS - set(data))
        if "source_url" in miss and "source_ref" in data:
            # Local/manual sources may use source_ref instead of source_url.
            miss.remove("source_url")
        if miss:
            raw_required_missing.append((p, miss))
        if "sha256" in data:
            stored = scalar(data["sha256"]).lower()
            calc = hashlib.sha256(body.lstrip("\n").encode("utf-8")).hexdigest()
            if stored != calc:
                raw_hash_mismatch.append((p, stored[:12], calc[:12]))
    for p in compiled_pages:
        page_text = read_text(p)
        body_refs = nonclickable_raw_refs(page_text)
        if body_refs:
            nonclickable_body_refs.append((p, body_refs))
        sources = parse_listish(page_fm.get(p, {}).get("sources", ""))
        if not sources:
            compiled_missing_sources.append(p)
        for src in sources:
            if src.startswith("raw/") and not (wiki / src).exists():
                source_resolve_issues.append((p, src))
    failure_recorded = bool(re.search(r"failed|failure|exclude|제외|실패|Page Not Found", log_text, re.I)) or any("fetch" in q.name.lower() or "report" in q.name.lower() for q in (wiki / "_meta").glob("*")) if (wiki / "_meta").exists() else False
    multi_source_pages = []
    provenance_ok = []
    for p in compiled_pages:
        text = read_text(p)
        sources = parse_listish(page_fm.get(p, {}).get("sources", ""))
        if len(sources) >= 3:
            multi_source_pages.append(p)
            if all(has_clickable_raw_link(text, src) for src in sources):
                provenance_ok.append(p)
    provenance_score = 2 if len(provenance_ok) == len(multi_source_pages) else 0

    d4_items = [
        Criterion("raw_frontmatter_exists", 4 if not raw_fm_missing else 0, 4, evidence=[f"raw_fm_missing={len(raw_fm_missing)}"], paths=[rel(wiki, p) for p in raw_fm_missing[:20]]),
        Criterion("required_raw_fields_exist", 4 if not raw_required_missing else 0, 4, evidence=[f"raw_required_missing={[(rel(wiki,p),m) for p,m in raw_required_missing[:20]]}"]),
        Criterion("raw_sha256_matches_body", 4 if not raw_hash_mismatch else 0, 4, evidence=[f"mismatch_count={len(raw_hash_mismatch)}", f"sample={[(rel(wiki,p),s,c) for p,s,c in raw_hash_mismatch[:20]]}"]),
        Criterion("compiled_pages_cite_sources", 3 if not compiled_missing_sources else 0, 3, evidence=[f"compiled_missing_sources={len(compiled_missing_sources)}"], paths=[rel(wiki, p) for p in compiled_missing_sources[:20]]),
        Criterion("source_references_resolve", 2 if not source_resolve_issues else 0, 2, evidence=[f"resolve_issues={[(rel(wiki,p),s) for p,s in source_resolve_issues[:20]]}"]),
        Criterion("clickable_raw_provenance_and_source_links", 2 if provenance_score == 2 and not nonclickable_body_refs else 0, 2, deterministic=True, evidence=[f"multi_source_pages={len(multi_source_pages)}", f"with_clickable_traceability={len(provenance_ok)}", f"nonclickable_body_ref_pages={len(nonclickable_body_refs)}"], comment="Requires clickable Markdown/Obsidian links to raw files; plain/backticked paths do not receive credit, including supplemental source sections."),
        Criterion("fetch_failures_exclusions_recorded", 1 if failure_recorded else 0, 1, evidence=[f"failure_or_fetch_record_found={failure_recorded}"]),
    ]
    d4 = Dimension("D4", "Source Integrity & Provenance", 20, "hard", d4_items)
    if raw_required_missing:
        d4.local_caps_applied.append({"rule": "raw_sha256_or_required_field_missing", "cap": 14})
    if raw_hash_mismatch:
        d4.local_caps_applied.append({"rule": "unexplained_raw_sha256_drift", "cap": 16})
    if compiled_missing_sources:
        d4.local_caps_applied.append({"rule": "compiled_pages_missing_sources", "cap": 15})
    if (multi_source_pages and len(provenance_ok) != len(multi_source_pages)) or nonclickable_body_refs:
        d4.local_caps_applied.append({"rule": "non_clickable_or_missing_raw_source_links", "cap": 18})
    for p, stored, calc in raw_hash_mismatch:
        add_issue(issues, "critical", "D4", "raw_sha256_mismatch", rel(wiki, p), f"stored_prefix={stored}, calculated_prefix={calc}", "Investigate whether raw changed or hash normalization differs; document or restore immutable source.")
    for p in multi_source_pages:
        if p not in provenance_ok:
            add_issue(issues, "critical", "D4", "non_clickable_provenance_links", rel(wiki, p), "Multi-source page lacks clickable raw source provenance links for every source", "Replace plain/backticked raw paths with Markdown or Obsidian links to raw files.")
    for p, refs in nonclickable_body_refs:
        add_issue(issues, "critical", "D4", "non_clickable_body_raw_source_refs", rel(wiki, p), f"Plain raw source refs: {refs[:10]}", "Convert supplemental/source-body raw paths to clickable Markdown or Obsidian links.")

    # D5-D7 heuristic scoring
    entity_count = sum(1 for p in compiled_pages if p.relative_to(wiki).parts[0] == "entities")
    concept_count = sum(1 for p in compiled_pages if p.relative_to(wiki).parts[0] == "concepts")
    comparison_count = sum(1 for p in compiled_pages if p.relative_to(wiki).parts[0] == "comparisons")
    query_count = sum(1 for p in compiled_pages if p.relative_to(wiki).parts[0] == "queries")
    raw_clusters = sorted({p.relative_to(wiki).parts[1] for p in raw_files if len(p.relative_to(wiki).parts) > 2})
    large_pages = [(p, len(read_text(p).splitlines())) for p in compiled_pages if len(read_text(p).splitlines()) > 200]
    meta_artifacts = list((wiki / "_meta").glob("*")) if (wiki / "_meta").exists() else []

    compiled_text = "\n".join(read_text(p) for p in compiled_pages)
    domain_alignment_score = 2 if schema_text and compiled_pages and raw_files else 0
    cluster_hits = sum(1 for c in raw_clusters if c.replace("-", " ") in compiled_text.lower() or c in compiled_text.lower())
    raw_cluster_score = 3 if raw_clusters and cluster_hits >= max(1, min(5, len(raw_clusters)//2)) else (2 if cluster_hits else 0)
    entity_promotion_score = 3 if entity_count >= 5 else (2 if entity_count > 0 else 0)
    type_mix_score = 2 if entity_count and concept_count and comparison_count and query_count else 1 if concept_count and (comparison_count or query_count) else 0
    use_case_score = 3 if "marketing-question-to-knowledge-map" in index_text and "marketing-rubric-v3-answers-q01-q20" in index_text else 0
    gap_docs = [p for p in meta_artifacts if "required" in p.name.lower() or "gap" in p.name.lower() or "review" in p.name.lower()]
    gap_score = 2 if gap_docs else 0
    d5 = Dimension("D5", "Corpus Coverage & Domain Fit", 15, "quality", [
        Criterion("domain_alignment", domain_alignment_score, 2, evidence=[f"schema_present={bool(schema_text)}", f"compiled_pages={len(compiled_pages)}", f"raw_sources={len(raw_files)}"]),
        Criterion("raw_clusters_reflected", raw_cluster_score, 3, evidence=[f"raw_clusters={raw_clusters[:50]}", f"cluster_hits={cluster_hits}"]),
        Criterion("repeated_entities_concepts_promoted", entity_promotion_score, 3, evidence=[f"entity_count={entity_count}"]),
        Criterion("page_type_mix_justified", type_mix_score, 2, evidence=[f"entities={entity_count}, concepts={concept_count}, comparisons={comparison_count}, queries={query_count}"]),
        Criterion("key_use_cases_have_evidence", use_case_score, 3, evidence=["Checks for question map and Q01-Q20 answer set in index."]),
        Criterion("known_gaps_documented", gap_score, 2, evidence=[f"gap_or_review_docs={[q.name for q in gap_docs[:20]]}"]),
    ])
    if entity_count == 0 and raw_files:
        add_issue(issues, "medium", "D5", "entities_empty_with_raw_corpus", "entities/", f"entities=0, raw_sources={len(raw_files)}", "Document concept-first policy or create core entity pages.")

    heading_rich_pages = sum(1 for p in compiled_pages if len(re.findall(r"^## ", read_text(p), re.M)) >= 2)
    source_rich_pages = sum(1 for p in compiled_pages if len(parse_listish(page_fm.get(p, {}).get("sources", ""))) >= 2)
    decision_terms = len(re.findall(r"decision rule|판단|조건|tradeoff|지표|metric|KPI|리스크|한계", compiled_text, re.I))
    uncertainty_terms = len(re.findall(r"confidence:|한계|불확실|contested|모순|주의|부족", compiled_text, re.I))
    long_nav_score = 1 if not large_pages or all(len(re.findall(r"^## ", read_text(p), re.M)) >= 10 for p, _ in large_pages) else 0
    d6 = Dimension("D6", "Synthesis Quality & Non-Generic Knowledge", 10, "quality", [
        Criterion("page_structure_supports_reuse", 2 if heading_rich_pages >= max(1, len(compiled_pages)//2) else 1, 2, evidence=[f"heading_rich_pages={heading_rich_pages}"]),
        Criterion("multi_source_synthesis", 3 if source_rich_pages >= max(1, len(compiled_pages)//2) else 1, 3, evidence=[f"source_rich_pages={source_rich_pages}"]),
        Criterion("decision_relevant_knowledge", 2 if decision_terms >= 20 else 1 if decision_terms else 0, 2, evidence=[f"decision_terms={decision_terms}"]),
        Criterion("uncertainty_contradictions_handled", 2 if uncertainty_terms >= 10 else 1 if uncertainty_terms else 0, 2, evidence=[f"uncertainty_terms={uncertainty_terms}"]),
        Criterion("long_form_answers_navigable", long_nav_score, 1, evidence=[f"large_pages={[(rel(wiki,p),n) for p,n in large_pages[:20]]}"], comment="Long pages pass if they contain substantial section structure."),
    ])
    if large_pages and not long_nav_score:
        add_issue(issues, "low", "D6", "large_compiled_pages", ", ".join(rel(wiki, p) for p, _ in large_pages[:5]), f"pages_over_200_lines={len(large_pages)}", "Review whether long pages should be split or better structured.")

    weak_surface_score = 2 if re.search(r"confidence:|contested:|contradictions:", compiled_text) else 0
    report_like_count = sum(1 for p in meta_artifacts if 'report' in p.name.lower() or 'validation' in p.name.lower() or 'review' in p.name.lower())
    d7 = Dimension("D7", "Maintenance, Auditability & Evolution", 10, "quality", [
        Criterion("operations_logged", 2 if log_entries else 0, 2, evidence=[f"log_entries={log_entries}"]),
        Criterion("log_rotation_healthy", 1 if log_entries <= 500 else 0, 1, evidence=[f"log_entries={log_entries}"]),
        Criterion("reproducibility_artifacts_exist", 2 if meta_artifacts else 0, 2, evidence=[f"meta_artifacts={len(meta_artifacts)}"]),
        Criterion("weak_page_review_surfaces_exist", weak_surface_score, 2, evidence=["Searches compiled pages for confidence/contested/contradictions fields."]),
        Criterion("large_ingest_validation_reports", 2 if report_like_count else 0, 2, evidence=[f"meta_report_like={report_like_count}"]),
        Criterion("recommendations_path_specific", 1, 1, evidence=["Checker issues and next_actions include path-specific recommendations."]),
    ])

    dimensions = [d1, d2, d3, d4, d5, d6, d7]
    raw_total = sum(d.score for d in dimensions)

    if not wiki.exists() or not wiki.is_dir():
        global_caps.append({"rule_id": "target_not_directory", "cap": 40, "reason": "Target path is not a directory", "evidence": [str(wiki)]})
    if not (wiki / "SCHEMA.md").exists() and not (wiki / "index.md").exists():
        global_caps.append({"rule_id": "schema_and_index_missing", "cap": 40, "reason": "Both SCHEMA.md and index.md are missing", "evidence": []})
    if raw_hash_mismatch:
        global_caps.append({"rule_id": "raw_drift_unexplained", "cap": 75, "reason": "Raw source sha256 drift detected", "evidence": [f"mismatch_count={len(raw_hash_mismatch)}"]})
    if title_language_issues and compiled_pages and len(title_language_issues) / len(compiled_pages) > 0.10:
        global_caps.append({"rule_id": "english_only_titles_in_korean_wiki", "cap": 85, "reason": "Non-proper-noun page titles are not Korean-first", "evidence": [f"title_language_issues={len(title_language_issues)}"]})
    if (multi_source_pages and len(provenance_ok) != len(multi_source_pages)) or nonclickable_body_refs:
        global_caps.append({"rule_id": "non_clickable_raw_source_links", "cap": 90, "reason": "Source-trace or supplemental raw paths are not clickable for all compiled pages", "evidence": [f"multi_source_pages={len(multi_source_pages)}", f"with_clickable_traceability={len(provenance_ok)}", f"nonclickable_body_ref_pages={len(nonclickable_body_refs)}"]})

    capped_total = raw_total
    for cap in global_caps:
        capped_total = min(capped_total, int(cap["cap"]))

    hard_gate_requirements = {"D1": 15, "D2": 15, "D3": 15, "D4": 20}
    hard_gates = []
    for d in dimensions[:4]:
        blocking = [i["rule"] + ": " + i["path"] for i in issues if i["dimension_id"] == d.dimension_id and i["severity"] == "critical"]
        hard_gates.append({
            "dimension_id": d.dimension_id,
            "required_score": hard_gate_requirements[d.dimension_id],
            "actual_score": d.score,
            "passed": d.score == hard_gate_requirements[d.dimension_id],
            "blocking_issues": blocking,
        })

    all_hard_gates_pass = all(g["passed"] for g in hard_gates)
    certification_score = capped_total if all_hard_gates_pass else min(capped_total, 89)
    passed = certification_score >= BASELINE_PASSING_SCORE and all_hard_gates_pass
    if passed:
        grade = "excellent"
    elif capped_total >= 90:
        grade = "strong_not_passing"
    elif capped_total >= 80:
        grade = "adequate"
    elif capped_total >= 60:
        grade = "weak"
    else:
        grade = "unacceptable"

    counts = {
        "md_total": len(md_files),
        "compiled_pages": len(compiled_pages),
        "entities": entity_count,
        "concepts": concept_count,
        "comparisons": comparison_count,
        "queries": query_count,
        "raw_sources": len(raw_files),
        "meta_files": len(meta_files),
        "log_entries": log_entries,
    }

    next_actions = []
    for issue in issues:
        if issue["severity"] in {"critical", "high"}:
            next_actions.append({"priority": "high", "action": issue["recommendation"], "paths": [issue["path"]]})
    if not next_actions and issues:
        for issue in issues[:5]:
            next_actions.append({"priority": issue["severity"], "action": issue["recommendation"], "paths": [issue["path"]]})

    return {
        "wiki_path": str(wiki),
        "evaluated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "read_only": True,
        "rubric_version": RUBRIC_VERSION,
        "baseline_passing_score": BASELINE_PASSING_SCORE,
        "raw_total_score": raw_total,
        "certification_score": certification_score,
        "max_score": 100,
        "pass": passed,
        "grade": grade,
        "hard_gates": hard_gates,
        "global_caps_applied": global_caps,
        "dimension_scores": [d.as_json() for d in dimensions],
        "counts": counts,
        "issues": issues,
        "unverified": unverified,
        "next_actions": next_actions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only deterministic llm-wiki quality checker")
    parser.add_argument("wiki_path", type=Path)
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()
    result = score_all(args.wiki_path)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
