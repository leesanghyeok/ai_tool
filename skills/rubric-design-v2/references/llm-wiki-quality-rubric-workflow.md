# llm-wiki 품질 루브릭 절차

## 목적

llm-wiki 문서 품질을 평가하는 임시 상태 점검를 재사용 가능한 95점 기준 루브릭으로 전환하는 패턴이다. 원천 자료 출처 추적, Obsidian 링크, 근거 범위, 결정론적 검사 경계를 분리한다.

## 핵심 차원

- 자료 포괄성와 출처 추적.
- 원천 자료 path가 클릭 가능한 Markdown/Obsidian 링크인지 여부.
- 주장과 자료 근거의 정합성.
- wiki 문서 구조와 한국어 우선 제목.
- 결정론적 checker로 확인 가능한 링크, 해시, 개수.
- judge가 평가해야 하는 종합 품질.

## 절차

1. 평가 대상 wiki 문서와 원천 자료 묶음을 고정한다.
2. 결정론적 checker가 확인할 항목을 분리한다: 링크 존재, frontmatter, 자료 개수, 해시, section 존재.
3. judge가 평가할 항목을 분리한다: 종합, 자료 사용 품질, 누락된 뉘앙스, 환각 위험.
4. hard gate를 만든다: 자료 없는 주장, 원천 path 일반 텍스트, 조작된 citation, 한국어 우선 실패.
5. JSON 점수카드 schema와 검증 script를 둔다.
6. 보정 sample과 canonical rubric을 분리한다.

## 주의사항

- wiki-only 요청에서는 원천 자료 밖 추론을 금지한다.
- 자료 추적와 보강 section의 path도 클릭 가능 링크여야 한다.
- 결정론적 checker 통과를 최종 품질 통과로 오해하지 않는다.
