# 한국어 Wiki 생성

`llm-wiki` skill의 한국어 localization 동작을 업데이트하거나 검증할 때 이 참고 문서를 사용한다.

## 목표

대화가 한국어이거나 사용자가 한국어 출력을 명시적으로 요청한 경우, 새로 초기화되는 wiki 파일은 기본적으로 사람이 읽는 부분을 한국어로 작성한다.

- `SCHEMA.md`: heading, 설명 prose, comment, machine identifier가 아닌 예시
- `index.md`: title, guidance block, section heading, comment
- `log.md`: title, guidance block, 초기 log subject/body
- 이후 `entities/`, `concepts/`, `comparisons/`, `queries/` 아래 생성되는 wiki page: 본문 prose, section heading, index summary, log description

## 호환성을 위해 유지할 것

사용자가 명시적으로 요구하지 않는 한 machine-readable 또는 integration-sensitive surface는 번역하지 않는다.

- 환경변수: `WIKI_PATHS`, `WIKI_DEFAULT`, `WIKI_PATH`
- 파일/디렉터리명: `SCHEMA.md`, `index.md`, `log.md`, `raw/`, `entities/`, `concepts/`, `comparisons/`, `queries/`
- YAML/frontmatter key: `title`, `created`, `updated`, `type`, `tags`, `sources`, `confidence`, `source_url`, `sha256`
- enum/action 값: `entity`, `concept`, `comparison`, `query`, `summary`, `high`, `medium`, `low`, `ingest`, `update`, `query`, `lint`, `create`, `archive`, `delete`
- code block, command, path, URL, placeholder, taxonomy에서 사용하는 tag 값

`title:`은 human-facing field이므로 한국어로 쓸 수 있다. `type`, `tags`, `sources` 같은 구조 field는 schema를 따른다.

## 검증 체크리스트

localization 변경 후 다음을 확인한다.

1. `git diff --check`를 실행한다.
2. Markdown code fence 개수를 세고 짝수인지 확인한다.
3. 생성된 한국어 template에 남아 있으면 안 되는 영어 template phrase를 검색한다.
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
4. 필수 호환성 term이 남아 있는지 확인한다.
   - `WIKI_PATHS`
   - `WIKI_DEFAULT`
   - `WIKI_PATH`
   - `type: entity | concept | comparison | query | summary`
   - `confidence: high | medium | low`
   - `source_url`
   - `sha256`
   - `ingest, update, query, lint, create, archive, delete`
5. frontmatter에 필요한 skill metadata key가 유지되는지 확인한다.
