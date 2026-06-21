# 마케팅 루브릭 대응을 위한 근거 소스 다각화 워크플로우

루브릭 90점 류 질문(특히 `마케팅이 뭐야` 같은 정량 의사결정형 초안 작성)에서 흔히 생기는 함정은 `articles` 중심 수집이다. 웹 아티클 단독은 hard-cap을 낳으므로, 수집 전략을 유형별로 분기한다.

## 핵심 원칙

- 소스는 최소 3타입을 기본으로 분리 수집한다.
  - `raw/articles/`: 일반 웹 글/블로그/랜딩
  - `raw/reports/`: 공개 리포트, 가이드, 벤더 문서, annual report류(원문이 HTML/MD 변환)
  - `raw/papers/`: PDF/학술논문/연구 노트
- 매니페스트(`*_source-manifest*.json`)에 `cluster`, `raw_type`, `questions`, `file_type`을 넣어 질문 커버리지를 추적한다.
- `subagent`가 URL 후보를 제공해도, 부모 에이전트가 반드시 실제 저장/검증/병합을 수행한다.

## 권장 수집 패턴 (재현 가능)

1. 후보군 수집
   - 질문별 Q-mapping을 기반으로 URL 후보를 모은다.
   - Q 타깃이 서로 다를수록 cluster 별 분리(manifest 분할)
2. fetch 실행
   - script 기반으로 manifest를 읽어 순회 저장
   - 기존 파일은 `exists`로 분류해 중복 저장 회피
3. 실패 처리
   - `r.jina.ai`가 200이면서 텍스트 길이가 비정상적으로 짧은 PDF 원본을 반환하면 실패로 기록
   - 동일 문서의 canonical HTML 경로로 대체 재시도
4. 결과 검증
   - `saved_or_exists`/`failed` 집계와 raw 타입별 개수를 확인
   - Q01~Q20 등 질문별 카운트가 기대 범위를 벗어나면 후보군 재확보
5. 로그
   - 수집 확장 및 재시도 이유를 `log.md` append-only로 남긴다.

## 패턴에서 배운 실패 교훈

- static pdf URL은 가끔 content-length가 매우 작아서 실패로 보이는 경우가 많다.
- 동일 도메인이라도 `research.google/pubs/...`와 `static.googleusercontent.com/...pdf` 같은 대체 경로를 번갈아 사용하면 회수율이 오른다.
- 같은 URL을 반복 삽입하지 않도록 dedupe와 idempotent 실행이 중요하다.

## 확인 항목

- 수집 후 `raw/reports`와 `raw/papers` 비율이 극단적으로 한쪽으로 치우치지 않게 유지한다.
- Q07/Q10/Q13/Q16/Q19 같은 비중 높은 질문군에는 ABM/웨비나/카테고리/경쟁 wedge 등 비-article 자료를 포함한다.
- 루브릭 점검 이전에 corpus 보강 로그와 fetch report를 먼저 점검한다.

