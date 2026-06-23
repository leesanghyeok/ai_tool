# 엄격한 Rubric을 위한 Holdout Validation

rubric이 calibration set에 맞춰 강화된 뒤, 사용자가 해당 예시에 overfit되었을 가능성을 걱정할 때 사용한다.

## 패턴

1. holdout 실행에서는 조정된 rubric을 고정된 상태로 유지한다.
2. calibration set과는 다르지만 동일한 task class를 포괄하는 새로운 prompts/questions 세트를 만든다.
3. rubric, target score, evaluation purpose를 공개하지 않고 fresh isolated/new-session 방식의 답변을 수집한다.
4. 모든 raw answer를 원본 그대로 별도의 holdout folder에 저장하고, 기존 calibration set과 섞지 않는다.
5. 가능하면 parallel subagents를 사용해 고정된 rubric으로 holdout answers를 채점한다:
   - answers를 batches로 나눈다.
   - 각 scorer에게 answer 안의 명시적 evidence만 사용하라고 지시한다.
   - final score와 binding cap/gate reason을 반드시 요구한다.
   - batch scorers에게 overall average를 계산하게 하지 말고, 중앙에서 aggregate한다.
6. holdout average는 암산이 아니라 tool로 계산한다.
7. 다음을 포함하는 holdout validation report를 작성한다:
   - purpose와 overfit concern,
   - question list path,
   - raw response folder,
   - score table,
   - sum/count/average,
   - target 대비 pass/fail,
   - interpretation과 caveats.

## 폴더 구조

```text
<artifact-root>/<rubric-name>-validation/
  README.md
  questions-vN.md
  raw-session-responses/
    qNN-topic.md
  scores-<rubric-version>-holdout.md
```

## 채점 규율

hard caps/gates가 있는 엄격한 rubrics의 경우:

- 길고 잘 다듬어진 playbooks는 structure/execution의 evidence로만 취급하고, expert quality의 evidence로 보지 않는다.
- “metric mentioned”와 “numeric decision rule”을 구분한다.
- “experiment suggested”와, comparison group, period, sample/MDE 또는 success/stop criteria가 있는 “testable experiment design”을 구분한다.
- 높은 scores를 허용하기 전에, 명시적으로 누락된 elements를 기준으로 caps/gates를 적용한다.
- holdout validation 중에는 rubric을 변경하지 않는다. 결과가 결함을 드러내면 holdout results를 문서화한 뒤 새 version을 만든다.

## 유용한 해석 기준

calibration과 holdout averages가 모두 target을 충족하면, rubric이 원본 examples에만 맞춰졌을 가능성은 낮아진다. 그래도 다음 caveats를 명시한다:

- holdout answers가 동일한 model family나 prompting style에서 나왔을 수 있다.
- 엄격한 rubric은 “world-class only” gating에는 타당할 수 있지만, 일반 practitioner-quality assessment에는 지나치게 엄격할 수 있다.
- 더 부드러운 general rubric과 엄격한 gate rubric이 서로 다른 decisions에 쓰인다면 둘 다 보존한다.
