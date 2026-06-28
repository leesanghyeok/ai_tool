#!/usr/bin/env python3
"""Validate raw feedback Markdown files created by feedback-ai-logging-v2.

Checks are deterministic and intentionally limited to file shape:
- required YAML frontmatter fields
- controlled taxonomy values
- global raw feedback or skill-local feedback path convention
- body-only sha256
- required semantic body sections

Usage:
  python scripts/validate-feedback-log.py /path/to/raw/feedback/2026-06-01/*.md
  python scripts/validate-feedback-log.py /path/to/skills/foo/feedback/2026-06-01/*.md
  python scripts/validate-feedback-log.py --content-only /tmp/generated-feedback.md
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path

TASK_TYPES = {"research","coding","recommendation","summarization","planning","automation","review","translation","conversation","skill-usage","other"}
SEVERITIES = {"low","medium","high","critical"}
SOURCE_TYPES = {"ai-dissatisfaction", "skill-dissatisfaction"}
CATEGORIES = {"requirement-miss","evidence","freshness","verification","specificity","decision-criteria","format","tone","context-misread","overconfidence","hallucination","actionability","verbosity","insufficient-detail","skill-workflow"}
REQUIRED_FIELDS = {"type","source_type","source_platform","source_ref","session_id","ingested","created_at","task_type","agent_or_model","severity","categories","sha256"}
REQUIRED_SECTIONS = ["상황", "불만족", "기대", "실제 동작", "근거", "실패 범주", "심각도", "후보 Agent 규칙", "후보 체크리스트"]
GLOBAL_PATH_RE = re.compile(r"raw/feedback/\d{4}-\d{2}-\d{2}/\d{6}-.+-.+\.md$")
SKILL_LOCAL_PATH_RE = re.compile(r"/feedback/\d{4}-\d{2}-\d{2}/\d{6}-.+-.+\.md$")

def parse_frontmatter(text: str):
    if not text.startswith('---\n'):
        return None, text, ["frontmatter가 byte 0에서 시작하지 않음"]
    end = text.find('\n---\n', 4)
    if end == -1:
        return None, text, ["닫는 frontmatter delimiter가 없음"]
    fm_text = text[4:end]
    body = text[end+5:]
    data = {}
    for raw in fm_text.splitlines():
        if not raw.strip() or raw.lstrip().startswith('#'):
            continue
        if ':' not in raw:
            continue
        k, v = raw.split(':', 1)
        v = v.strip().strip('"')
        if v.startswith('[') and v.endswith(']'):
            v = [x.strip().strip('"\'') for x in v[1:-1].split(',') if x.strip()]
        data[k.strip()] = v
    return data, body, []

def validate(path: Path, *, content_only: bool = False):
    text = path.read_text(encoding='utf-8')
    fm, body, errors = parse_frontmatter(text)
    if fm is None:
        return {"path": str(path), "ok": False, "errors": errors}
    missing = sorted(REQUIRED_FIELDS - set(fm))
    errors += [f"required field 누락: {x}" for x in missing]
    if fm.get('type') != 'feedback-log':
        errors.append('type은 feedback-log여야 함')
    if fm.get('source_type') not in SOURCE_TYPES:
        errors.append('source_type taxonomy 위반')
    if fm.get('task_type') not in TASK_TYPES:
        errors.append('task_type taxonomy 위반')
    if fm.get('severity') not in SEVERITIES:
        errors.append('severity taxonomy 위반')
    cats = fm.get('categories', [])
    if isinstance(cats, str):
        cats = [cats]
    bad = [c for c in cats if c not in CATEGORIES]
    if bad:
        errors.append('categories taxonomy 위반: ' + ','.join(bad))
    actual_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()
    if fm.get('sha256') and fm.get('sha256') != actual_hash:
        errors.append(f"sha256 mismatch expected={fm.get('sha256')} actual={actual_hash}")
    if not content_only:
        norm = str(path.resolve()).replace('\\','/')
        source_type = fm.get('source_type')
        if source_type == 'skill-dissatisfaction':
            if not SKILL_LOCAL_PATH_RE.search(norm):
                errors.append('path convention 불일치: skill-local feedback/YYYY-MM-DD/{HHMMSS}-{session_id}-{short-slug}.md')
        elif source_type == 'ai-dissatisfaction':
            if not GLOBAL_PATH_RE.search(norm):
                errors.append('path convention 불일치: raw/feedback/YYYY-MM-DD/{HHMMSS}-{session_id}-{short-slug}.md')
        else:
            if not (GLOBAL_PATH_RE.search(norm) or SKILL_LOCAL_PATH_RE.search(norm)):
                errors.append('path convention 불일치')
    for section in REQUIRED_SECTIONS:
        if section not in body:
            errors.append(f"semantic section 누락: {section}")
    forbidden = ['triage_status','derived_pages','converted_to_rule','converted_to_rubric']
    for field in forbidden:
        if field in fm:
            errors.append(f"raw processing state field 금지: {field}")
    return {"path": str(path), "ok": not errors, "errors": errors}

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--content-only', action='store_true', help='path convention은 건너뛰고 file content shape/hash/taxonomy만 검증한다.')
    ap.add_argument('paths', nargs='+')
    ns = ap.parse_args(argv)
    files=[]
    for item in ns.paths:
        p=Path(item)
        if p.is_dir():
            files.extend(sorted(p.rglob('*.md')))
        else:
            files.extend(sorted(Path().glob(item)) if any(ch in item for ch in '*?[') else [p])
    results=[validate(p, content_only=ns.content_only) for p in files]
    print(json.dumps({"ok": all(r['ok'] for r in results), "files": results}, ensure_ascii=False, indent=2))
    return 0 if all(r['ok'] for r in results) else 1
if __name__ == '__main__':
    raise SystemExit(main())
