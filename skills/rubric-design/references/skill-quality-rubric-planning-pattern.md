# Skill Quality Rubric Planning Pattern

Use this reference when designing a rubric for evaluating agent skills, workflow playbooks, or reusable procedural memory.

## Purpose

A skill-quality rubric should evaluate whether a skill actually improves future agent behavior, not whether the document merely sounds polished. Reward operational usefulness: clear trigger, executable procedure, approval boundaries, verification discipline, failure recovery, reusable structure, low ambiguity, and context-management discipline.

Do not treat any existing skill repository, source family, or local skill collection as a gold standard. External examples such as popular skill repos are calibration samples only; score the explicitness and reliability of their workflow, not their reputation or style.

## Recommended artifact split

For reusable rubrics, create separate artifacts instead of one overloaded document:

```text
rubric/skill/
  skill-quality-rubric-plan.md
  skill-quality-rubric-v1.md
  judge_prompt.md
  score_schema.json
  calibration/
    README.md
```

- `*-plan.md`: purpose, target, proposed dimensions, cap strategy, calibration plan.
- `*-rubric-v1.md`: canonical human-readable scoring standard.
- `judge_prompt.md`: strict LLM-as-judge instructions that reference the canonical rubric.
- `score_schema.json`: parseable output schema for scorecards.
- `calibration/README.md`: sample selection, scorecard storage, and tuning rules.

## Dimension set for skill quality rubrics

Use 100 points unless the user requests otherwise:

| Dimension | Points | Focus |
|---|---:|---|
| Trigger & Scope Precision | 15 | When to load the skill and where it stops |
| Operational Procedure Quality | 20 | Whether the skill provides executable steps |
| User Preference / Boundary Alignment | 15 | Approval boundaries, style, and user-specific operating preferences |
| Verification & Evidence Discipline | 15 | Real output checks before claiming completion |
| Failure Handling & Recovery | 10 | Error reporting, likely cause, impact, and recovery path |
| Reusability & Portability | 10 | Stable reusable procedure vs one-off session narrative |
| Structure, Consistency, and Cognitive Load | 8 | No contradictions or ambiguous decision flow; easy scanning for the agent |
| Parallelization, Context Management & Deterministic Automation | 7 | Identify concurrently processable work for speed, isolate large-context shards, separate deterministic automation from nondeterministic reasoning, and use reusable scripts/artifacts instead of per-step one-off scripts |

## Hard rules to consider for user-facing skill rubrics

When the user's skill library is Korean-first or intended for Korean operators, include language and generality rules explicitly:

- If the skill is not Korean-first, cap the score unless the task explicitly requires another language. Preserve machine identifiers, commands, paths, API names, schema keys, and proper nouns in their original form when useful.
- If the skill unnecessarily depends on a specific product name, agent brand, or local runtime when the workflow should be generic, cap or penalize reusability. Platform-specific skills may name the platform, but should separate general procedure from platform-specific implementation.
- If the core workflow is implicit and the evaluator must infer the procedure, cap the score even if the prose sounds competent.
- If a skill covers large-context work but lacks subagent/parallel-review strategy or fixed intermediate artifacts, cap the score for context-management weakness. Parallelization should not be framed only as context hygiene: reward skills that identify independent tasks that can run concurrently to improve wall-clock speed.
- If a skill sends deterministic work (parsing, aggregation, normalization, schema validation, score-bounds checks, duplicate/missing-criteria checks) to agent reasoning instead of reusable scripts, cap or penalize automation quality.
- If a skill creates a separate one-off script for every workflow step instead of extracting a reusable script shared across samples/runs, penalize maintainability and reusability.

## Cap rules that matter for skills

Apply checklist scoring first, then caps. Use the lowest applicable global cap.

- If the skill has no executable procedure and is only conceptual prose, cap total at 60.
- If it covers destructive, external, credential, production, or persistent-state changes without approval boundaries, cap total at 55.
- If the rubric evaluates large or multi-part workflows, parallelization criteria should check both context isolation and speed: independent shards should run concurrently, while dependency-ordered steps remain sequential.
- If deterministic repeatable work is left to LLM judgment instead of scripts or deterministic validators, cap total at 75.
- If the workflow encourages per-step one-off scripts rather than reusable common scripts for repeated parsing/aggregation/validation, cap total at 80.
- If it has no verification discipline, cap total at 70.
- If it permits fabricated output, unverified completion, or pretending tools ran, cap total at 50.
- If it conflicts with stable user/project conventions, cap total at 65.
- If the trigger is so broad that the skill would load for nearly everything, cap total at 75.
- If the body is a one-off incident log rather than reusable procedural knowledge, cap total at 70.
- If it encourages security or privacy risk, cap total at 50.

## Calibration pattern

Use real skills as samples before freezing the rubric:

1. Strong skills that are known to improve agent behavior.
2. Average but usable skills.
3. Fluent/long skills with weak execution detail.
4. Skills missing approval or verification boundaries.
5. Skills that are too broad, too narrow, or too session-specific.

6. Skills that are over-bound to a specific product/agent name when the workflow should be generic.
7. Large-context skills that lack subagent/parallelization or intermediate-artifact strategy.
8. Skills that miss parallelization opportunities by forcing independent subtasks into a purely sequential flow.
9. Skills that fail to separate deterministic automation from nondeterministic reasoning.
10. Skills that create per-step one-off scripts instead of reusable common scripts for repeated parsing, aggregation, normalization, or validation.

Check whether strong skills score high for the right reasons and whether verbose but non-operational skills are capped. If weak examples score too high, adjust caps before changing weights. If judge variance exceeds roughly 5–8 points, split subjective criteria into more observable checklist items. Also check that sample source families do not become implicit gold standards: the rubric should reward explicit, reusable workflow quality rather than repository reputation. For LLM-judge workflows, prefer clean or parallel clean subagents and parent-side deterministic aggregation/validation.

## Reporting preference

When the user asks for a plan first, produce a concise plan and wait for approval before writing files. Once approved for non-destructive scoped file creation, write the artifacts and verify with file read-back plus JSON parse validation for schemas.
