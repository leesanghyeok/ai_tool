# 실제 응답 기반 rubric calibration 패턴

사용자가 지어낸 예시가 아니라 실제 model/session outputs에 맞춰 calibration된 재사용 가능한 rubric을 원할 때 이 reference를 사용한다.

## 워크플로우

1. 사용자가 destination을 명시적으로 승인하기 전까지 artifacts는 repos/wiki/skills 밖에 보관한다.
2. 다음 항목을 포함한 calibration folder를 만든다:
   - `questions-v1.md` — prompts/questions와 evaluation intent.
   - `raw-session-responses/` — 수정하지 않은 responses, sample당 파일 하나.
   - `scores-v1.md` — baseline rubric scores.
   - `rubric-gap-analysis.md` — scores가 너무 높거나 낮았던 이유.
   - `rubric-v2.md` 또는 canonical v2 rubric path.
   - `scores-v2.md` — 변경 후 re-scoring 결과.
   - `README.md` 및/또는 handoff file.
3. rubric, score goal, calibration intent를 노출하지 않고 isolated/new-session style로 실제 outputs를 수집한다.
4. 가능하면 original responses를 verbatim으로 보존한다. session history에서 복구한 경우 prior tool output에서 recovered되었다고 label한다.
5. rubric을 수정하기 전에 current rubric으로 score한다.
6. 높은 scores의 원인이 다음 중 무엇인지 분석한다:
   - rubric이 너무 permissive한지, 또는
   - sample이 실제로 강한 evidence를 포함하는지.
7. 새 session outputs가 rubric을 실제로 만족한다면 target threshold 아래로 억지로 밀어내지 않는다. 목표를 generic/framework/tactic-list answers가 과대평가되지 않도록 방지하는 것으로 재정의한다.
8. Rubrics는 주로 다음 방식으로 개선한다:
   - 더 엄격한 observable criteria,
   - local caps,
   - global caps,
   - 80+/90+ bands를 위한 high-score gates,
   - “mentioned”와 “used as a decision rule”의 분리.
9. 변경 후 re-score하고 distribution shift를 요약한다.
10. file paths, score tables, caveats, 다음 calibration needs를 handoff/README에 업데이트한다.

## Marketing rubric calibration에서 발견한 유용한 v2 개선점

- low-score caps뿐 아니라 high-score gates를 추가한다.
- 사용자가 world-class expert answers를 원할 때 measurement/financial judgment와 risk/assumption handling의 weight를 높인다.
- 길고 polished된 answers가 과도하게 보상되지 않도록 structure/readability의 영향을 줄인다.
- metric name-dropping과 expand/stop/pivot thresholds 같은 실제 decision rules를 구분한다.
- 80+ 또는 90+ scores에는 explicit assumptions, risk, failure alternatives, trade-offs를 요구한다.
- calibration samples와 scores는 canonical rubric document와 분리해서 유지한다.

## 함정

- 실제로 강한 outputs가 target threshold 아래로 인위적으로 밀려나도록 rubric을 overfit하지 않는다.
- reusable rubric에 오래된 calibration scores를 섞지 않는다. rubric이 진화하면서 scores는 drift한다.
- 하나의 domain-specific gate를 보편적으로 유효한 것으로 취급하지 않는다. 예를 들어 performance-marketing incrementality question은 GTM positioning question보다 broad market/competition analysis가 약해도 정당할 수 있다.
