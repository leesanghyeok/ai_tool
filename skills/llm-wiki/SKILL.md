---
name: llm-wiki
description: "Karpathy LLM Wiki: 상호 링크된 Markdown 지식 베이스 생성/조회."
version: 2.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [wiki, knowledge-base, research, notes, markdown, rag-alternative]
    category: research
    related_skills: [obsidian, arxiv]
---

# Karpathy의 LLM Wiki

상호 링크된 Markdown 파일로 지속적으로 축적되고 복리처럼 성장하는 지식 베이스를 만든다.
[Andrej Karpathy의 LLM Wiki 패턴](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)을 기반으로 한다.

전통적인 RAG가 매 질의마다 지식을 다시 탐색하는 방식이라면, 이 wiki는 지식을 한 번 컴파일하고 계속 최신 상태로 유지한다. 교차 참조가 이미 마련되어 있고, 모순은 표시되어 있으며, 종합 분석은 지금까지 수집한 내용을 반영한다.

**역할 분담:** 사람은 소스를 큐레이션하고 분석 방향을 정한다. 에이전트는 요약, 교차 참조, 파일 정리, 일관성 유지를 맡는다.

## 이 스킬이 활성화되는 경우

사용자가 다음을 요청하면 이 스킬을 사용한다:
- wiki 또는 지식 베이스를 만들거나 시작해 달라고 요청할 때
- 소스를 wiki에 ingest/add/process 해 달라고 요청할 때
- 선택된 경로에 기존 wiki가 있고 그 wiki에 대한 질문을 할 때
- wiki lint, audit, health-check를 요청할 때
- 연구 맥락에서 wiki, knowledge base, notes를 언급할 때

## Wiki 위치

**위치는 단일 wiki 또는 이름이 붙은 다중 wiki registry로 설정할 수 있다.** `${HERMES_HOME:-~/.hermes}/.env` 또는 에이전트 런타임에 다음 환경변수를 설정한다:

```bash
# 다중 wiki 모드: 세미콜론으로 구분한 key=path 쌍.
WIKI_PATHS="ai=$HOME/wiki/ai;work=$HOME/wiki/work;feedback=$HOME/wiki/feedback"

# 사용자가 wiki를 명시하지 않았을 때 사용할 기본 key. 선택 사항.
WIKI_DEFAULT="ai"

# 기존 단일 wiki 모드도 계속 지원한다.
WIKI_PATH="$HOME/wiki"
```

각 작업마다 다음 우선순위로 활성 wiki를 결정한다:

1. 사용자가 명시한 경로(절대 경로, `~/...`, 또는 명확한 상대 경로).
2. 사용자가 말한 wiki key/topic을 `WIKI_PATHS` key와 매칭한 결과(예: "ai wiki", "work wiki").
3. `WIKI_DEFAULT`가 설정되어 있고 `WIKI_PATHS`에 존재하는 경우 해당 key.
4. 기존 방식의 `WIKI_PATH`.
5. `~/wiki`.

경로를 결정한 뒤에는 해당 작업이 끝날 때까지 `WIKI`를 선택된 디렉터리로 간주한다.
여러 wiki 경로가 설정되어 있고 쓰기 작업의 대상이 모호하면, 생성, ingest, 업데이트, 삭제, archive, log 기록을 하기 전에 어떤 wiki를 사용할지 사용자에게 물어본다. 읽기 전용 질의는 기본 wiki를 사용할 수 있지만, 어떤 wiki key/path를 사용했는지 보고한다.

wiki는 Markdown 파일이 들어 있는 디렉터리일 뿐이다. Obsidian, VS Code 또는 아무 편집기에서 열 수 있다. 데이터베이스나 특수 도구는 필요 없다.

## 아키텍처: 세 계층

```
wiki/
├── SCHEMA.md           # 규칙, 구조, 도메인 설정
├── index.md            # 한 줄 요약이 포함된 섹션별 콘텐츠 카탈로그
├── log.md              # 시간순 작업 로그(append-only, 연 단위 회전)
├── raw/                # Layer 1: 변경하지 않는 원본 소스
│   ├── articles/       # 웹 글, 클리핑
│   ├── papers/         # PDF, arXiv 논문
│   ├── transcripts/    # 회의록, 인터뷰
│   └── assets/         # 소스에서 참조하는 이미지, 다이어그램
├── entities/           # Layer 2: 엔티티 페이지(사람, 조직, 제품, 모델)
├── concepts/           # Layer 2: 개념/주제 페이지
├── comparisons/        # Layer 2: 비교 분석
└── queries/            # Layer 2: 보존할 가치가 있는 질의 결과
```

**Layer 1 — 원본 소스:** 변경하지 않는다. 에이전트는 읽기만 하고 수정하지 않는다.
**Layer 2 — Wiki 본문:** 에이전트가 관리하는 Markdown 파일이다. 생성, 업데이트, 교차 참조를 수행한다.
**Layer 3 — Schema:** `SCHEMA.md`가 구조, 규칙, 태그 taxonomy를 정의한다.

## 기존 Wiki 재개하기 (중요 — 매 세션마다 수행)

기존 wiki가 있으면, 어떤 작업을 하기 전에 **반드시 먼저 방향을 잡는다**:

① **`SCHEMA.md` 읽기** — 도메인, 규칙, 태그 taxonomy를 이해한다.
② **`index.md` 읽기** — 어떤 페이지가 있고 각 페이지의 요약이 무엇인지 파악한다.
③ **최근 `log.md` 확인** — 최근 작업을 이해하기 위해 마지막 20~30개 항목을 읽는다.

```bash
# 먼저 사용자가 요청한 key/topic/path, WIKI_PATHS + WIKI_DEFAULT,
# legacy WIKI_PATH 또는 ~/wiki를 기준으로 활성 wiki를 결정한다.
WIKI="<selected wiki path>"
WIKI_KEY="<selected key, or explicit-path/legacy/default>"

# 세션 시작 시 orientation 읽기
read_file "$WIKI/SCHEMA.md"
read_file "$WIKI/index.md"
read_file "$WIKI/log.md" offset=<last 30 lines>
```

orientation을 마친 뒤에만 ingest, query, lint를 수행한다. 이렇게 해야 다음 문제를 막을 수 있다:
- 이미 존재하는 엔티티에 중복 페이지 생성
- 기존 콘텐츠와의 교차 참조 누락
- schema 규칙과 충돌
- 이미 log에 기록된 작업 반복

큰 wiki(100페이지 이상)에서는 새 페이지를 만들기 전에 관련 주제로 `search_files`를 빠르게 실행한다.

## 새 Wiki 초기화

사용자가 wiki 생성 또는 시작을 요청하면:

1. 위의 경로 결정 우선순위에 따라 wiki 경로를 정한다. 다중 wiki 모드이고 대상이 모호하면 쓰기 전에 key/path를 물어본다.
2. 새로 이름 붙일 wiki라면 `WIKI_PATHS`에 사용할 안정적인 lowercase key를 선택하거나 확인한다(예: `ai`, `work`, `feedback`, `project-x`).
3. 위 디렉터리 구조를 생성한다.
4. wiki가 다룰 도메인을 사용자에게 묻는다. 구체적으로 확인한다.
5. 도메인에 맞춘 `SCHEMA.md`를 작성한다(아래 템플릿 참고).
6. 섹션 헤더가 있는 초기 `index.md`를 작성한다.
7. wiki key/path가 포함된 생성 항목을 초기 `log.md`에 작성한다.
8. wiki 준비가 끝났음을 알리고 처음 ingest할 소스를 제안한다.

### 생성 문서 언어

- 한국어 대화이거나 사용자가 한국어 생성을 요청한 경우, 새 wiki의 `SCHEMA.md`, `index.md`, `log.md`에 들어가는 사람이 읽는 제목, 설명, 요약, 로그 본문은 한국어로 작성한다.
- 이후 생성되는 `entities/`, `concepts/`, `comparisons/`, `queries/` 페이지의 본문, 섹션 제목, index 항목, log 설명도 같은 언어를 따른다.
- 도구 호환성을 위해 파일명, 디렉터리명, 환경변수, 명령어, YAML/frontmatter 키, enum 값, action 값은 원문을 유지한다. 예: `WIKI_PATHS`, `SCHEMA.md`, `type: entity | concept | comparison | query | summary`, `confidence: high | medium | low`, `ingest`, `update`, `query`, `lint`.
- `title:` 값은 사람이 읽는 제목이므로 wiki 언어에 맞춰 한국어로 쓸 수 있다. `type`, `tags`, `sources` 등 구조 필드는 schema 규칙과 taxonomy를 따른다.

### 기존 wiki 메타 문서 언어 정리

사용자가 기존 wiki의 영어 생성 템플릿/메타 문구를 대상 언어로 바꿔 달라고 하면:
1. 먼저 평소처럼 orientation한다: `SCHEMA.md`, `index.md`, 최근 `log.md`를 읽는다.
2. `search_files`로 `# Wiki Schema`, `# Wiki Index`, `# Wiki Log`, `Content catalog`, `Chronological record`, `Page Title`, `Tag Taxonomy`, `Page Thresholds`, `Update Policy`, `Wiki initialized` 같은 남은 템플릿 영어 문구를 찾는다.
3. `SCHEMA.md`, `index.md`, `log.md`의 사람이 읽는 제목/설명/요약/로그 본문만 대상 언어로 바꾼다.
4. 호환성 표면은 유지한다: 파일명/디렉터리명, YAML/frontmatter 키, enum/action 값, taxonomy 태그 값, 환경변수, 명령어, source path.
5. `raw/` 원본 소스는 수정하지 않는다.
6. `log.md`에 `update | 메타 문서 <언어>화` 항목을 append하고, 어떤 호환성 표면을 유지했는지 기록한다.
7. 검증한다: Markdown code fence 짝수 여부, 영어 템플릿 핵심문구 0건, 필수 호환성 문자열(`type: entity | concept | comparison | query | summary`, `confidence: high | medium | low`, `source_url`, `sha256`, action 목록) 존재 여부.

### 명시적 경로 + 이름으로 새 Wiki를 만들 때
### 명시적 경로 + 이름으로 새 Wiki를 만들 때

- 사용자가 `~/Documents/marketing-wiki`처럼 경로와 이름을 함께 주고 "llmwiki를 만들어줘"라고 하면, 경로와 이름에서 도메인이 명확한 경우(예: `marketing-wiki`)에는 낮은 위험의 기본 도메인을 추론해 즉시 초기화할 수 있다. 단, `SCHEMA.md`의 도메인 섹션에 추론 범위를 명시한다.
- 생성 후 사용자가 "설정해줘/등록해줘"라고 명시 승인하면 `${HERMES_HOME:-~/.hermes}/.env`에 `WIKI_PATHS`와 필요 시 `WIKI_DEFAULT`를 등록한다.
- `.env`를 수정할 때는 기존 `WIKI_PATHS` 항목을 덮어쓰지 말고 세미콜론 구분 key=path 목록을 파싱해 새 key만 추가하거나 같은 key만 교체한다.
- 검증은 최소한 wiki root, `SCHEMA.md`, `index.md`, `log.md` 존재 여부와 `.env`의 `WIKI_PATHS`/`WIKI_DEFAULT` 최종 값을 확인한다.
- 적용 범위를 보고할 때는 현재 세션에는 환경변수 변경이 즉시 반영되지 않을 수 있으므로 새 세션 또는 `/reset`이 필요할 수 있음을 짧게 알린다.

### SCHEMA.md 템플릿

사용자 도메인에 맞게 조정한다. schema는 에이전트 행동을 제약하고 일관성을 보장한다:

```markdown
# 위키 스키마

## 도메인
[이 wiki가 다루는 범위 — 예: "AI/ML 연구", "개인 건강", "스타트업 인텔리전스"]

## 작성 규칙
- 파일명은 소문자, 하이픈, 공백 없음 형식을 사용한다(예: `transformer-architecture.md`).
- 모든 wiki 페이지는 YAML frontmatter로 시작한다(아래 참고).
- 페이지 사이 연결에는 `[[wikilinks]]`를 사용한다(페이지마다 최소 2개 외부 연결).
- 페이지를 업데이트할 때는 항상 `updated` 날짜를 갱신한다.
- 새 페이지는 반드시 `index.md`의 올바른 섹션에 추가한다.
- 모든 작업은 반드시 `log.md`에 추가한다.
- **출처 표시(Provenance markers):** 3개 이상의 소스를 종합한 페이지에서는 특정 소스에서 온 주장 문단 끝에 `^[raw/articles/source-file.md]`를 붙인다. 이렇게 하면 독자가 원본 전체를 다시 읽지 않고도 주장의 출처를 추적할 수 있다. 단일 소스 페이지에서는 `sources:` frontmatter만으로 충분하므로 선택 사항이다.

## 프론트매터
  ```yaml
  ---
  title: 페이지 제목
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  type: entity | concept | comparison | query | summary
  tags: [아래 taxonomy에서 선택]
  sources: [raw/articles/source-name.md]
  # 선택 품질 신호:
  confidence: high | medium | low        # 주장이 얼마나 잘 뒷받침되는지
  contested: true                        # 해결되지 않은 모순이 있을 때 설정
  contradictions: [other-page-slug]      # 이 페이지와 충돌하는 페이지
  ---
  ```

`confidence`와 `contested`는 선택 사항이지만, 의견이 많거나 빠르게 변하는 주제에는 권장한다. lint는 `contested: true`와 `confidence: low` 페이지를 검토 대상으로 표시하여 약한 주장이 조용히 확정 사실처럼 굳어지는 것을 막는다.

### raw/ Frontmatter

Raw source에도 작은 frontmatter block을 추가하여 재 ingest 시 drift를 감지한다:

```yaml
---
source_url: https://example.com/article   # 원본 URL, 있는 경우
ingested: YYYY-MM-DD
sha256: <frontmatter 아래 본문에 대한 16진수 digest>
---
```

`sha256:`을 사용하면 같은 URL을 나중에 다시 ingest할 때 콘텐츠가 같으면 건너뛰고, 달라졌으면 drift로 표시할 수 있다. 해시는 frontmatter가 아니라 닫는 `---` 뒤의 본문만 대상으로 계산한다.

## 태그 분류 체계
[도메인에 맞는 상위 태그 10~20개를 정의한다. 새 태그는 사용하기 전에 여기에 먼저 추가한다.]

AI/ML 예시:
- 모델: model, architecture, benchmark, training
- 사람/조직: person, company, lab, open-source
- 기법: optimization, fine-tuning, inference, alignment, data
- 메타: comparison, timeline, controversy, prediction

규칙: 페이지에서 사용하는 모든 태그는 이 taxonomy에 있어야 한다. 새 태그가 필요하면 먼저 여기에 추가한 뒤 사용한다. 이렇게 해야 태그가 무분별하게 늘어나는 것을 막을 수 있다.

## 페이지 생성 기준
- **페이지 생성:** 엔티티/개념이 2개 이상의 소스에 등장하거나, 하나의 소스에서 중심 주제일 때
- **기존 페이지에 추가:** 소스가 이미 다뤄진 내용을 언급할 때
- **페이지 생성 금지:** 지나가는 언급, 사소한 세부사항, 도메인 밖의 내용
- **페이지 분할:** 약 200줄을 넘으면 하위 주제로 나누고 교차 링크를 추가
- **페이지 보관:** 내용이 완전히 대체되면 `_archive/`로 이동하고 index에서 제거

## 엔티티 페이지
주요 엔티티마다 한 페이지를 둔다. 포함 항목:
- 개요 / 무엇인지
- 핵심 사실과 날짜
- 다른 엔티티와의 관계(`[[wikilinks]]`)
- 소스 참조

## 개념 페이지
개념 또는 주제마다 한 페이지를 둔다. 포함 항목:
- 정의 / 설명
- 현재 지식 상태
- 열린 질문 또는 논쟁
- 관련 개념(`[[wikilinks]]`)

## 비교 페이지
나란히 비교하는 분석이다. 포함 항목:
- 무엇을 왜 비교하는지
- 비교 차원(표 형식 권장)
- 결론 또는 종합
- 소스

## 업데이트 정책
새 정보가 기존 내용과 충돌하면:
1. 날짜를 확인한다. 일반적으로 더 최신 소스가 오래된 소스를 대체한다.
2. 실제로 모순이면 날짜와 소스를 포함해 양쪽 입장을 모두 적는다.
3. frontmatter에 모순을 표시한다: `contradictions: [page-name]`
4. lint 보고서에서 사용자 검토 대상으로 표시한다.
```

### index.md 템플릿

index는 type별 섹션으로 구성한다. 각 항목은 wikilink + 한 줄 요약이다.

```markdown
# 위키 인덱스

> 콘텐츠 카탈로그. 모든 wiki 페이지를 type별로 나누고 한 줄 요약과 함께 나열한다.
> 질의와 관련된 페이지를 찾을 때 먼저 읽는다.
> 마지막 업데이트: YYYY-MM-DD | 전체 페이지 수: N

## 엔티티
<!-- 섹션 안에서는 알파벳/가나다순 정렬 -->

## 개념

## 비교

## 질의
```

**확장 규칙:** 한 섹션이 50개 항목을 넘으면 첫 글자 또는 하위 도메인별 subsection으로 나눈다. index가 총 200개 항목을 넘으면 `_meta/topic-map.md`를 만들어 theme별로 페이지를 묶어 탐색 속도를 높인다.

### log.md 템플릿

```markdown
# 위키 로그

> 모든 wiki 작업을 시간순으로 기록한다. Append-only로 유지한다.
> 형식: `## [YYYY-MM-DD] action | subject`
> 작업 유형: ingest, update, query, lint, create, archive, delete
> 이 파일이 500개 항목을 넘으면 `log-YYYY.md`로 이름을 바꾸고 새 `log.md`를 시작한다.

## [YYYY-MM-DD] create | 위키 초기화
- 도메인: [domain]
- SCHEMA.md, index.md, log.md 구조 생성
```

## 핵심 작업

### 3. Ingest

사용자가 소스(URL, 파일, 붙여넣기)를 제공하면 wiki에 통합한다:

① **원본 소스 캡처:**
   - URL → 웹 글/랜딩은 `web_extract` 기반으로 `raw/articles/` 또는 `raw/reports/`에 저장
   - PDF/슬라이드/학회 논문은 `raw/papers/`에 저장
   - 연차보고서, annual report, marketplace annual filing 등은 `raw/reports/` 또는 `raw/papers/`로 분류해 별도 추적
   - 붙여넣은 텍스트 → 적절한 `raw/` 하위 디렉터리에 저장
   - 파일명은 설명적으로 작성: `raw/reports/` 또는 `raw/papers/` 기준으로 슬러그화
   - **raw frontmatter 추가**(`source_url`, `ingested`, 본문의 `sha256`, `cluster`, `questions`, `file_type`).
     같은 URL을 재 ingest할 때는 sha256을 다시 계산해 저장된 값과 비교한다. 같으면 건너뛰고, 다르면 drift로 표시한 뒤 업데이트한다.

② **수집 소스 타입 전략:**
   - “웹글만”으로 끝내지 말고 PDF, ppt/x, 공개 guide/report, annual report를 함께 후보화한다.
   - 초기 후보군은 `raw_type`(예: `articles`, `reports`, `papers`)로 분리해 관리한다.
   - 단일 벤더의 블로그가 아니라, 서로 다른 유형의 원천(컨설팅 리포트/학술 paper/산업 보고서/벤더 가이드)을 교차조합해 근거 편향을 줄인다.

③ **사용자와 핵심 takeaways 논의** — 도메인에서 무엇이 흥미롭고 중요한지 확인한다. 자동화/cron 맥락에서는 이 단계를 건너뛰고 바로 진행한다.

④ **이미 존재하는 내용 확인** — `index.md`를 검색하고 `search_files`로 언급된 엔티티/개념의 기존 페이지를 찾는다. 이것이 성장하는 wiki와 중복 파일 더미를 가르는 차이다.

⑤ **wiki 페이지 작성 또는 업데이트:**
   - **새 엔티티/개념:** `SCHEMA.md`의 페이지 생성 기준을 만족할 때만 생성한다(2개 이상 소스 언급 또는 한 소스의 중심 주제).
   - **기존 페이지:** 새 정보를 추가하고, 사실을 업데이트하며, `updated` 날짜를 갱신한다. 새 정보가 기존 내용과 충돌하면 업데이트 정책을 따른다.
   - **교차 참조:** 새로 만들거나 업데이트한 모든 페이지는 적어도 2개의 다른 페이지에 `[[wikilinks]]`로 링크한다. 기존 페이지가 역방향으로 링크하는지도 확인한다.
   - **태그:** `SCHEMA.md` taxonomy에 있는 태그만 사용한다.
   - **출처 표시(Provenance):** 3개 이상의 소스를 종합한 페이지에서는 특정 소스에서 온 주장 문단 끝에 `^[raw/articles/source.md]` marker를 붙인다. (비-article 자료는 `raw/reports/..` 또는 `raw/papers/..` 경로를 문단 marker에 반영)
   - **신뢰도(Confidence):** 의견이 많거나 빠르게 변하는 주제에는 frontmatter에 `confidence: medium` 또는 `low`를 설정한다. 여러 소스로 잘 뒷받침되지 않으면 `high`로 설정하지 않는다.

⑥ **navigation 업데이트:**
   - 새 페이지를 `index.md`의 올바른 섹션에 알파벳 순으로 추가한다.
   - index header의 "Total pages" 수와 "Last updated" 날짜를 갱신한다.
   - `log.md`에 append한다: `## [YYYY-MM-DD] ingest | Source Title`
   - 생성/수정한 모든 파일을 로그 항목에 나열한다.

⑦ **변경 내용 보고** — 생성 또는 수정한 모든 파일을 사용자에게 나열한다.

단일 소스 하나가 5~15개 wiki 페이지 업데이트로 이어질 수 있다. 이것은 정상이며, wiki가 복리처럼 성장하는 효과다.

### 2. Query

사용자가 wiki 도메인에 대해 질문하면:

> Strict grounding note: 사용자가 “이 wiki 안의 내용만”, “여기에 있는 내용만”처럼 범위를 제한하면, 반드시 `references/strict-wiki-grounding-and-rubric-corpus.md`를 따른다. `llm-wiki` 스킬 본문은 절차 지침일 뿐 도메인 근거가 아니며, `SCHEMA.md` taxonomy만으로 구체 전략을 추론하면 안 된다.

> 루브릭/정량 KPI 질문처럼 목표 점수(예: 90점)를 명시한 경우, 웹 아티클 단일군이 아니라 `raw/articles`, `raw/reports`, `raw/papers`를 동시에 확장해 근거군을 다양화하고, 질문별 커버리지가 cluster/question 단위로 충분한지 점검한다. 질문당 근거군이 적으면 수치형 decision-rule만 주장하는 형태로 과신하지 않는다.

① **`index.md` 읽기** — 관련 페이지를 식별한다.
② **100페이지 이상의 wiki**에서는 모든 `.md` 파일에 대해 핵심 용어로 `search_files`도 실행한다. index만으로는 관련 내용을 놓칠 수 있다.
③ **관련 페이지 읽기** — `read_file`을 사용한다.
④ **컴파일된 지식으로 답변 종합** — 근거로 사용한 wiki 페이지를 인용한다: "[[page-a]]와 [[page-b]]를 기준으로..."
⑤ **근거 부족 시 추론하지 않기** — 사용자가 "이 wiki 안의 내용만", "여기에 있는 내용만"처럼 범위를 제한하면, 스킬 본문/일반 지식/SCHEMA taxonomy에서 답을 추론하지 않는다. 실제 wiki 본문에 답변 근거가 없으면 "현재 wiki에는 이 질문에 답할 충분한 근거가 없습니다"라고 말하고, 확인된 파일/페이지와 부족한 근거를 짧게 설명한다. SCHEMA.md의 도메인·태그는 "이 질문이 어떤 주제에 속할 수 있는지"까지만 말할 수 있으며, 구체적 진단·권고의 근거로 확장하지 않는다.
⑥ **외부 자료로 wiki를 보강한 뒤 답하기** — 사용자가 "자료를 수집해서 raw에 넣고 ingest한 뒤 wiki 내용으로 답하라"고 하면, 답변 전에 공개 소스를 `raw/`에 frontmatter+sha256로 저장하고, `concepts/`/`comparisons/`/`queries/`로 컴파일한 뒤 그 본문만 근거로 답한다. 대량 주제는 manifest(`_meta/*source-manifest*.json`)로 URL을 관리하고, subagent를 병렬로 써도 subagent 결과는 URL 후보/초안으로만 취급하며 부모가 raw 저장·페이지 생성·검증을 수행한다.
⑦ **평가 루브릭/종료조건이 있을 때 한계 표시** — 루브릭이 회사별 baseline, 재무 수치, 표본/MDE, 경쟁자별 데이터 같은 비공개/문맥 의존 데이터를 요구하면, 공개 인터넷 자료만으로 엄격 점수 목표를 달성했다고 주장하지 않는다. 가능한 산출물은 (a) 공개 근거 corpus, (b) wiki 기반 답변 템플릿/초안, (c) 실제 90점 달성에 필요한 데이터 체크리스트로 구분해 보고한다. 허위 수치나 임의 baseline을 만들어 종료조건을 만족한 것처럼 말하지 않는다.
⑧ **가치 있는 답변을 다시 저장** — 답변이 중요한 비교, deep dive, 새로운 종합이라면 `queries/` 또는 `comparisons/`에 페이지를 만든다. 단순 조회는 저장하지 않는다. 다시 도출하기 번거로운 답변만 저장한다.
⑦ **`log.md` 업데이트** — 질의와 저장 여부를 기록한다.

### 3. Lint

사용자가 wiki lint, health-check, audit, 상태점검을 요청하면 **항상 재현 가능한 고정 프로토콜**로 수행한다. 즉석 감상식 점검을 피하고, 같은 wiki를 다시 점검해도 같은 규칙/필드/severity가 나오도록 한다. Read-only 요청이면 `log.md` append를 포함한 어떤 수정도 하지 않는다.

#### Health-check levels

- **Level 0 — Orientation:** 활성 wiki path, `SCHEMA.md`, `index.md`, 최근 `log.md`, 파일/페이지 수를 확인한다.
- **Level 1 — Structural lint:** 필수 파일, index count 일치, index 누락/초과, frontmatter 필수 필드, type 값, tag taxonomy, wiki 본문 간 broken wikilink, orphan/inbound 0, outbound link 수, log rotation을 검사한다.
- **Level 2 — Source integrity:** raw frontmatter(`source_url`, `ingested`, `sha256`) 존재, raw category 분포, fetch report와 실제 raw count 차이, source drift를 검사한다.
- **Level 3 — Corpus coverage:** entities/concepts/comparisons/queries 비율, raw cluster 대비 compiled page coverage, 반복 등장 source/entity 후보 중 page 없는 항목, concept page별 source 수, long page split 후보, low-confidence/contested/single-source pages를 검사한다.
- **Level 4 — Purpose-specific audit:** 루브릭/질문셋/도메인 목표가 있으면 질문별 evidence coverage, articles/reports/papers 분산, private-data 필요 여부, wiki-only 답변 가능/불가능을 별도 판정한다.

#### Fixed report shape

가능하면 내부 결과를 다음 스키마로 정리하고, 사용자 보고도 같은 섹션 순서를 유지한다:

```json
{
  "scope": {"wiki_path": "...", "read_only": true, "levels": [0,1,2,3]},
  "counts": {"md_total": 0, "wiki_pages": 0, "raw_md": 0, "entities": 0, "concepts": 0, "comparisons": 0, "queries": 0},
  "status": "pass | warning | fail",
  "issues": [
    {"id": "coverage.entities.empty_with_large_raw_corpus", "severity": "warning", "level": 3, "rule": "...", "path": "...", "evidence": "...", "recommendation": "..."}
  ],
  "unverified": []
}
```

Severity 우선순위는 기본적으로 `broken wiki links/frontmatter invalid` > `index mismatch` > `raw sha256 drift` > `taxonomy violations` > `coverage gaps` > `style/split candidates` 순서로 둔다. 단, 사용자가 특정 목적(예: 루브릭 통과)을 제시하면 Level 4 이슈가 더 높은 우선순위를 가질 수 있다.

① **고립 페이지(Orphan pages):** `entities/`, `concepts/`, `comparisons/`, `queries/` 안의 wiki 본문 페이지만 대상으로 inbound `[[wikilinks]]`를 계산한다. `raw/`, `_meta/`, `SCHEMA.md`의 pseudo link나 웹 원문 안의 `[[...]]`는 broken/orphan 판정에 섞지 않는다.
```python
# execute_code로 수행 — 선택된 wiki의 본문 페이지만 프로그램으로 스캔
import os, re
from collections import defaultdict
wiki = "<selected wiki path>"
# entities/, concepts/, comparisons/, queries/의 모든 .md 파일 스캔
# 모든 [[wikilinks]]를 추출해 inbound link map 생성
# inbound link가 0개인 페이지가 orphan
```

② **깨진 wikilink:** `entities/`, `concepts/`, `comparisons/`, `queries/` 안의 wiki 본문 페이지가 존재하지 않는 wiki page를 가리키는 경우만 hard issue로 잡는다. raw 원문에 포함된 `[[...]]` 문자열은 source 품질/클리핑 이슈로 따로 다루고 structural broken link에 포함하지 않는다.

③ **Index 완전성:** 모든 wiki 페이지가 `index.md`에 있어야 한다. 파일시스템과 index 항목을 비교한다.

④ **Frontmatter 검증:** 모든 wiki 페이지에 필수 필드(title, created, updated, type, tags, sources)가 있어야 한다. 태그는 taxonomy에 있어야 한다.

⑤ **오래된 콘텐츠:** 같은 엔티티를 언급하는 가장 최신 source보다 `updated` 날짜가 90일 이상 오래된 페이지를 찾는다.

⑥ **모순:** 같은 주제의 페이지들이 서로 충돌하는 주장을 하는지 확인한다. 태그/엔티티를 공유하지만 다른 사실을 말하는 페이지를 찾는다. `contested: true` 또는 `contradictions:` frontmatter가 있는 모든 페이지를 사용자 검토 대상으로 표시한다.

⑦ **품질 신호:** `confidence: low` 페이지와, 단일 소스만 인용하면서 confidence 필드가 없는 페이지를 나열한다. 이들은 추가 corroboration을 찾거나 `confidence: medium`으로 낮출 후보이다.

⑧ **소스 drift:** `raw/`의 각 파일 중 `sha256:` frontmatter가 있는 파일은 해시를 재계산해 mismatch를 표시한다. 이 wiki의 raw sha256은 frontmatter 종료 뒤 본문에서 선행 blank line을 제외한 내용 기준으로 저장된 경우가 있으므로, drift 검증 시 `body = text[m.end():].lstrip("\n")` 방식도 확인해 false positive를 줄인다. mismatch는 raw 파일이 수정되었거나(원칙상 수정하면 안 됨), URL에서 ingest한 원본이 이후 변경되었음을 의미한다. hard error는 아니지만 보고할 가치가 있다.

⑨ **페이지 크기:** 200줄을 넘는 페이지를 표시한다. 분할 후보이다. 단, 보존용 query/deep-dive page는 의도적으로 길 수 있으므로 `style/split candidate`로 보고하고 hard error로 취급하지 않는다.

⑩ **태그 감사:** 사용 중인 모든 태그를 나열하고 `SCHEMA.md` taxonomy에 없는 태그를 표시한다.

⑪ **Corpus coverage gap:** schema가 특정 page type을 정의하고 raw corpus가 충분히 큰데 해당 type이 비어 있거나 거의 없으면 warning으로 보고한다. 예: `entities/`가 0개이고 raw source가 다수이며 schema에 회사/제품/플랫폼/사람 entity 정책이 있으면 `coverage.entities.empty_with_large_raw_corpus`로 표시한다. 이는 구조 오류가 아니라 탐색성/재사용성 저하 신호이며, 권장 조치는 (a) concept-first wiki 정책을 `SCHEMA.md`에 명시하거나 (b) 반복 등장 핵심 엔티티 5~10개를 짧은 entity page로 생성하는 것이다.

⑫ **Log rotation:** `log.md`가 500개 항목을 넘으면 rotate한다.

⑬ **결과 보고:** 구체적 파일 경로와 제안 조치를 severity별로 묶어 보고한다. 우선순위는 broken wiki links/frontmatter invalid > index mismatch > source drift > taxonomy violations > coverage gaps > contested pages > stale content > style issues 순으로 둔다. Read-only 요청에서는 `log.md` 업데이트를 하지 않고 `read_only: true`와 미수행 항목을 명시한다.

⑭ **`log.md`에 append:** read-only가 아닐 때만 `## [YYYY-MM-DD] lint | N issues found`를 append한다.

## Wiki 작업 방식

### 검색

아래 예시는 모두 `WIKI`가 이미 선택된 wiki path로 결정되었다고 가정한다. 여러 wiki에서 가져온 결과를 보고할 때는 wiki key를 prefix로 붙이거나(예: `ai:concepts/transformers.md`) 절대 경로를 사용한다.

```bash
# 내용으로 페이지 찾기
search_files "transformer" path="$WIKI" file_glob="*.md"

# 파일명으로 페이지 찾기
search_files "*.md" target="files" path="$WIKI"

# 태그로 페이지 찾기
search_files "tags:.*alignment" path="$WIKI" file_glob="*.md"

# 최근 활동
read_file "$WIKI/log.md" offset=<last 20 lines>
```

### 대량 Ingest

여러 소스를 한 번에 ingest할 때는 업데이트를 batch로 처리한다:
### 대량 Ingest

여러 소스를 한 번에 ingest할 때는 업데이트를 batch로 처리한다:
1. 모든 소스를 먼저 읽는다.
2. 모든 소스에서 엔티티와 개념을 식별한다.
3. 모든 엔티티/개념에 대해 기존 페이지를 확인한다(N번 검색하지 말고 한 번의 search pass로 처리).
4. 한 번의 pass에서 페이지를 생성/업데이트한다(중복 업데이트 방지).
5. 마지막에 `index.md`를 한 번만 업데이트한다.
6. batch 전체를 다루는 log 항목 하나를 작성한다.

### 루브릭 기준 corpus 구축

사용자가 “이 wiki 내용만으로 답변”하면서 특정 평가 루브릭의 고득점/통과를 종료조건으로 제시하면, 먼저 `references/rubric-calibrated-domain-corpus.md`를 읽는다. 핵심 주의점:
- 스킬 본문, SCHEMA taxonomy, 일반 지식은 답변 근거가 아니다. 실제 wiki 본문과 raw에서 컴파일된 페이지만 근거로 쓴다.
- 공개 자료 수집은 “인터넷 전체 학습”이 아니라 루브릭 통과에 필요한 최소 충분 corpus 구축으로 범위를 잡는다.
- 루브릭이 회사별 baseline, CAC/LTV/payback, 경쟁자별 수치, 표본/MDE 같은 실제 데이터를 요구하면 허위 수치를 만들지 않는다. 부족하면 “현재 wiki corpus로는 90점 달성 불가”라고 보고하고 필요한 데이터 체크리스트를 별도 산출물로 만든다.
- 자동 키워드 검증은 hard-cap 누락 탐지일 뿐이며 90점 통과 판정으로 보고하지 않는다.

### Archive

내용이 완전히 대체되었거나 도메인 범위가 바뀌었을 때:
1. `_archive/` 디렉터리가 없으면 생성한다.
2. 페이지를 원래 경로를 유지해 `_archive/`로 이동한다(예: `_archive/entities/old-page.md`).
3. `index.md`에서 제거한다.
4. 해당 페이지에 링크하던 모든 페이지를 업데이트한다. wikilink를 일반 텍스트 + "(archived)"로 바꾼다.
5. archive 작업을 log에 기록한다.

### Obsidian 연동

wiki 디렉터리는 기본적으로 Obsidian vault로 사용할 수 있다:
- `[[wikilinks]]`가 클릭 가능한 링크로 렌더링된다.
- Graph View가 지식 네트워크를 시각화한다.
- YAML frontmatter는 Dataview query에 활용된다.
- `raw/assets/` 폴더는 `![[image.png]]`로 참조하는 이미지를 담는다.

권장 설정:
- Obsidian attachment folder를 `raw/assets/`로 설정한다.
- Obsidian 설정에서 "Wikilinks"를 활성화한다(대개 기본 활성화).
- Dataview plugin을 설치해 `TABLE tags FROM "entities" WHERE contains(tags, "company")` 같은 query를 사용한다.

Obsidian skill을 이 스킬과 함께 사용할 때는 `OBSIDIAN_VAULT_PATH`를 선택된 wiki path와 같은 디렉터리로 설정한다. 여러 wiki가 있으면 Obsidian 관련 작업 전에 활성 `WIKI`와 같은 경로로 전환한다.

### Obsidian Headless (서버와 headless 머신)

디스플레이가 없는 머신에서는 desktop app 대신 `obsidian-headless`를 사용한다. GUI 없이 Obsidian Sync로 vault를 동기화하므로, 서버에서 실행되는 에이전트가 wiki에 쓰고 다른 기기의 Obsidian desktop에서 읽는 환경에 적합하다.

**설정:**
```bash
# Node.js 22+ 필요
npm install -g obsidian-headless

# 로그인(Obsidian Sync subscription이 있는 Obsidian 계정 필요)
ob login --email <email> --password '<password>'

# wiki용 remote vault 생성
ob sync-create-remote --name "LLM Wiki"

# wiki 디렉터리를 vault에 연결
cd "$WIKI"
ob sync-setup --vault "<vault-id>"

# 초기 sync
ob sync

# 지속 sync(foreground — background는 systemd 사용)
ob sync --continuous
```

**systemd로 지속 background sync:**
```ini
# ~/.config/systemd/user/obsidian-wiki-sync.service
[Unit]
Description=Obsidian LLM Wiki Sync
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/path/to/ob sync --continuous
WorkingDirectory=<selected wiki path>
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now obsidian-wiki-sync
# logout 후에도 sync가 살아 있도록 linger 활성화:
sudo loginctl enable-linger $USER
```

이렇게 하면 서버의 에이전트가 선택된 wiki에 쓰고, 노트북/폰의 Obsidian에서 같은 vault를 볼 수 있다. 변경 사항은 몇 초 안에 나타난다.

## 참고 워크플로우

- `references/wiki-rubric-corpus-workflow.md` — wiki-only 답변을 위해 공개 자료를 raw에 수집·ingest하고, 평가 루브릭/종료조건이 회사별 데이터를 요구할 때 정직하게 한계를 표시하는 대량 corpus 구축 패턴.
- `references/wiki-non-article-source-workflow.md` — 웹 아티클 외(보고서/PDF/학술/연차보고서) 소스 후보 발굴·분류·저장 실패 복구까지 포함한 수집 워크플로우.
- `references/marketing-rubric-source-diversification-workflow.md` — 루브릭 Q07/Q10/Q13/Q16/Q19 같은 hard-cap 문항에서 `articles/reports/papers` 분산 전략, 실패 복구, 질문별 커버리지 점검 패턴을 담은 실전 체크리스트.

## 주의사항

- **`raw/`의 파일은 절대 수정하지 않는다** — 소스는 immutable이다. 수정/정정은 wiki page에서 처리한다.
- **먼저 wiki를 결정한다** — 여러 wiki가 설정되어 있으면 orientation 전에 대상 key/path를 식별한다. 모호한 wiki에는 절대 쓰지 말고 사용자에게 선택을 요청한다.
- **항상 먼저 orientation한다** — 새 세션에서 어떤 작업을 하든 SCHEMA + index + 최근 log를 먼저 읽는다. 이 단계를 건너뛰면 중복 페이지와 교차 참조 누락이 생긴다.
- **항상 index.md와 log.md를 업데이트한다** — 이를 빼먹으면 wiki가 퇴화한다. 이 둘은 탐색의 backbone이다.
- **지나가는 언급만으로 페이지를 만들지 않는다** — `SCHEMA.md`의 페이지 생성 기준을 따른다. 각주에 한 번 등장한 이름은 entity page로 만들 이유가 없다.
- **교차 참조 없는 페이지를 만들지 않는다** — 고립된 페이지는 보이지 않는다. 모든 페이지는 최소 2개의 다른 페이지에 링크해야 한다.
- **Frontmatter는 필수다** — 검색, 필터링, stale content 감지에 필요하다.
- **태그는 taxonomy에서 가져온다** — 자유 태그는 noise로 무너진다. 새 태그가 필요하면 먼저 `SCHEMA.md`에 추가한 뒤 사용한다.
- **페이지는 훑어보기 쉽게 유지한다** — wiki page는 30초 안에 읽을 수 있어야 한다. 200줄을 넘으면 분할한다. 상세 분석은 별도 deep-dive page로 옮긴다.
- **대량 업데이트 전에는 묻는다** — ingest가 기존 페이지 10개 이상을 건드릴 것 같으면 먼저 사용자에게 scope를 확인한다.
- **log를 rotate한다** — `log.md`가 500개 항목을 넘으면 `log-YYYY.md`로 이름을 바꾸고 새로 시작한다. lint 중 log 크기를 확인해야 한다.
- **모순은 명시적으로 처리한다** — 조용히 덮어쓰지 않는다. 날짜와 소스로 양쪽 주장을 기록하고, frontmatter에 표시하며, 사용자 검토 대상으로 flag한다.
