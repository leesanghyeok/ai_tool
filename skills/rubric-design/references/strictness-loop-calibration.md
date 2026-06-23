# Strictness-loop calibration for hard target averages

Use this reference when a user asks to iteratively tighten a rubric until a measured score target is reached, e.g. “keep evolving the rubric until the average score is below 40 or v10 is reached.”

## Pattern

1. Define explicit stop conditions before editing the rubric.
   - Example: `average_score < 40 OR rubric_version == v10`.
   - Treat the score target as a calibration objective, not as permission to fabricate scores.

2. Establish the current baseline with real calculation.
   - Read the current scores table.
   - Compute the average with a tool/script, not mentally.
   - Record the baseline in the loop log.

3. Use parallel subagents for independent diagnosis when the sample set spans domains.
   - Split by domain or sample cluster, not by arbitrary line ranges.
   - Ask each subagent to identify over-credit patterns and propose caps/gates.
   - Keep outputs as proposals; synthesize the final rubric yourself.

4. Tighten by adding gates/caps before changing point weights.
   - For a hard average target, weights alone rarely move scores enough.
   - Add 40+ / 60+ / 75+ gates and domain-specific hard caps.
   - Distinguish “mentions a metric” from “uses a numeric decision rule.”

5. Re-score in parallel.
   - Split the sample answers into batches.
   - Instruct subagents to apply the new rubric strictly and return final_score + cap/gate reason only.
   - Compute the average centrally after collecting results.

6. Stop immediately when the first stop condition is met.
   - If `average < target`, do not continue to later versions.
   - If the version ceiling is reached, stop and report the best achieved average.

7. Save durable artifacts.
   - New rubric version: `...rubric-vN.md`
   - Score table: `scores-vN.md`
   - Loop log: `strictness-loop.md`
   - Proposal files when subagents produced useful domain analyses.

## Useful strictness levers

- 40+ gate: require numeric decision rule, required economic metric, failure/stop condition, relevant customer/competition context, and explicit choice/forfeit.
- 60+ gate: require segment-specific strategy, competitor/substitute analysis, unit economics or financial scenario, real experiment design, risk/pivot, and trade-off.
- 75+ gate: require financial model, statistically/operationally credible experiment, resource constraints/opportunity cost, success/stop/scale rules, and pivot condition.
- Domain hard caps: cap answers that lack the domain’s essential proof.
  - B2B SaaS: ACV, sales cycle, CAC payback, pipeline source, conversion baselines.
  - DTC retention: purchase cycle, replenishment, cohort LTV, margin, holdout details.
  - App retention: activation event, aha moment, habit loop, cohort segmentation, LTV/CAC stop rule.
  - Premium repositioning: WTP, price anchor, premium proof, cannibalization/rollback.
  - Content marketing: cost, payback, opportunity cost, sourced vs influenced pipeline, kill/scale threshold.
  - Incrementality: MDE/sample, pre-period balance, contamination, confidence/uncertainty.
  - Pricing: revenue/churn scenarios, elasticity/WTP, grandfathering economics.
  - Competitive entry: competitor battlecard, wedge economics, ACV/CAC/payback, validation thresholds.

## Pitfalls

- Do not simply “grade harsher” without changing the rubric. Encode strictness as observable gates/caps.
- Do not lower strong answers arbitrarily; explain which explicit high-bar condition is missing.
- Do not let long, well-structured playbooks score highly unless they contain decision rules and economics.
- Do not continue the loop after the stop condition is met.
