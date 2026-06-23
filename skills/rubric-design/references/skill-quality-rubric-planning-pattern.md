# Skill Quality Rubric Planning Pattern

Use this reference when designing a rubric for evaluating agent skills, workflow playbooks, or reusable procedural memory.

## Purpose

A skill-quality rubric should evaluate whether a skill actually improves future agent behavior, not whether the document merely sounds polished. Reward operational usefulness: clear trigger, explicit workflow, approval boundaries, verification discipline, failure recovery, reusable structure, low ambiguity, language fit, parallelization judgment, and deterministic automation discipline.

Do not treat any existing skill repository, source family, or local skill collection as a gold standard. External examples such as popular skill repos are calibration samples only; score the explicitness and reliability of their workflow, not their reputation or style.

## Preferred artifact split

For reusable rubrics, create separate artifacts instead of one overloaded document:

```text
rubric/skill/
  skill-quality-rubric-plan.md
  skill-quality-rubric-v1.md
  judge_prompt.md
  score_schema.json
  calibration/
    README.md
  _backup/
    YYYYMMDDTHHMMSSZ/
      ...previous artifacts...
```

Before a major rewrite, back up the current artifacts under `_backup/<UTC timestamp>/`. Keep backups out of the canonical rubric path.

## Preferred canonical rubric format

When the user points to an existing rubric format such as `llm-wiki-quality-rubric-v1.md`, preserve that structure instead of using the generic rubric-design template. For skill-quality rubrics, the preferred shape is:

```text
# Agent Skill 품질 루브릭 v1

## 1. 평가 목적
## 2. 평가 대상
## 3. 통과 기준
## 4. Dimension 요약
## 5. 세부 채점 기준
## 6. Global Caps and Certification Rules
## 7. 점수 해석
## 8. 채점 절차
## 9. Judge Execution Mode
## 10. Judge 지침
## 11. JSON Scorecard Schema
## 12. Calibration Notes
```

Key format traits:

- Use `D1`, `D2`, ... dimension IDs.
- Include a `Gate Type` column in the dimension summary.
- Include a `Deterministic?` column for each checklist table.
- Separate hard-gated dimensions from quality dimensions.
- Include local caps per dimension.
- Include global caps and certification rules after checklist scoring.
- Include an inline JSON scorecard schema matching the standalone `score_schema.json`.

## Recommended dimension set

Use 100 points unless the user requests otherwise:

| ID | Dimension | Points | Gate Type | Focus |
|---|---:|---:|---|---|
| D1 | Trigger & Scope Precision | 15 | Hard gate | When to load the skill and where it stops |
| D2 | Operational Workflow Explicitness | 20 | Hard gate | Explicit executable steps, not implicit workflow |
| D3 | Safety, Approval & Boundary Alignment | 15 | Hard gate | Approval boundaries, risk handling, user operating preferences |
| D4 | Verification & Evidence Discipline | 15 | Hard gate | Real output checks before claiming completion |
| D5 | Reusability, Generality & Language Fit | 10 | Hard gate | Korean-first, generic-agent fit, avoiding product over-binding |
| D6 | Failure Handling & Recovery | 10 | Quality | Error reporting, likely cause, impact, recovery path |
| D7 | Structure, Consistency & Cognitive Load | 8 | Quality | No contradictions or ambiguous decision flow; easy scanning |
| D8 | Parallelization, Context Management & Deterministic Automation | 7 | Quality | Parallel task judgment, context control, deterministic scripting |

Recommended passing model:

- Baseline passing score: `90 / 100`.
- Hard gate thresholds: D1 >= 13, D2 >= 17, D3 >= 13, D4 >= 13, D5 >= 8.
- If any hard gate fails, `pass = false` and certification score is capped at 89, even if the raw total is >= 90.

## Hard rules to consider

When the user's skill library is Korean-first or intended for Korean operators, include language and generality rules explicitly:

- If the skill is not Korean-first, cap the score unless the task explicitly requires another language. Preserve machine identifiers, commands, paths, API names, schema keys, and proper nouns in their original form when useful.
- If the skill unnecessarily depends on a specific product name, agent brand, or local runtime when the workflow should be generic, cap or penalize reusability. Platform-specific skills may name the platform, but should separate general procedure from platform-specific implementation.
- If the core workflow is implicit and the evaluator must infer the procedure, cap the score even if the prose sounds competent.
- If a skill covers large-context work but lacks subagent/parallel-review strategy or fixed intermediate artifacts, cap the score for context-management weakness.
- If deterministic repeated processing is left to agent reasoning rather than scripts/checkers, cap or penalize. Deterministic parsing, counting, normalization, schema validation, bounds checks, and aggregation should be scriptable.
- If each step creates a one-off script instead of a reusable common script/checker, penalize automation design.

## Parallelization and deterministic automation

Subagents and parallelism are valuable for two reasons:

1. Reducing context contamination and keeping shard reasoning clean.
2. Improving speed when tasks are independent and can be processed simultaneously.

A good skill should teach the agent to distinguish:

- Sequential dependency: step B needs step A's output.
- Parallelizable work: independent files, dimensions, logs, samples, or candidate evaluations can run concurrently.
- Deterministic work: parse, count, normalize, hash, validate schema, check bounds, aggregate JSON. Prefer reusable scripts/checkers.
- Nondeterministic work: judgment, synthesis, prioritization, tradeoff assessment. Use clean agent reasoning with bounded evidence packets.

Avoid generating a new ad-hoc script for every tiny step. Prefer one reusable script/checker that handles a class of deterministic subtasks across samples or runs.

## Clean / parallel judging workflow

When a rubric will be applied by an LLM judge:

1. Parent prepares a self-contained evaluation packet: target skill, included files, rubric, deterministic checker output, cap rules, and JSON schema.
2. Judge runs in `clean_subagent` by default.
3. For multi-dimension, long, or high-stakes evaluations, use `parallel_clean_subagents` and shard by dimension/checklist group.
4. Shard judges score only their assigned shard and do not compute the final total.
5. Parent centrally validates JSON, score bounds, missing/duplicate criteria, evidence grounding, contradictions, local caps, and global caps.
6. Use `same_context_exception` only for low-stakes quick checks or when clean subagents are unavailable; record contamination risk.

## JSON scorecard expectations

Use a scorecard shape similar to the llm-wiki rubric style, including:

- `skill_path`
- `evaluated_at`
- `read_only`
- `rubric_version`
- `judging_context`
- `context_contamination_notes`
- `baseline_passing_score`
- `raw_total_score`
- `certification_score`
- `max_score`
- `pass`
- `grade`
- `hard_gates`
- `global_caps_applied`
- `dimension_scores`
- `counts`
- `issues`
- `unverified`
- `next_actions`

## Calibration pattern

Use real skills as samples before freezing the rubric:

1. Strong skills known to improve agent behavior.
2. Average but usable skills.
3. Fluent/long skills with weak execution detail.
4. Skills missing approval or verification boundaries.
5. Skills that are too broad, too narrow, or too session-specific.
6. Skills over-bound to a specific product/agent name when the workflow should be generic.
7. Large-context skills that lack subagent/parallelization or intermediate-artifact strategy.
8. Skills that fail to separate deterministic processing from nondeterministic reasoning.
9. Skills that create per-step one-off scripts instead of common reusable checkers.

Check whether strong skills score high for the right reasons and whether verbose but non-operational skills are capped. If weak examples score too high, adjust caps before changing weights. If judge variance exceeds roughly 5–8 points, split subjective criteria into more observable checklist items. Also check that sample source families do not become implicit gold standards.

## Reporting preference

When the user asks for a plan first, produce a concise plan and wait for approval before writing files. Once approved for non-destructive scoped file creation or rewrite, back up existing artifacts, write the canonical files, and verify with file read-back plus JSON parse validation for schemas.

## origin/main 병합 보강

계획 단계에서 다음 항목을 빠뜨리지 않는다.

- 병렬화 평가는 context hygiene뿐 아니라 독립 shard 병렬 실행으로 wall-clock time을 줄일 수 있는지도 본다.
- 독립 shard는 병렬, 의존 단계는 순차라는 기준을 명시한다.
- Deterministic work는 LLM judgment에 맡기지 않고 reusable script/checker로 처리한다.
- Per-step one-off script 남발은 감점 또는 cap 사유로 둔다.
- Calibration sample에는 병렬화 기회를 놓친 skill과 deterministic/nondeterministic 처리를 혼동한 skill을 포함한다.
