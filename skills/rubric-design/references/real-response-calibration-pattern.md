# Real-response rubric calibration pattern

Use this when a user wants a reusable rubric calibrated against actual model/session outputs rather than invented examples.

## Workflow

1. Keep artifacts outside repos/wiki/skills until the user explicitly approves a destination.
2. Create a calibration folder with:
   - `questions-v1.md` — prompts/questions and evaluation intent.
   - `raw-session-responses/` — unedited responses, one file per sample.
   - `scores-v1.md` — baseline rubric scores.
   - `rubric-gap-analysis.md` — why scores were too high/low.
   - `rubric-v2.md` or the canonical v2 rubric path.
   - `scores-v2.md` — re-scoring after changes.
   - `README.md` and/or handoff file.
3. Collect actual outputs in isolated/new-session style without exposing the rubric, score goal, or calibration intent.
4. Preserve original responses verbatim where possible. If recovering from session history, label them as recovered from prior tool output.
5. Score with the current rubric before editing the rubric.
6. Analyze whether high scores are caused by:
   - the rubric being too permissive, or
   - the sample genuinely containing strong evidence.
7. Do not force all new-session outputs below a target threshold if they genuinely satisfy the rubric. Reframe the goal as preventing generic/framework/tactic-list answers from being over-scored.
8. Improve rubrics primarily with:
   - stricter observable criteria,
   - local caps,
   - global caps,
   - high-score gates for 80+/90+ bands,
   - separation between “mentioned” and “used as a decision rule.”
9. Re-score after changes and summarize the distribution shift.
10. Update the handoff/README with file paths, score tables, caveats, and next calibration needs.

## Useful v2 improvements found in the marketing rubric calibration

- Add high-score gates, not only low-score caps.
- Raise weight for measurement/financial judgment and risk/assumption handling when the user wants world-class expert answers.
- Reduce the effect of structure/readability so long, polished answers are not over-rewarded.
- Distinguish metric name-dropping from actual decision rules such as expand/stop/pivot thresholds.
- Require explicit assumptions, risk, failure alternatives, and trade-offs for 80+ or 90+ scores.
- Keep calibration samples and scores separate from the canonical rubric document.

## Pitfalls

- Do not overfit the rubric so genuinely strong outputs are artificially pushed below the target threshold.
- Do not mix old calibration scores into the reusable rubric; they drift as the rubric evolves.
- Do not treat one domain-specific gate as universally valid. For example, a performance-marketing incrementality question may legitimately have weaker broad market/competition analysis than a GTM positioning question.
