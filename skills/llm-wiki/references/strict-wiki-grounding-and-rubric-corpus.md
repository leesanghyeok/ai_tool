# 엄격한 wiki grounding과 루브릭 기준 corpus 구축

사용자가 답변 근거를 특정 LLM wiki 안의 내용으로 제한하거나, 웹 자료를 `raw/`에 수집하고 루브릭을 만족할 만큼 지식을 ingest해 달라고 요청할 때 이 참고 문서를 사용한다.

## 엄격한 wiki-only 답변

사용자가 “이 위키 내용만”, “여기에 있는 내용만”, “llmwiki 안에 있는 내용만” 또는 같은 의미로 말하면 다음을 지킨다.

1. 대상 wiki의 실제 page만 답변 근거로 사용한다.
2. `llm-wiki` skill 본문 자체를 domain evidence로 사용하지 않는다. skill은 절차이지 내용 근거가 아니다.
3. `SCHEMA.md` taxonomy에서 구체 권고를 확장 추론하지 않는다. schema/domain/tag는 주제 관련성까지만 보여준다.
4. `index.md`에 관련 page가 없으면 wiki에 충분한 근거가 없다고 답한다.
5. 사용한 실제 wiki page를 인용한다. `SCHEMA.md`/`index.md`만 있는 상태라면 그것도 명시한다.

나쁜 패턴:

- 사용자가 “wiki only”로 B2B SaaS 또는 marketplace 질문을 했는데, agent가 `funnel`, `retention`, `go-to-market` 같은 schema tag만 읽고 일반 전략 답변을 생성한다.

올바른 패턴:

- “현재 wiki에는 이 질문에 답할 충분한 근거가 없습니다. 확인된 근거는 `SCHEMA.md`의 도메인/태그뿐이며, 구체 진단·개선안 페이지는 없습니다.”

## 루브릭 게이트 답변을 위한 corpus 구축

사용자가 인터넷 자료를 `raw/`에 수집하고 ingest해서 답변이 루브릭을 통과하게 해 달라고 요청하면 다음을 지킨다.

1. 루브릭을 먼저 읽고 hard cap/gate를 식별한다.
2. 모든 질문 파일을 읽고 domain별로 cluster화한다.
3. 유용할 때만 source discovery에 병렬 subagent를 사용한다. 부모 agent가 검증하고 write/ingest한다.
4. 웹 source는 `raw/articles/<cluster>/` 아래에 저장하고 frontmatter에 `source_url`, 필요 시 `fetched_via`, `ingested`, `sha256`, `cluster`, `questions`, `title`을 둔다.
5. source 하나당 좁은 page를 만들지 말고 class-level concept/comparison/query page로 ingest한다.
6. 수집이 audit 가능하도록 `_meta/` 아래에 source manifest와 fetch report를 추가한다.
7. mechanical gate용 validation script/report는 만들 수 있지만, keyword check를 실제 루브릭 통과와 혼동하지 않는다.
8. 가능하면 독립적인 strict review를 실행한다.
9. 루브릭이 회사별 baseline, unit economics, experiment, competitive data처럼 공개 인터넷 자료만으로 제공할 수 없는 정보를 요구하면 숫자를 만들지 말고 blocker를 정직하게 보고한다.
10. 루브릭 목표를 공개 자료만으로 정직하게 충족할 수 없으면 “required data for rubric pass” checklist를 만든다.

## 종료조건 정직성

사용자가 “인터넷 source를 계속 학습해서 20개 답변이 모두 90점 이상 나올 때까지” 같은 야심찬 종료조건을 설정해도, 생성 답변에 올바른 heading이나 keyword가 있다는 이유만으로 완료를 주장하지 않는다. 엄격한 루브릭에서는 hard cap에 대한 semantic review가 필요하다. hard cap이 비공개/회사 내부 데이터를 요구한다면 올바른 산출물은 조작된 pass/fail 숫자가 아니라 blocker report와 최선의 completed artifact다.
