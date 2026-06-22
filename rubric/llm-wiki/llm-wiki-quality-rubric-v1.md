# LLM Wiki 품질 루브릭 v1

## 1. 평가 목적

이 루브릭은 `llm-wiki` 지식 베이스가 유지보수 가능하고, 출처에 근거하며, 탐색 가능하고, 재사용 가능한 지식 시스템으로 신뢰해도 되는지를 평가한다.

이 루브릭은 ad-hoc wiki health check를 막기 위해 다음을 고정한다.

- 고정 100점 채점 모델
- hard gate 요구사항
- 가능한 경우 deterministic check
- 정성 판단이 필요한 경우 judge-only check
- 안정적인 JSON scorecard 형식

## 2. 평가 대상

단일 `llm-wiki` root directory. 최소한 다음을 포함한다.

- `SCHEMA.md`
- `index.md`
- `log.md`
- `entities/`, `concepts/`, `comparisons/`, `queries/` 아래 compiled wiki page
- `raw/` 아래 immutable source material
- 선택적으로 `_meta/` 아래 reproducibility artifact
- wiki 언어에 맞는 human-facing title, heading, compiled page filename/slug. 한국어 wiki에서는 설명형 concept/comparison/query의 `title`, H1, 파일명 slug가 한국어 우선이어야 하며, YAML key, enum 값, raw file path, tag, proper noun entity filename은 영어로 남겨도 된다.

## 3. 통과 기준

Baseline passing score(기본 통과 점수): **95 / 100**.

wiki는 다음 두 조건을 모두 만족할 때만 통과한다.

1. `total_score >= 95`
2. 모든 hard-gated dimension이 만점이어야 한다.
   - D1 Wiki Structure & Navigation: 15 / 15
   - D2 Page-Level Schema Compliance: 15 / 15
   - D3 Link Graph & Knowledge Connectivity: 15 / 15
   - D4 Source Integrity & Provenance: 20 / 20

D1-D4 중 하나라도 감점되면, numeric total이 90점 이상이어도 wiki는 **통과하면 안 된다**.

Hard-gate cap rule(하드 게이트 상한 규칙):

- D1-D4 중 하나라도 만점 미만이면 `pass = false`이고 `certification_score_cap = 89`다.
- 진단을 위해 `raw_total_score`는 표시할 수 있지만, certification 결과는 실패다.

## 4. Dimension 요약

| ID | 차원 | 점수 | Gate Type | 평가 초점 |
|---|---:|---:|---|---|
| D1 | Wiki Structure & Navigation | 15 | Hard gate | 필수 구조, index 일관성, log 존재 |
| D2 | Page-Level Schema Compliance | 15 | Hard gate | Frontmatter, type enum, 한국어 title/filename, tag, source reference |
| D3 | Link Graph & Knowledge Connectivity | 15 | Hard gate | Broken link, orphan page, 의미 있는 연결성 |
| D4 | Source Integrity & Provenance | 20 | Hard gate | Raw frontmatter, sha256 무결성, provenance 추적성 |
| D5 | Corpus Coverage & Domain Fit | 15 | Quality | Domain coverage, entity/concept 균형, cluster coverage |
| D6 | Synthesis Quality & Non-Generic Knowledge | 10 | Quality | 재사용 가능한 판단, tradeoff, source synthesis |
| D7 | Maintenance, Auditability & Evolution | 10 | Quality | Log, manifest, validation artifact, reviewability |
| **Total** |  | **100** |  |  |

## 5. 세부 채점 기준

### D1. Wiki Structure & Navigation — 15 points — Hard Gate

| 기준 | 점수 | 인정 기준 | Deterministic? |
|---|---:|---|---|
| 필수 root file 존재 | 3 | wiki root에 `SCHEMA.md`, `index.md`, `log.md`가 존재한다 | Yes |
| 필수 directory 존재 | 2 | `entities/`, `concepts/`, `comparisons/`, `queries/`, `raw/`가 존재한다 | Yes |
| Index count와 compiled page count 일치 | 3 | `index.md`에 선언된 page count가 compiled page directory 아래 실제 count와 같다 | Yes |
| 모든 compiled page가 index에 등재됨 | 3 | compiled directory 아래 모든 page stem에 대응하는 `[[wikilink]]`가 `index.md`에 있다 | Yes |
| Stale/extra index link 없음 | 2 | `index.md`의 모든 compiled-page wikilink가 실제 compiled page로 resolve된다 | Yes |
| Log 존재 및 내용 있음 | 2 | `log.md`에 최소 하나의 `## [YYYY-MM-DD]` entry가 있다 | Yes |

Local cap(차원 내 상한):

- `SCHEMA.md` 또는 `index.md`가 없으면 D1은 최대 6점이다.
- `log.md`가 없거나 dated entry가 없으면 D1은 최대 12점이다.
- D1 점수가 15점 미만이면 hard gate 실패다.

### D2. Page-Level Schema Compliance — 15 points — Hard Gate

| 기준 | 점수 | 인정 기준 | Deterministic? |
|---|---:|---|---|
| 유효한 YAML-like frontmatter block | 3 | 모든 compiled page가 `---`로 시작하고 닫는 `---`를 가지며 key-value frontmatter를 포함한다 | Yes |
| 필수 field 존재 | 3 | 모든 compiled page에 `title`, `created`, `updated`, `type`, `tags`, `sources`가 있다 | Yes |
| 유효한 `type` enum | 1 | `type`이 `entity`, `concept`, `comparison`, `query`, `summary` 중 하나다 | Yes |
| Human-readable title language | 1 | 한국어 wiki에서 non-proper-noun page title의 frontmatter와 H1은 한국어 우선이며, proper noun은 영어로 남겨도 된다 | Mostly yes |
| Korean-first compiled page filename/slug | 1 | 한국어 wiki에서 설명형 `concepts/`, `comparisons/`, `queries/` page filename/slug는 한국어를 포함한다. Google/Meta/Airbnb 같은 proper noun `entities/` filename은 영어 허용 | Mostly yes |
| Tag가 taxonomy 안에 있음 | 3 | compiled page의 모든 tag가 `SCHEMA.md` taxonomy에 등장한다 | Mostly yes |
| Source path가 구조적으로 유효함 | 2 | `sources`는 list-like field이며, 비어 있지 않은 source entry가 `raw/` 또는 문서화된 non-raw source path를 가리킨다 | Mostly yes |
| Date field가 유효한 ISO date | 1 | `created`와 `updated`가 `YYYY-MM-DD` 형식을 사용한다 | Yes |

Local cap(차원 내 상한):

- frontmatter가 없는 compiled page가 하나라도 있으면 D2는 최대 10점이다.
- 필수 field가 누락된 compiled page가 하나라도 있으면 D2는 최대 11점이다.
- taxonomy violation이 있으면 D2는 최대 12점이다.
- 한국어 wiki에서 non-proper-noun compiled page의 10% 초과가 English-only human-facing title이면 D2는 최대 12점이다.
- 한국어 wiki에서 설명형 compiled page filename/slug의 10% 초과가 English-only이면 D2는 최대 12점이다.
- D2 점수가 15점 미만이면 hard gate 실패다.

### D3. Link Graph & Knowledge Connectivity — 15 points — Hard Gate

| 기준 | 점수 | 인정 기준 | Deterministic? |
|---|---:|---|---|
| Broken compiled-page wikilink 없음 | 4 | compiled page 안의 wikilink가 compiled page stem 또는 허용된 root doc으로 resolve된다 | Yes |
| 최소 outbound link | 3 | 명시적으로 exempt된 page를 제외하고 모든 compiled page가 최소 2개 outbound wikilink를 가진다 | Yes |
| 설명 없는 orphan compiled page 없음 | 3 | 모든 compiled page가 inbound link를 갖거나 top-level query/index artifact로 명시적으로 exempt된다 | Yes + policy |
| Query/comparison page가 concept/entity로 다시 연결됨 | 2 | Query/comparison page가 관련 concept/entity/comparison page에 link한다 | Yes |
| Cross-link가 의미적으로 관련 있음 | 2 | link가 random padding이 아니라 의미 있는 관계를 나타낸다 | Judge |
| Raw file link noise가 graph에 포함되지 않음 | 1 | false positive를 피하기 위해 link graph가 `raw/` source artifact를 제외한다 | Yes |

Local cap(차원 내 상한):

- compiled-page broken link가 하나라도 있으면 D3은 최대 11점이다.
- 명시 exemption 없는 compiled page 중 orphan page가 10% 초과면 D3은 최대 10점이다.
- outbound link 요구사항이 광범위하게 위반되면 D3은 최대 10점이다.
- D3 점수가 15점 미만이면 hard gate 실패다.

### D4. Source Integrity & Provenance — 20 points — Hard Gate

| 기준 | 점수 | 인정 기준 | Deterministic? |
|---|---:|---|---|
| Raw frontmatter 존재 | 4 | 모든 raw `.md` file에 frontmatter block이 있다 | Yes |
| 필수 raw field 존재 | 4 | local/manual source로 문서화된 경우를 제외하고 모든 raw source에 `source_url`, `ingested`, `sha256`가 있다 | Yes |
| Raw sha256이 body와 일치 | 4 | 저장된 `sha256`이 project-defined normalization을 적용한 frontmatter 이후 body와 일치한다 | Yes |
| Compiled page가 source를 인용함 | 3 | 모든 compiled page의 `sources`가 비어 있지 않다 | Yes |
| Source reference resolve | 2 | compiled page frontmatter의 source path가 resolve되거나 명시적으로 문서화된 external reference다 | Mostly yes |
| Clickable raw provenance/source link | 2 | 3개 이상 source를 종합한 page와 `## 출처 보강` 같은 supplemental source section은 raw file로 클릭 가능한 link를 사용한다. plain/backticked `raw/...md` path는 점수를 주지 않는다 | Judge + partial regex |
| Fetch failure/exclusion 기록 | 1 | 실패하거나 제외된 source가 `log.md`, `_meta`, fetch report 중 하나에 기록되어 있다 | Yes + judge |

Hash normalization rule:

- 기본 deterministic checker는 raw frontmatter 닫는 delimiter 뒤의 text에서 leading blank newline을 제거한 값(`body.lstrip("\n")`)을 hash한다.
- wiki가 다른 normalization rule을 사용하면 그 rule을 `SCHEMA.md` 또는 `_meta/`에 문서화하고 checker도 그에 맞게 설정해야 한다.

Local cap(차원 내 상한):

- `sha256`이 없는 raw source가 하나라도 있으면 D4는 최대 14점이다.
- 설명 없는 raw source sha256 drift가 하나라도 있으면 D4는 최대 16점이다.
- compiled page의 `sources`가 비어 있거나 누락되면 D4는 최대 15점이다.
- raw provenance가 대부분 없으면 D4는 최대 12점이다.
- compiled-page body에 clickable Markdown/Obsidian link가 아닌 plain 또는 backticked `raw/...md` source path가 있으면 D4는 최대 18점이다.
- D4 점수가 20점 미만이면 hard gate 실패다.

### D5. Corpus Coverage & Domain Fit — 15 points — Quality Dimension

| 기준 | 점수 | 인정 기준 | Deterministic? |
|---|---:|---|---|
| Domain alignment | 2 | Source와 compiled page가 `SCHEMA.md`의 domain과 일치한다 | Judge |
| Raw cluster가 compiled page에 반영됨 | 3 | 주요 raw cluster에 대응하는 concept/entity/comparison/query coverage가 있다 | Partial |
| 반복 등장 entity/concept가 승격됨 | 3 | 고빈도이면서 decision-relevant한 entity/concept가 page로 compiled되었거나 명시적으로 deferred되었다 | Judge + partial |
| Page type mix가 정당화됨 | 2 | entities/concepts/comparisons/queries 비율이 wiki 목적과 맞고, unusual하면 설명되어 있다 | Judge |
| 핵심 use case에 evidence coverage가 있음 | 3 | 주요 question/use case를 compiled page와 source로 답할 수 있다 | Judge |
| 알려진 corpus gap이 문서화됨 | 2 | missing data, private-data requirement, coverage gap이 기록되어 있다 | Judge + search |

Local cap(차원 내 상한):

- raw corpus가 큰데 compiled coverage가 sparse하고 설명이 없으면 D5는 최대 10점이다.
- schema가 entity page를 요구하고 반복 entity가 존재하는데 `entities/`가 비어 있으면, concept-first policy가 문서화된 경우를 제외하고 D5는 최대 12점이다.
- 한 vendor/source family가 caveat 없이 지배적이면 D5는 최대 12점이다.

### D6. Synthesis Quality & Non-Generic Knowledge — 10 points — Quality Dimension

| 기준 | 점수 | 인정 기준 | Deterministic? |
|---|---:|---|---|
| Page가 definition, claim, implication, limit을 분리함 | 2 | page structure가 재사용과 review를 지원한다 | Judge |
| Multi-source synthesis | 3 | page가 source summary를 복사하는 대신 source를 비교하거나 종합한다 | Judge |
| Decision-relevant knowledge | 2 | page에 condition, tradeoff, metric, decision rule이 포함되어 있다 | Judge |
| Uncertainty와 contradiction 처리 | 2 | 관련 있는 경우 limitation, contested point, confidence가 명시되어 있다 | Judge |
| Long-form answer가 탐색 가능함 | 1 | 긴 query page가 분할되어 있거나 review하기 충분히 잘 구조화되어 있다 | Judge + line count |

Local cap(차원 내 상한):

- page가 대부분 copied source summary라면 D6은 최대 6점이다.
- unsupported recommendation이 흔하면 D6은 최대 7점이다.
- generic advice가 지배적이면 D6은 최대 7점이다.

### D7. Maintenance, Auditability & Evolution — 10 points — Quality Dimension

| 기준 | 점수 | 인정 기준 | Deterministic? |
|---|---:|---|---|
| Operation이 log에 기록됨 | 2 | ingest/update/query/lint 작업이 `log.md`에 나타난다 | Yes + judge |
| Log rotation이 건강함 | 1 | `log.md`가 rotation threshold 미만이거나 yearly rotation이 문서화되어 있다 | Yes |
| Reproducibility artifact 존재 | 2 | `_meta`가 manifest, fetch report, validation report 또는 동등한 artifact를 포함한다 | Yes |
| Low-confidence/contested/stale review surface 존재 | 2 | wiki가 약하거나 disputed된 page를 식별할 수 있다 | Partial |
| Large ingest에 validation report가 있음 | 2 | bulk source collection 또는 answer generation에 report/check가 있다 | Yes + judge |
| Recommendation이 path-specific임 | 1 | audit output이 path, evidence, fix를 명시한다 | Judge |

Local cap(차원 내 상한):

- 최근 bulk change에 log 또는 manifest가 없으면 D7은 최대 6점이다.
- validation 또는 reproducibility artifact가 전혀 없으면 D7은 최대 7점이다.

## 6. Global Caps and Certification Rules

먼저 checklist scoring을 적용하고, 그다음 local cap, global cap, certification rule 순서로 적용한다.

Global cap(전체 상한):

- 대상이 llm-wiki root가 아니면 total score는 최대 40점이다.
- `SCHEMA.md`와 `index.md`가 모두 없으면 total score는 최대 40점이다.
- 대부분의 compiled page에 frontmatter가 없으면 total score는 최대 60점이다.
- raw source provenance가 대부분 없으면 total score는 최대 65점이다.
- 한국어 wiki에서 non-proper-noun title이 English-only인 compiled page가 10% 초과면 total score는 최대 85점이다.
- 한국어 wiki에서 설명형 compiled page filename/slug가 English-only인 compiled page가 10% 초과면 total score는 최대 85점이다.
- source-trace 또는 supplemental raw path가 clickable link가 아니면 total score는 최대 90점이다.
- compiled-page broken link 또는 index mismatch가 광범위하면 total score는 최대 70점이다.
- 주요 claim이 source reference 없이 반복되면 total score는 최대 70점이다.
- 설명 없는 raw source drift가 있으면 total score는 최대 75점이다.
- 실제 corpus가 schema domain과 맞지 않으면 total score는 최대 75점이다.

Certification rule(인증 규칙):

- `pass = total_score >= 95 AND D1 = 15 AND D2 = 15 AND D3 = 15 AND D4 = 20`.
- hard-gated dimension 중 하나라도 실패하면 `raw_total_score >= 95`여도 `pass = false`다.
- cap이 적용되면 `raw_total_score`와 `certification_score`를 모두 보고한다.

## 7. 점수 해석

| 점수 | 해석 |
|---:|---|
| 95–100 and all hard gates pass | Production-quality llm-wiki. 일반 caveat 하에 반복적인 wiki-only 사용에 안전함 |
| 90–94 | 강하지만 passing baseline은 아님. quality dimension 또는 hard-gate gap 개선 필요 |
| 80–89 | 구조는 건강하지만 의미 있는 gap이 남아 있음. 인증되지 않음 |
| 70–79 | 부분적으로 사용 가능. 중요한 coverage, source, navigation issue가 남아 있음 |
| 60–69 | 약한 wiki. source dump 또는 incomplete compilation일 가능성이 큼 |
| 0–59 | llm-wiki로 신뢰하기 어려움. structure/provenance를 먼저 재구축해야 함 |

## 8. 채점 절차

1. target path와 read-only mode를 확인한다.
2. `SCHEMA.md`, `index.md`, 최근 `log.md`를 읽는다.
3. D1-D4와 D5-D7의 deterministic part에 대해 deterministic check를 실행한다.
4. checklist item을 독립적으로 채점한다.
5. local cap을 적용한다.
6. global cap을 적용한다.
7. hard-gate certification rule을 적용한다.
8. JSON scorecard와 짧은 human summary를 생성한다.
9. read-only audit 중에는 `log.md`를 업데이트하지 않는다.

## 9. Judge 지침

LLM 또는 human reviewer가 non-deterministic criteria를 평가할 때 다음 지침을 사용한다.

1. wiki file과 deterministic checker output의 evidence만 사용한다.
2. file count만으로 quality를 추론하지 않는다.
3. page가 탐색 가능하고 source-grounded한 경우가 아니라면 긴 page에 보상하지 않는다.
4. taxonomy intent가 `SCHEMA.md` 또는 compiled page에 나타나지 않으면 점수를 주지 않는다.
5. raw source는 provenance와 supplemental source reference가 plain-text raw path가 아니라 clickable Markdown/Obsidian link로 추적 가능할 때만 evidence로 취급한다.
6. total을 결정하기 전에 checklist item을 먼저 채점한다.
7. D1-D4 hard gate를 엄격하게 적용한다.
8. criterion을 검증할 수 없으면 `unverified`로 표시하고 적절하게 partial 또는 zero credit만 준다.
9. 모든 issue에 대해 구체적인 path와 evidence를 보고한다.

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
