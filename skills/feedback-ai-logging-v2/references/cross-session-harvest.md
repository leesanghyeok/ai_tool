# 과거 세션 피드백 수확 노트

사용자가 “6월 19일 이후 세션 전체를 돌려줘”처럼 날짜 범위나 여러 과거 세션에서 누락된 feedback incident를 찾으라고 요청할 때 이 참고 문서를 사용한다.

## 목적

과거 세션 수확은 일반적인 현재 세션 수확보다 넓다. session history에서 사용자 정정, 재작업, 검증 실패, scope mismatch, 가벼운 planning correction을 찾아 이미 `raw/feedback/` 아래 기록된 사건과 비교한다.

산출물은 여전히 raw feedback log다. 사건 하나마다 Markdown 파일 하나를 만들며, 이 단계에서 concept page, promoted rule, rubric page를 만들지 않는다.

## 절차

1. **기간과 feedback wiki 경로를 확정한다.**
   - 사용자가 다른 feedback wiki를 명시하지 않으면 기본 목적지는 `$HOME/wiki/raw/feedback`이다.
   - `WIKI_DEFAULT`가 domain wiki를 가리킨다는 이유만으로 feedback log를 domain wiki에 넣지 않는다.
2. **세션 후보를 수집한다.**
   - session search, platform link, source metadata에서 범위 내 session id와 source reference를 찾는다.
   - secrets, credentials, unrelated private state는 읽지 않는다.
3. **수정/불만족 신호가 있는 user message 후보를 추린다.**
   - 유용한 한국어 신호: `아니`, `그게 아니라`, `잘못`, `빠졌`, `누락`, `틀렸`, `이상한데`, `아씨`, `오타`, `하지마`, `하면 안`, `절대`, `기본값`, `변수`, `직접`, `고쳐`, `수정`, `반영`, `피드백`, `기록`.
   - 자동 skill invocation prompt나 “응 진행해줘” 같은 정상 승인은 주변 맥락에 prior correction이 있을 때만 후보로 본다.
4. **후보가 많으면 기간 또는 session shard로 병렬 검토한다.**
   - subagent는 structured incident candidate JSON만 반환한다.
   - parent가 최종 taxonomy 정규화, 중복 검사, 파일 작성, 검증을 담당한다.
   - 각 후보는 `session_id`, `timestamp`, `slug`, `task_type`, `severity`, `categories`, expected behavior, actual behavior, evidence excerpt, candidate rule, checklist items를 포함한다.
5. **기존 로그와 비교한다.**
   - 현재 날짜 폴더가 아니라 전체 `$WIKI/raw/feedback/**`를 검색한다.
   - filename만 보지 말고 Situation, Expected Behavior, Evidence, Candidate Agent Rule의 의미를 비교한다.
6. **taxonomy를 정규화한다.**
   - `task_type`은 main skill의 controlled taxonomy 중 하나여야 한다.
   - `categories`도 controlled taxonomy를 사용한다. subagent가 만든 one-off label은 기존 category로 mapping한다.
7. **새 사건만 immutable Markdown으로 작성한다.**
   - body-only `sha256`을 계산한다.
   - 사건 하나에 파일 하나만 만든다.
8. **각 파일을 검증한다.**
   - required frontmatter, controlled taxonomy, body hash, one incident per file, feedback path를 확인한다.
9. **최종 보고를 만든다.**
   - 생성 수, 중복 skip 수, evidence 부족/비실패 제외 수, severity/category 분포, 실제 생성 경로를 보고한다.

## 자주 나오는 후보 패턴

아래는 새 category label이 아니라 기존 taxonomy로 분류해야 하는 예시다.

- raw layer와 derived layer 혼동 → `context-misread`, `requirement-miss`, `specificity`.
- 반복 보고 template에서 format drift 발생 → `format`, `requirement-miss`.
- side-effect automation 기본값이 공격적임 → `decision-criteria`, `specificity`.
- 현재 plan에 미래 workflow stage를 섞음 → `context-misread`, `requirement-miss`, `specificity`.
- 실제 독립 output 대신 synthetic example 사용 → `verification`, `context-misread`, `evidence`.
- threshold/gate validation 실패를 실패로 처리하지 않음 → `verification`, `decision-criteria`.
- batch logging에서 idempotency 누락 → `requirement-miss`, `specificity`, `actionability`.
- checker는 통과했지만 user-visible requirement를 확인하지 않음 → `verification`, `requirement-miss`, `format`.

## 주의사항

- keyword가 있다는 이유만으로 모든 user message를 기록하지 않는다. 유효한 incident에는 expected behavior, actual behavior, concrete mismatch, evidence, reusable candidate rule이 필요하다.
- subagent가 만든 taxonomy 값을 frontmatter에 그대로 쓰지 않는다. 작성 전에 controlled taxonomy로 정규화한다.
- automation이 생성한 historical feedback prompt는 보통 user dissatisfaction이 아니라 harvest invocation이다.
- 여러 session을 하나의 거대한 feedback 파일로 합치지 않는다.
- 주제가 비슷하다는 이유만으로 duplicate 처리하지 않는다. expected behavior나 candidate rule이 다르면 별도 사건으로 기록한다.
