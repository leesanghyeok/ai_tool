# AI 품질 피드백 루프 참고 노트

## 목적

AI/LLM 품질 개선을 위해 feedback log, eval set, rubric, golden sample, pairwise comparison, RAGAS, DSPy, Reflexion 같은 도구를 어떻게 조합할지 정리한다. 이 문서는 방법론 선택을 돕는 참고 자료이며, 특정 tool 이름 자체를 점수로 보상하지 않는다.

## 주요 루프

1. 사용자 불만족과 실패 사례를 raw feedback으로 남긴다.
2. 중복 제거와 taxonomy 정리를 거쳐 평가 후보를 만든다.
3. 실패 유형을 rubric criterion, cap, test case, golden sample로 변환한다.
4. model 또는 agent output을 반복 채점한다.
5. 점수 변화와 실제 사용자 만족이 함께 개선되는지 확인한다.

## 평가 방식

- 절대 점수 rubric: checklist와 cap으로 안정적인 score를 만든다.
- pairwise comparison: 두 output의 상대 품질을 비교한다.
- golden set: 반복 regression 확인에 사용한다.
- RAG 평가: retrieval, grounding, citation quality를 분리한다.
- prompt/program optimization: DSPy 같은 도구를 쓰더라도 평가 기준과 held-out set을 분리한다.

## 주의사항

- feedback raw log와 처리 ledger를 섞지 않는다.
- calibration sample을 canonical rule로 오해하지 않는다.
- metric이 올라도 실제 task success가 나빠지면 루브릭을 재검토한다.
