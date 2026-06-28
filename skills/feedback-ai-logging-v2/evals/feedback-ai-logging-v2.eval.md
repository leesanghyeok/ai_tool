# Eval Spec: feedback-ai-logging-v2

이 eval spec은 `feedback-ai-logging-v2`의 정규화된 incident JSON → raw feedback Markdown 변환 계약을 검증한다. `command` criteria는 자동 채점하고, `llm-judge` criteria는 현재 checklist로만 출력한다.

실행:

```bash
python3 scripts/run_evals.py --validate
python3 scripts/run_evals.py --rollout --json
```

## 기준 (Criteria)

1. **valid-feedback-log-content** (`command`) — generated feedback Markdown이 required frontmatter, semantic section, taxonomy, body-only `sha256` 검증을 통과한다.
2. **raw-state-separated** (`command`) — raw log에 처리 상태나 승격 상태 field가 섞이지 않는다.
3. **body-has-core-evidence** (`command`) — 본문에 기대 동작, 실제 동작, 근거, 후보 Agent 규칙 section이 있다.
4. **pipeline-renders-frontmatter** (`command`) — pipeline output이 필수 feedback-log frontmatter field를 포함한다.
5. **semantic-incident-quality** (`llm-judge`) — 사건이 expected/actual/mismatch/evidence/candidate rule을 갖춘 독립 사건인지 사람이 packet evidence로 확인한다.

## 골든 케이스 (Golden cases)

- `case-1`: global raw feedback에서 검증 없이 완료 보고한 사건.
- `case-2`: skill-local feedback에서 스킬 사용 불만족을 해당 스킬 내부 `feedback/`으로 라우팅하는 사건.
- `case-3`: cross-session 수확 중 의미상 중복 후보를 제외해야 하는 사건.

## JSON 명세 (Spec)

```json
{
  "skill": "feedback-ai-logging-v2",
  "run": "python3 scripts/run_pipeline.py --input {input} --output {output}",
  "criteria": [
    {
      "id": "valid-feedback-log-content",
      "text": "Generated feedback Markdown passes required frontmatter, taxonomy, sections, and body-only sha256 checks.",
      "type": "command",
      "cmd": "python3 scripts/validate-feedback-log.py --content-only {output}"
    },
    {
      "id": "raw-state-separated",
      "text": "Raw feedback log does not contain processing or promotion state fields.",
      "type": "command",
      "cmd": "python3 -c 'import sys; t=open(sys.argv[1], encoding=\"utf-8\").read(); bad=[x for x in [\"triage_status\",\"derived_pages\",\"converted_to_rule\",\"converted_to_rubric\"] if x in t]; raise SystemExit(1 if bad else 0)' {output}"
    },
    {
      "id": "body-has-core-evidence",
      "text": "Body includes expected behavior, actual behavior, evidence, and candidate rule sections.",
      "type": "command",
      "cmd": "python3 -c 'import sys; t=open(sys.argv[1], encoding=\"utf-8\").read(); req=[\"## 기대한 동작\",\"## 실제 동작\",\"## 근거\",\"## 후보 Agent 규칙\"]; raise SystemExit(0 if all(x in t for x in req) else 1)' {output}"
    },
    {
      "id": "pipeline-renders-frontmatter",
      "text": "Generated output includes required feedback-log frontmatter fields.",
      "type": "command",
      "cmd": "python3 -c 'import sys; t=open(sys.argv[1], encoding=\"utf-8\").read(); req=[\"type: \\\"feedback-log\\\"\",\"source_type:\",\"source_platform:\",\"source_ref:\",\"session_id:\",\"sha256:\"]; raise SystemExit(0 if all(x in t for x in req) else 1)' {output}"
    },
    {
      "id": "semantic-incident-quality",
      "text": "A reviewer can identify one incident with expected behavior, actual behavior, mismatch, evidence, and candidate rule.",
      "type": "llm-judge"
    }
  ],
  "golden": [
    {
      "id": "case-1",
      "input": "golden/case-1/input.json",
      "expected": "golden/case-1/expected.md",
      "split": "val"
    },
    {
      "id": "case-2",
      "input": "golden/case-2/input.json",
      "expected": "golden/case-2/expected.md",
      "split": "val"
    },
    {
      "id": "case-3",
      "input": "golden/case-3/input.json",
      "expected": "golden/case-3/expected.md",
      "split": "val"
    }
  ]
}
```
