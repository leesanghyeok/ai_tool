# Skill rubric remediation loop

Use this reference when a user asks to improve an agent skill so it passes a skill-quality rubric or reaches a target score.

## Trigger

- A skill package was scored with a checklist rubric and failed a hard gate.
- The user asks to make the skill pass, target a score such as 95+, or remediate rubric findings.
- The target is an editable skill/package, not a protected bundled or hub-installed skill.

## Workflow

1. Treat the rubric scorecard as a remediation map, not as generic advice.
   - List hard-gate blockers first.
   - Identify the smallest edits that remove local/global caps.
   - Prefer patching the target skill and existing references over creating a new narrow skill.

2. Patch the skill at the class-level procedure layer.
   - Put recurring rules in `SKILL.md`.
   - Put detailed runbooks, schemas, examples, source-specific procedures, or session-derived details under `references/`.
   - Avoid one-session narrative additions.

3. Close hard gates before optimizing quality dimensions.
   - Approval/security/privacy gaps often belong in the main `SKILL.md` body.
   - Verification, deterministic checks, reporting templates, and failure labels should be explicit enough to score without inference.

4. Add machine-checkable evidence where the rubric rewards it.
   - Fixed JSON schemas.
   - Parseable shard outputs.
   - Deterministic preflight checks.
   - Read-back or diff verification.

5. For large or multi-dimensional skill evaluation, re-score in clean shards.
   - Split dimensions across clean subagents or equivalent isolated judges.
   - Shard judges should not compute final global score.
   - Parent aggregates scores, applies caps, and reconciles contradictions.

6. Verify edits before claiming success.
   - Read back changed sections.
   - Run syntax/format checks available for the files.
   - Parse JSON code blocks if schemas were added.
   - Re-score against the rubric and report hard-gate status.

## Common high-value remediation patterns

- D3 safety/approval failures:
  - Add low-risk vs approval-required action split.
  - State that plan feedback or partial agreement is not execution approval.
  - Define credential, secret, private URL, raw evidence, and delivery-target boundaries.
  - Require target/account/body/thread policy/public-private scope before external delivery.

- D4 verification failures:
  - Define completion conditions with observable outputs.
  - Require actual artifact/read-back/API/message/test evidence.
  - Treat scheduler/tool `ok` or subagent self-report as insufficient without artifact verification.

- D6 failure handling gaps:
  - Require failed command/API/tool, core error, likely cause, impact, and recovery action.
  - Add retry and alternative-source criteria.
  - Label `completed`, `partial`, `blocked`, `unverified`, `source 부족`, or equivalent states.

- D7 structure gaps:
  - Add fixed final report templates.
  - Resolve apparent contradictions with explicit job-type or scope distinctions.

- D8 parallel/deterministic automation gaps:
  - Add shard criteria for independent work.
  - Keep final ranking, synthesis, caps, and delivery gates centralized.
  - Use reusable collector/checker design instead of one-off scripts.

## Reporting shape

Report:

- files changed
- verification commands/checks and results
- old score vs new score
- hard gate status
- caps still applied, if any
- remaining score-limiting issues
- whether commit/push/external delivery was intentionally not done
