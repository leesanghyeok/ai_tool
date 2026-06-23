# Persona System Prompt Evaluation Scorecard Pattern

Use this reference when the user asks to evaluate a persona/system prompt generated from conversation logs, or asks to "make a rubric and scorecard" for an already-created prompt/evaluation.

## Session-derived pattern

For a persona/system-prompt evaluation, keep these artifacts separate:

1. Canonical system prompt under the final artifact directory.
2. Validation scenarios that test expected behavior.
3. Model responses generated under that system prompt.
4. Rubric document that defines reusable scoring criteria.
5. Scorecard document that applies the rubric to the current prompt and responses.
6. Machine-readable JSON score block inside the scorecard.

Do not collapse the rubric and scorecard into one document unless the user explicitly wants a single all-in-one file. The rubric is reusable; the scorecard is a specific evaluation result.

## Recommended rubric dimensions

For user-persona system prompts, score on 100 points:

- Core judgment model reproduction: live evidence, data-based judgment, verification-first, scope control.
- Approval/execution boundaries: plan feedback vs execution approval, risky changes, non-destructive execution.
- Verification/completion standard: read-back, parse/lint/test, API/UI/channel/scheduler evidence, blocker reporting.
- Communication style: user language, concise structure, uncertainty labels, failure reporting.
- Risk/security/privacy: secret redaction, raw evidence vs prompt separation, external/credential/profile boundaries.
- Code/design judgment: existing structure, minimal reversible changes, YAGNI, tests, request flow, PR thread policy.
- Large-analysis/tooling reproducibility: shard/subagent, fixed schema, evidence index, parent verification of subagent outputs.
- Conflict/exception handling: conditional rules, current explicit instruction vs memory, legal/financial/medical exclusion.

## Scorecard pattern

The scorecard should include:

- Static rubric score by dimension.
- Scenario response score by scenario group.
- Final formula, e.g. `static * 0.4 + scenario * 0.6`.
- Global cap check table.
- Strengths, weaknesses, and recommended prompt patch.
- JSON output block with final score, dimension scores, scenario group scores, recommended edits, confidence, and human-review flag.

## Verification

After writing the rubric and scorecard:

- Verify both files exist/read back.
- If the scorecard contains a JSON block, parse it with a tool before reporting success.
- Report the final score and where the files were saved.

## Common pitfall

Creating only validation scenarios and a template is not enough if the user asked for quality evaluation. Actually apply the prompt to scenarios, judge the responses, write a scorecard, and compute a numeric score with a tool.
