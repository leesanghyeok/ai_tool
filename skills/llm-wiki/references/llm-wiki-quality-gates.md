# LLM Wiki 품질 게이트

사용자가 `llm-wiki`가 품질 루브릭을 통과할 때까지 평가하거나 개선해 달라고 요청할 때 이 참고 문서를 사용한다.

## 인증 기준선

재사용 가능한 강한 wiki는 보통 `95/100` 같은 높은 기준선을 통과해야 한다. 다만 원점수만으로는 충분하지 않다. 인증에는 hard-gate 차원의 만점도 함께 필요하다.

1. 구조와 탐색성
2. 페이지 단위 schema 준수
3. 링크 그래프와 지식 연결성
4. 출처 무결성과 provenance

D1-D4 hard gate 중 하나라도 감점되면, 원점수가 90점 이상이어도 인증 실패로 보고한다.

## 출처 provenance는 클릭 가능해야 한다

plain text 또는 backtick raw 경로만으로는 Markdown/Obsidian에서 이동하기 어렵기 때문에 충분하지 않다.

```markdown
- `raw/articles/source.md`  # 불충분
```

다음처럼 클릭 가능한 링크를 선호한다.

```markdown
- [raw/articles/source.md](../raw/articles/source.md)
- [[raw/articles/source]]
```

`## 출처 추적`뿐 아니라 `## 출처 보강`, `추가 근거:` 같은 supplemental source 섹션의 모든 raw source 경로도 클릭 가능해야 한다. Frontmatter `sources:`는 구조 필드이므로 별도이고, 본문에 노출되는 raw path는 사용자가 바로 이동할 수 있어야 한다.

## 한국어 human-facing 제목

한국어 wiki에서는 제목이 고유명사인 경우를 제외하고 사람이 읽는 제목을 한국어 우선으로 작성한다.

좋은 예:

```yaml
title: B2B SaaS 퍼널 경제성과 GTM 진단
```

```markdown
# B2B SaaS 퍼널 경제성과 GTM 진단
```

허용되는 고유명사 예:

```yaml
title: Google
title: Meta
title: Airbnb
```

호환성 표면은 안정적으로 유지한다. YAML key, enum 값, tag, raw path, command, identifier는 영어로 남겨도 된다. 단, 한국어 wiki의 설명형 compiled page filename/slug는 한국어를 포함해야 하며, proper noun entity filename은 영어 허용이다.

## deterministic checker 경계

deterministic check에 적합한 항목:

- 필수 파일/디렉터리
- index count와 index membership
- frontmatter field
- type enum
- tag taxonomy
- compiled page wikilink만 대상으로 하는 검사(raw source noise 제외)
- orphan page
- raw frontmatter와 sha256 drift
- clickable provenance/source links
- 한국어 제목 heuristic
- log와 `_meta` artifact

판정자/heuristic check로 라벨링해야 하는 항목:

- semantic link relevance
- synthesis quality
- domain coverage
- entity 승격이 충분한지 여부

## 안전한 개선 순서

1. checker를 실행하고 hard-gate 실패를 먼저 확인한다.
2. softer D5-D7 점수를 최적화하기 전에 D1-D4를 먼저 고친다.
3. 각 batch 후 checker를 다시 실행한다.
4. wiki가 통과한 뒤에만 scorecard를 `_meta/` 아래에 저장한다.
5. `log.md`에는 rubric, checker, scorecard path, pass/fail 결과를 append한다.

## 주의사항

- 원점수만으로 인증을 주장하지 않는다. pass/fail은 hard gate가 결정한다.
- 한국어 wiki에서 설명형 제목을 영어-only로 만들지 않는다.
- provenance/source 섹션을 non-clickable raw path로 만들지 않는다.
- `raw/` 파일 안의 pseudo-link를 compiled-page broken-link 검사에 포함하지 않는다.
- hash drift를 고치기 위해 raw body를 수정하지 않는다. 사용자가 명시 승인한 경우가 아니라면 현재 body를 accepted stored source로 보고 metadata correction만 수행한다.
