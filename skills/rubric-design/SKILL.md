---
name: rubric-design
description: Use when designing, refining, or calibrating scoring rubrics for evaluating AI outputs, research summaries, documents, model responses, or agent work.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [rubric, evaluation, llm-as-judge, scoring, calibration]
    related_skills: [test-driven-development, writing-plans]
---

# Rubric Design

## Overview

Use this skill to design reusable, task-specific scoring rubrics. The goal is not merely to assign weights, but to produce a rubric that is actually usable by humans or LLM judges: purpose-driven, weighted, checklist-based, equipped with cap/penalty rules, and paired with a stable output template.

A good rubric separates four things:

1. **Evaluation purpose** — what the evaluator is trying to reward.
2. **Weights** — the user's value judgment about what matters most.
3. **Observable checklist criteria** — concrete evidence that can be checked.
4. **Caps and penalties** — rules for critical failures that should limit the final score.

Avoid relying only on broad range anchors such as “13–15 = excellent.” Range anchors are useful as explanatory aids, but they create large scoring variance. Prefer checklist-style scoring where each item has a small, explicit point value.

## When to Use

Use this skill when the user asks to:

- Design a new rubric.
- Improve or calibrate an existing rubric.
- Convert a vague evaluation standard into a 100-point scoring rubric.
- Build a rubric for LLM-as-a-Judge evaluation.
- Evaluate AI outputs, research summaries, documents, code reviews, model responses, or agent work.
- Define scoring criteria with checklist items, caps, penalties, and JSON output.
- Create a reusable evaluation template for repeated work.

Do not use this skill when:

- The user only wants a casual opinion and no scoring structure is needed.
- The task is pure factual lookup with no evaluative judgment.
- The user has already provided a complete rubric and only asks for direct scoring; in that case, apply the provided rubric unless it is ambiguous.

## Core Principles

### 1. Weights Are Value Judgments

Weights should reflect what the user considers important for this evaluation.

Examples:

- Literature quality matters most → increase coverage, evidence, citation quality, and research flow.
- Practical system design matters most → increase methodology comparison, applicability, calibration, and operational risk.
- Beginner-facing explanation matters most → increase conceptual accuracy, structure, clarity, and examples.
- Agent task evaluation matters most → increase requirement satisfaction, verification evidence, failure handling, and user intent alignment.

When modifying a rubric, ask: “What should this rubric reward more than the previous version?”

### 2. Checklists Are Observable Evidence

Do not stop at high-level categories like:

```text
Bias and reliability discussion — 20 points
```

Break the category into observable checklist items:

```text
Position/order bias explained — 3 points
Verbosity bias explained — 3 points
Self-preference/model-family bias explained — 3 points
Calibration problem explained — 3 points
Human agreement problem explained — 3 points
Mitigation strategies proposed — 5 points
```

The evaluator should be able to point to concrete evidence for each score.

### 3. Do Not Rely Only on Range Anchors

Range anchors such as `13–15 points = excellent` are too coarse for consistent scoring. If every category has a 2–3 point internal range, total scores can differ by 10+ points across evaluators.

Prefer:

```text
Category total: 15 points
- Criterion A: 2 points
- Criterion B: 2 points
- Criterion C: 3 points
- Criterion D: 3 points
- Criterion E: 5 points
```

Range anchors may be included only as secondary interpretation, not as the primary scoring mechanism.

### 4. Use Caps for Critical Failures

Important dimensions should receive higher weight. Critical conditions should receive caps or penalties.

Examples:

```text
If the answer is unrelated to the task, total score is capped at 40.
If a core requirement is completely missing, total score is capped at 60.
If fabricated citations are present, total score is capped at 60.
If there are multiple critical conceptual errors, total score is capped at 70.
If safety, legal, or security constraints are violated, total score is capped at 50.
```

Distinguish:

- **Important** → assign more points.
- **Fatal if missing/wrong** → define cap or penalty.

### 5. Rubrics Should Be Purpose-Specific

Do not force all tasks into a single fixed rubric. A rubric should be designed or adapted for the task purpose.

Use category templates only as starting points. The final rubric should reflect:

- The task goal.
- The intended use of the score.
- The user's priorities.
- The critical failure conditions.
- The desired output format.

### 6. Judge Output Should Be Structured

When the rubric will be used by an LLM judge, require structured output. At minimum, require:

- Category score.
- Checklist-level scores.
- Evidence for each score.
- Caps or penalties applied.
- Missing points.
- Strengths.
- Recommended revisions.
- Confidence and need for human review.

### 7. Judge Runs Should Be Context-Isolated

When a rubric is intended for LLM judging, design the judging workflow so the evaluator runs in a clean context rather than continuing the current conversation. The judge should receive a self-contained evaluation packet and must not use prior chat history, agent memory, implementation notes, or unstated assumptions as evidence.

Default pattern:

1. Build a self-contained evaluation packet containing only the evaluation target, evaluated output, rubric, allowed source/evidence bundle, cap rules, and JSON schema.
2. Spawn a new clean subagent/session to apply the rubric whenever practical.
3. Instruct the judge to use only the supplied packet and to treat missing packet evidence as missing evidence.
4. For multi-dimension or high-stakes rubrics, split scoring by dimension/checklist group across parallel clean subagents.
5. Have the parent agent validate shard JSON, check missing/duplicate criteria, reconcile contradictions, sum scores, and apply global caps centrally.

Use same-context judging only for low-stakes quick checks or when a clean subagent is unavailable; label the exception explicitly in the scorecard.

## Rubric Design Workflow

### Step 1: Define Evaluation Purpose

Clarify the evaluation target and why it is being scored.

Answer these questions:

```text
What is being evaluated?
Who will use the score?
What decision will the score support?
What does an excellent output look like?
What failures should sharply reduce trust?
```

### Step 2: Define the Evaluation Target

Examples:

- LLM response.
- Literature survey.
- Research briefing.
- Code implementation.
- PR review.
- Planning document.
- Agent task result.
- Model evaluation report.

State the target explicitly in the final rubric.

### Step 3: Select Evaluation Dimensions

Choose 5–8 dimensions. Too few dimensions make the rubric vague; too many make it hard to apply.

Common dimension candidates:

- Requirement satisfaction.
- Factual/conceptual accuracy.
- Coverage.
- Methodology comparison.
- Analytical depth.
- Evidence and citation quality.
- Practical applicability.
- Structure and readability.
- Verification evidence.
- Risk, limitation, and bias awareness.
- User intent alignment.

### Step 4: Assign Weights

Use 100 points unless the user requests another scale.

Recommended distribution:

```text
Core dimensions: 2–4 dimensions, 60–75 total points
Supporting dimensions: 2–4 dimensions, 25–40 total points
```

Avoid making every dimension equal unless the user explicitly wants equal weighting. Equal weighting often hides the actual evaluation priority.

### Step 5: Convert Weights into Checklists

For each dimension, break the score into small checklist items, usually 1–5 points each.

Checklist items should be:

- Observable.
- Specific.
- Separately scorable.
- Tied to the task purpose.
- Not redundant with other checklist items.

Bad:

```text
Good analysis — 20 points
```

Good:

```text
Analysis depth — 20 points
- Identifies the main tradeoffs — 5
- Explains causal relationships or mechanisms — 5
- Compares alternatives rather than listing them — 5
- States limitations and uncertainty — 3
- Provides decision-relevant implications — 2
```

### Step 6: Add Caps and Penalty Rules

Caps and penalties should be explicit and applied after checklist scoring.

Use global caps for failures that affect the entire evaluation:

```text
If the output is off-topic, total score is capped at 40.
If the output ignores the main user request, total score is capped at 60.
If fabricated sources are present, total score is capped at 60.
If a critical safety constraint is violated, total score is capped at 50.
```

Use local caps for failures inside a dimension:

```text
If no sources are provided, Evidence Quality is capped at 4/10.
If methods are only listed but not compared, Methodology Comparison is capped at 8/20.
If tests were not run, Verification Evidence is capped at 5/15.
```

If multiple global caps apply, use the lowest cap.

### Step 7: Define Judge Execution Mode

Before writing the judge prompt, define how the judging run will be isolated from the current conversation.

Default execution mode:

1. Use a clean new subagent/session for judging rather than continuing in the current context.
2. Pass a self-contained evaluation packet only: evaluation target, evaluated output, rubric, allowed evidence/source bundle, cap and penalty rules, and JSON schema.
3. Exclude current conversation history, hidden memory, prior implementation notes, and user preferences unless they are explicitly part of the evaluation target or evidence packet.
4. For multi-dimension, long, or high-stakes evaluations, shard the rubric by dimension/checklist group and run parallel clean subagents.
5. Require each shard judge to return only its assigned dimension/checklist JSON.
6. Aggregate centrally in the parent agent: validate JSON, detect missing or duplicate criteria, reconcile contradictions, sum scores, apply local caps, and apply global caps after merging.

If same-context judging is used, the scorecard must label it as an exception and explain why context contamination risk is acceptable.

### Step 8: Define Judge Instructions

When an LLM will apply the rubric, include strict instructions:

```text
1. Run this evaluation in a clean context. Ignore prior conversation, memory, or assumptions not included in the evaluation packet.
2. Use only the supplied rubric, evaluated output, and explicitly supplied evidence bundle.
3. Do not decide the total score first.
4. Score checklist items first.
5. Do not give credit for implied or assumed content.
6. Quote or summarize evidence for each score.
7. If the packet lacks evidence needed for a criterion, assign low or zero credit instead of inferring from outside context.
8. Apply local caps and penalties after checklist scoring.
9. Apply global caps after local caps; if multiple global caps apply, use the lowest cap.
10. Long outputs are not automatically better.
11. Technical vocabulary is not automatically better.
12. If evaluating a dimension shard, return only that shard result and do not compute the final total unless instructed.
13. Return only the requested structured output.
```

### Step 9: Define Output Template

The final rubric should include both:

1. A human-readable rubric document.
2. A machine-readable JSON output schema for judge results.

Use the templates below.

### Step 10: Calibrate the Rubric

Before using the rubric at scale, test it on examples.

Recommended calibration loop:

1. Score 3–5 sample outputs.
2. Check whether the ranking matches human judgment.
3. Identify checklist items that are too vague or too easy to satisfy.
4. Adjust weights and caps.
5. Re-score the samples.
6. Freeze the rubric version once results are stable.

If scores vary more than 5–8 points between judges on the same output, tighten checklist criteria.

## Reusable Output Template: Human-Readable Rubric

Use this template when producing the final rubric for a user.

```markdown
# {task_name} Evaluation Rubric

## 1. Evaluation Purpose

{evaluation_purpose}

## 2. Evaluation Target

{evaluation_target}

## 3. Total Score

100 points

## 4. Dimension Summary

| Dimension | Points | Evaluation Focus |
|---|---:|---|
| {dimension_1} | {points} | {focus} |
| {dimension_2} | {points} | {focus} |
| ... | ... | ... |
| **Total** | **100** | |

## 5. Detailed Scoring Criteria

### 5.1 {dimension_1} — {points} points

| Checklist Criterion | Points | Recognition Standard |
|---|---:|---|
| {criterion_1} | {points} | {observable_evidence} |
| {criterion_2} | {points} | {observable_evidence} |

Local caps/penalties:
- {local_cap_rule}
- {local_penalty_rule}

### 5.2 {dimension_2} — {points} points

| Checklist Criterion | Points | Recognition Standard |
|---|---:|---|
| {criterion_1} | {points} | {observable_evidence} |
| {criterion_2} | {points} | {observable_evidence} |

## 6. Global Caps and Penalties

- {global_cap_rule_1}
- {global_cap_rule_2}

## 7. Score Interpretation

| Total Score | Interpretation |
|---:|---|
| 90–100 | Excellent; ready to use with little or no revision |
| 80–89 | Good; usable with minor revision |
| 70–79 | Adequate; core requirements met but notable gaps remain |
| 60–69 | Weak; substantial revision needed |
| 0–59 | Not acceptable; major requirements missing or unreliable |

## 8. Scoring Procedure

1. Confirm that the evaluated output is in scope.
2. Check whether any global cap applies.
3. Score each checklist item independently.
4. Sum dimension scores.
5. Apply local caps and penalties.
6. Apply global caps.
7. Report evidence, missing points, and recommended revisions.

## 9. Judge Prompt

```text
{judge_prompt}
```

## 10. JSON Output Schema

```json
{json_schema}
```
```

## Parallel Clean-Subagent Judging Workflow

Use this workflow when the rubric has multiple dimensions, a long evaluated output, high-stakes consequences, or a user explicitly requests parallel inspection.

1. Parent agent prepares a bounded evaluation packet: rubric, evaluated output, allowed evidence, score schema, and cap rules.
2. Parent splits the rubric into dimension or checklist shards with non-overlapping score ownership.
3. Parent spawns clean subagents in parallel; each subagent receives only the packet plus its assigned shard.
4. Each shard judge returns strict JSON for its assigned criteria, including evidence and any local cap/penalty suggestions.
5. Parent validates every shard result for JSON parseability, score bounds, missing criteria, duplicate criteria, and evidence grounding.
6. Parent reconciles contradictions between shards before final scoring.
7. Parent applies local caps, then applies global caps centrally after all shard scores are merged.
8. Parent emits the final human-readable scorecard and machine-readable JSON result.

Do not let shard judges independently decide the final total unless the rubric is intentionally single-shard. Shard judges may flag possible global caps, but the parent agent applies the final global cap.

## Reusable Output Template: LLM Judge JSON

Use this as the default machine-readable result format.

```json
{
  "evaluation_target": "string",
  "judging_context": "clean_subagent | parallel_clean_subagents | same_context_exception",
  "context_contamination_notes": "string",
  "total_score": 0,
  "max_score": 100,
  "grade": "string",
  "global_caps_applied": [
    {
      "rule": "string",
      "reason": "string",
      "score_cap": 0
    }
  ],
  "dimension_scores": [
    {
      "dimension": "string",
      "score": 0,
      "max_score": 0,
      "checklist": [
        {
          "criterion": "string",
          "score": 0,
          "max_score": 0,
          "evidence": "string",
          "comment": "string"
        }
      ],
      "caps_or_penalties": [
        {
          "rule": "string",
          "effect": "string",
          "reason": "string"
        }
      ],
      "summary": "string",
      "improvement": "string"
    }
  ],
  "critical_missing_points": [
    "string"
  ],
  "major_errors": [
    "string"
  ],
  "strengths": [
    "string"
  ],
  "recommended_revisions": [
    "string"
  ],
  "confidence": "low | medium | high",
  "needs_human_review": true
}
```

## Reusable Output Template: Judge Prompt

Use this prompt when asking an LLM to apply a rubric.

```text
You are a strict evaluator applying the provided rubric.

Evaluation principles:
1. Run this evaluation in a clean context; ignore prior conversation, memory, and assumptions not included in the evaluation packet.
2. Use only the supplied rubric, evaluated output, and explicitly supplied evidence bundle.
3. Do not infer missing content or give credit for unstated assumptions.
4. Do not decide the total score first.
5. Score each checklist item before calculating the total.
6. Provide evidence for every checklist score.
7. If the packet lacks evidence needed for a criterion, assign low or zero credit instead of inferring from outside context.
8. Apply local caps and penalties after checklist scoring.
9. Apply global caps after local caps; if multiple global caps apply, use the lowest cap.
10. Do not reward length by itself.
11. Do not reward technical vocabulary by itself.
12. If a claim is unsupported, score the relevant evidence criterion lower.
13. If evaluating one dimension shard in a parallel judging workflow, return only that shard result and do not compute the final total unless instructed.
14. Return only the specified JSON format.

Evaluation target:
{evaluation_target}

Rubric:
{rubric}

JSON output schema:
{json_schema}
```

## Common Dimension Sets

These are starting points only. Adapt them to the task purpose.

Reference notes:

- `references/llm-wiki-quality-rubric-workflow.md` — pattern for converting ad-hoc llm-wiki health checks into a 95-point-baseline rubric with D1–D4 hard gates, deterministic checker boundaries, raw sha256 normalization, and stable JSON scorecards.
- `references/ai-quality-feedback-loops.md` — condensed research notes and templates for helping users build AI/LLM quality feedback loops using evals, failure logs, rubrics, golden sets, pairwise comparison, Reflexion, DSPy, RAGAS, and user feedback.
- `references/real-response-calibration-pattern.md` — workflow for calibrating rubrics against actual isolated/new-session outputs, including artifact layout, high-score gates, and pitfalls from marketing-rubric calibration.
- `references/strictness-loop-calibration.md` — pattern for iterative rubric tightening to a hard target average/version ceiling, using parallel subagent diagnosis, gates/caps, and stop-condition logging.
- `references/holdout-validation-for-strict-rubrics.md` — pattern for checking whether a tightened rubric is overfit: create fresh questions, collect blind/new-session answers, score in parallel with the fixed rubric, aggregate centrally, and document caveats.
- `references/persona-system-prompt-evaluation-scorecard.md` — pattern for evaluating user-persona system prompts: separate reusable rubric from task-specific scorecard, run scenario responses, judge with independent reviewers, include a parseable JSON score block, and verify files/read-back before reporting completion.
- `references/clean-parallel-judge-execution.md` — workflow for running rubric judges in clean new subagents, sharding multi-dimension scoring across parallel judges, aggregating centrally, and enforcing Korean-first human-facing rubric prose.
- `references/skill-quality-rubric-planning-pattern.md` — pattern for designing rubrics that evaluate reusable agent skills/workflow playbooks, including trigger/procedure/boundary/verification dimensions, Korean-first and generic-agent hard rules, structure/ambiguity checks, clean/parallel-subagent judging, parallelization-for-speed criteria, deterministic-vs-nondeterministic automation separation, reusable-script requirements, cap rules, artifact split, and calibration scaffold.


### Literature Survey / Research Review

Recommended dimensions:

- Research coverage.
- Conceptual accuracy.
- Methodology comparison.
- Limitations, bias, and reliability discussion.
- Research flow and synthesis.
- Evidence and citation quality.
- Practical implications.
- Structure and readability.

### LLM-as-a-Judge / Evaluation System Design

Recommended dimensions:

- Evaluation methodology comparison.
- Bias, reliability, and calibration awareness.
- Practical evaluation pipeline design.
- Conceptual accuracy.
- Coverage of relevant studies or benchmarks.
- Evidence quality.
- Output structure.

### Persona/System-Prompt Evaluation Rubrics

When the evaluated artifact is a persona-derived system prompt, the rubric should include both static prompt coverage and scenario response scoring:

- Static dimensions should cover: core judgment model, approval/execution boundaries, verification/completion standards, communication style, security/privacy, code/design preferences, large-analysis/tooling reproducibility, and conflict/excluded-domain handling.
- Scenario scoring should run the prompt against validation scenarios and score each response `0 / 0.5 / 1` before weighted aggregation.
- Use caps for dangerous failures: emulating legal/financial/medical judgment, encouraging unapproved destructive/production/credential/external actions, preferring stale memory over live evidence, allowing unverified completion, or leaking secrets into the prompt.
- Require a scorecard artifact in addition to the rubric: dimension table, scenario group table, global-cap check, final formula, strengths, weaknesses, recommended prompt patches, and a machine-readable JSON result.
- If the user asked for “quality evaluation,” do not stop at scenarios/templates; actually generate prompt-applied responses, run independent judge scoring, add static coverage review, and compute the final score.
- For Hermes default-profile persona work, validate against the active identity source (`~/.hermes/SOUL.md`) directly. Keep canonical prompt source/read-back parity (e.g., hash/size match) and avoid relying only on `config.yaml` for persistent persona identity.
- If the user wants real score certainty, run scenario evaluation in fresh sessions (`hermes chat -Q -q` style calls) and write both `.md` and `.json` result artifacts.

Supporting playbook: `references/hermes-persona-live-evaluation-playbook.md`

### Agent Task Result Evaluation

Recommended dimensions:

- Requirement satisfaction.
- Evidence of execution and verification.
- Correctness and completeness.
- Handling of failures and uncertainty.
- User intent alignment.
- Safety and reversibility.
- Communication clarity.

### Code Implementation Evaluation

Recommended dimensions:

- Requirement satisfaction.
- Correctness.
- Test coverage and verification.
- Maintainability.
- Integration with existing architecture.
- Error handling and edge cases.
- Regression risk.

### PR Review Quality Evaluation

Recommended dimensions:

- Bug/risk detection.
- Technical correctness.
- Actionability of comments.
- Evidence from diff or tests.
- Prioritization by severity.
- Avoidance of noise or nitpicks.
- Respectful and concise communication.

## Common Cap Rules Library

Use or adapt these rules when designing a rubric.

### Global Caps

- If the output is unrelated to the task, total score is capped at 40.
- If the main user request is ignored, total score is capped at 60.
- If a core deliverable is missing, total score is capped at 65.
- If fabricated citations, sources, or tool results are present, total score is capped at 60.
- If multiple critical factual or conceptual errors are present, total score is capped at 70.
- If safety, legal, privacy, or security constraints are violated, total score is capped at 50.
- If the output cannot be evaluated because it lacks substance, total score is capped at 50.
- If a requested reusable rubric document is not written primarily in Korean for human-facing prose, total score is capped at 80.
- If a Korean-first rubric requirement is explicit but the human-facing rubric prose is mostly English, total score is capped at 70.

Machine identifiers such as JSON keys, file paths, commands, API names, enum values, schema fields, and proper nouns may remain in their original language and should not trigger Korean-first language caps.

### Local Caps

- If no sources are provided, Evidence/Citation Quality is capped at 40% of that dimension.
- If methods are listed but not compared, Methodology Comparison is capped at 50% of that dimension.
- If tests or verification are absent, Verification Evidence is capped at 50% of that dimension.
- If the output format is not followed, Structure/Format is capped at 50% of that dimension.
- If the response is overly generic, Analysis Depth is capped at 60% of that dimension.

### Penalty Rules

- Unsupported claims should reduce evidence-related checklist scores.
- Ambiguous wording should reduce structure or clarity scores.
- Missing requested format should reduce structure/format scores.
- Redundant content should reduce concision/readability scores.
- Overconfident claims without uncertainty handling should reduce reliability scores.

## Example: LLM-as-a-Judge Literature Survey Rubric

This example illustrates the preferred checklist-based approach.

### Dimension Summary

| Dimension | Points |
|---|---:|
| Research coverage and scope | 15 |
| Conceptual accuracy | 15 |
| Evaluation methodology comparison | 15 |
| Limitations, bias, and reliability | 15 |
| Research flow and synthesis | 10 |
| Practical applicability | 10 |
| Evidence and citation quality | 10 |
| Structure and readability | 10 |
| **Total** | **100** |

### Limitations, Bias, and Reliability — 15 points

| Checklist Criterion | Points | Recognition Standard |
|---|---:|---|
| Position/order bias explained | 2 | Explains how answer order can affect judge preference |
| Verbosity bias explained | 2 | Explains why longer answers may be favored unfairly |
| Self-preference/model-family bias explained | 2 | Discusses preference toward outputs similar to the judge model |
| Calibration problem explained | 2 | Discusses score scale reliability or consistency |
| Human agreement problem explained | 2 | Discusses agreement or disagreement with human evaluators |
| Reproducibility problem explained | 2 | Discusses variance across prompts, models, runs, or benchmarks |
| Bias mitigation methods proposed | 2 | Gives concrete mitigation such as shuffling, pairwise evaluation, multi-judge, or calibration sets |
| Impact on evaluation outcomes explained | 1 | Explains why these biases matter for final decisions |

Local caps:

- If the answer only says “LLM judges have bias” without naming or explaining specific biases, this dimension is capped at 6/15.
- If no mitigation method is provided, this dimension is capped at 12/15.

## Calibration Guidance

After drafting a rubric, test it with sample outputs.

Use at least:

1. A strong output.
2. A mediocre output.
3. A weak output.
4. A tricky output that is fluent but wrong or unsupported.

Check:

- Does the strong output score high for the right reasons?
- Does the fluent-but-wrong output get penalized?
- Do missing requirements trigger caps?
- Do two evaluators differ by more than 5–8 points?
- Are any checklist items too subjective?

If variance is high, replace vague criteria with observable evidence.

### Reusable rubric vs calibration-results separation

When a rubric is intended for ongoing reuse, keep the stable standard separate from calibration artifacts:

- **Rubric document:** evaluation purpose, target, definition of excellence, weighted checklist criteria, local/global caps, scoring procedure, judge prompt, JSON schema, and score interpretation.
- **Calibration/results document:** sample prompts, sample answers, expected scores, score tables, cap applications, and notes about how the rubric was tuned.

Do not mix sample scores into the canonical rubric unless the user explicitly wants a single all-in-one artifact. Sample scores are result content and will drift as the rubric is revised; keeping them separate prevents future judges from treating old calibration examples as part of the standard.

When storage location is not decided, stage rubric artifacts outside project repositories or skill-managed directories to avoid accidental commits. Use a neutral non-repo artifact directory and report the path. Only write into a repo/wiki/skill directory after the user explicitly chooses that destination.

- Generic advice with no user context.
- Framework-name listing with no application.
- Tactic/channel list with no diagnosis or strategy.
- Fluent but unsupported strategy.
- Subdomain-biased answer that is strong in one area but lacks integrated judgment.
- Competent practitioner answer.
- Strong but incomplete expert answer.
- True expert answer with diagnosis, tradeoffs, measurement, and risks.

Check:

- Does the strong output score high for the right reasons?
- Does the fluent-but-wrong output get penalized?
- Do missing requirements trigger caps?
- Do generic or framework-only answers stay under the intended ceiling?
- Do two evaluators differ by more than 5–8 points?
- Are any checklist items too subjective?

If variance is high, replace vague criteria with observable evidence. If weak examples score too high, strengthen caps before changing weights; caps are the right tool for fatal omissions.

## Common Pitfalls

1. **Only assigning category weights.** A rubric with only weights is not enough. Add checklist criteria.
2. **Using broad range anchors as the main scoring method.** They create scoring variance.
3. **Making every category equally weighted.** This hides the user's priorities.
4. **Confusing importance with fatality.** Important items need points; fatal failures need caps.
5. **Using non-observable criteria.** Replace “good,” “clear,” or “sufficient” with evidence-based criteria.
6. **Letting the judge choose the total score first.** Always score checklist items first.
7. **Not requiring evidence.** Every score should have a reason grounded in the evaluated output.
8. **Ignoring calibration.** Test on examples before using the rubric repeatedly.
9. **Overfitting to one example.** The rubric should generalize across similar tasks.
10. **Rewarding length or jargon.** Length and technical vocabulary are not quality by themselves.

## Verification Checklist

Before finalizing a rubric, verify:

- [ ] The evaluation purpose is explicit.
- [ ] The evaluation target is explicit.
- [ ] The total score is normalized to 100 unless otherwise requested.
- [ ] The highest-weighted dimensions match the user's priorities.
- [ ] Each dimension is broken into checklist criteria.
- [ ] Checklist criteria are observable and separately scorable.
- [ ] The rubric does not rely only on range anchors.
- [ ] Critical failure conditions have cap or penalty rules.
- [ ] The scoring procedure says to score checklist items before total score.
- [ ] The judge prompt requires evidence for each score.
- [ ] The JSON output schema is included when LLM judging is expected.
- [ ] The final scorecard is generated from fresh or explicitly bounded scenario responses (no hand-written placeholders).
- [ ] Judge execution mode is defined: clean subagent, parallel clean subagents, or explicitly labeled same-context exception.
- [ ] Evaluation packet boundaries are defined, including included inputs and excluded context.
- [ ] For multi-dimension or high-stakes rubrics, parallel judging and parent aggregation are specified.
- [ ] Parent aggregation validates shard JSON and applies global caps centrally.
- [ ] Human-facing rubric prose is Korean-first when the request or domain requires Korean-first output.
- [ ] For persona/system-prompt evaluation in Hermes default profile, read-back-check the applied identity source (`~/.hermes/SOUL.md`) against the canonical prompt (hash/size).
- [ ] The canonical persona source is separated from one-off score artifacts (do not overwrite rubric with a specific run result).
- [ ] A calibration loop is defined for repeated use.
