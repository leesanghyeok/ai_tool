# 비-article 소스 기반 wiki corpus 확장 워크플로우

목적
- 사용자 요청이 "자료 조사 더 열심히" 혹은 증빙 근거 보강일 때, 웹 아티클만 수집하는 것을 피하고 PDF/슬라이드/가이드/공개 보고서/연차보고서를 함께 수집한다.
- 나중에 루브릭/검증 질문에서 근거 누락이 생기지 않도록 corpus 커버리지를 증대한다.

핵심 패턴
1. 소스 타입 분리
- `raw/articles/` : 웹 아티클/가이드 랜딩형 콘텐츠
- `raw/reports/` : PDF가 아닌 공개 리포트/브랜드/가이드/플랫폼 문서
- `raw/papers/` : PDF 중심 학술 자료/연차보고서/연구 문서
- `MANIFEST`에 `cluster`, `raw_type`, `questions`, `file_type`을 명시

2. 매니페스트 기준 수집
- 단일 질의 당 `*_source-manifest*.json`에서 질문별 태그를 걸어 추적
- 최소 한두 개 클러스터(예: B2B, measurement, marketplace 등)로 분할해 다중 워커 수집

3. 추출 실패 복구 규칙
- `r.jina.ai` 텍스트 추출이 정상이 아닌데도 200/short body가 나오는 항목이 있으면,
  - URL 구조를 canonical HTML 랜딩으로 교체해서 재시도
  - 예: Google 연구 논문은 `research.google/pubs/...` 형태로 접근 후 `raw/papers` 저장
- 실패는 `fetch-failures-*`로 기록하고, 성공 항목만 ingestion으로 넘김.

4. 검증
- 수집 후 반드시 fetch report(JSON) 확인: `saved_or_exists`, `failed`
- raw 타입별 카운트(`raw/reports`, `raw/papers`) 점검으로 커버리지 확인
- `log.md`에 수집-요약 항목 append

운영 노트
- 동일 URL 재수집 시 `sha256` 비교를 사용해 변경분만 반영
- 질문 커버리지는 Q별 매핑에 포함된 `questions` 필드 기반으로 추적
- `openview`, `bessemer`, `demandbase`, `google`, `nber`, `airbnb` 등 공개 소스는 article/report/paper로 다양하게 혼합해 넣는 편이 품질 개선에 유리하다.