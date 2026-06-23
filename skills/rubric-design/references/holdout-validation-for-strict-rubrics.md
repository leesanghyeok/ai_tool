# Holdout Validation for Strict Rubrics

Use when a rubric has been tightened against a calibration set and the user worries it may be overfit to those examples.

## Pattern

1. Keep the tuned rubric fixed for the holdout run.
2. Create a fresh set of prompts/questions that differ from the calibration set but cover the same task class.
3. Collect fresh isolated/new-session style answers without revealing the rubric, target score, or evaluation purpose.
4. Save every raw answer verbatim in a separate holdout folder, not mixed into the original calibration set.
5. Score the holdout answers with the fixed rubric using parallel subagents when possible:
   - Split answers into batches.
   - Tell each scorer to use only explicit evidence in the answer.
   - Require final score plus the binding cap/gate reason.
   - Do not ask batch scorers to compute the overall average; aggregate centrally.
6. Calculate the holdout average with a tool, not mental arithmetic.
7. Write a holdout validation report containing:
   - purpose and overfit concern,
   - question list path,
   - raw response folder,
   - score table,
   - sum/count/average,
   - pass/fail against the target,
   - interpretation and caveats.

## Folder shape

```text
<artifact-root>/<rubric-name>-validation/
  README.md
  questions-vN.md
  raw-session-responses/
    qNN-topic.md
  scores-<rubric-version>-holdout.md
```

## Scoring discipline

For strict rubrics with hard caps/gates:

- Treat long, polished playbooks as evidence only for structure/execution, not for expert quality.
- Separate “metric mentioned” from “numeric decision rule.”
- Separate “experiment suggested” from “testable experiment design” with comparison group, period, sample/MDE or success/stop criteria.
- Apply caps/gates based on explicit missing elements before allowing high scores.
- Keep the rubric unchanged during holdout validation; if results expose a flaw, create a new version after documenting holdout results.

## Useful interpretation

If both calibration and holdout averages meet the target, the rubric is less likely to be merely fit to the original examples. Still state caveats:

- The holdout answers may come from the same model family or prompting style.
- A strict rubric may be valid for “world-class only” gating but too harsh for general practitioner-quality assessment.
- Preserve both the softer general rubric and the strict gate rubric when they serve different decisions.
