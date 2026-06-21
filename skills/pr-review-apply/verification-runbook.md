# PR Review Apply Verification Runbook

Use this runbook to verify that `pr-review-apply` behaves correctly in both simulation and the live PR flow.

## Verification Targets

- Skill under test: `skills/pr-review-apply/SKILL.md`
- Scenario source: `skills/pr-review-apply/verification-scenarios.md`
- Live PR target: `leesanghyeok/subtitle_translator_web#14`

## Evidence Rules

Every verification run must record:

- execution time
- scenario id or PR thread id
- prompt or target thread summary
- category decision
- reply timing decision
- whether integration-verification started
- integration result
- failure-context package summary
- fixer task creation
- owner transfer, if any
- final reply timing
- raw output or raw command evidence
- final pass/fail

Use the template at the end of this file. Do not rely on memory.

## Simulation Harness

### Output Contract

Each simulation prompt must ask for the same fields:

1. category per review item
2. immediate vs deferred reply
3. whether integration-verification starts
4. whether fixer tasks are created
5. whether ownership changes
6. when the final reply is posted
7. short justification tied to the skill

### Pass/Fail Rule

A scenario passes only if every judgment point in `verification-scenarios.md` passes.

### Required Simulation Sweep

Run at least these scenarios:

- `question-immediate-reply`
- `not-apply-immediate-reply`
- `clarification-options-recommendation`
- `apply-clean-green`
- `apply-multi-area-fixer-loop`
- `cross-cutting-single-owner`
- `mixed-review-set`
- `top-level-fallback`
- `final-owner-transfer`
- `baseline-failure-guard`

### Pressure Variants

Add at least one pressure variant for the following temptations:

- reply now and fix later
- stop after the first integration failure
- parallelize a `cross_cutting` repair

### Meta-Test

If a simulation fails, ask a follow-up:

```text
You read the skill but still chose the wrong action.
Which exact rule felt ambiguous or easy to rationalize away?
What wording would have made the correct action unavoidable?
```

Use the answer only to tighten the skill or scenario if a real loophole exists.

## Live PR Verification For PR #14

### Preconditions

- `gh auth status` succeeds
- current repo is `~/WebstormProjects/subtitle_translator_frontend_refactor`
- target PR is still open: `gh pr view 14 --repo leesanghyeok/subtitle_translator_web`

### Current PR Facts To Recheck Before Every Live Run

Collect fresh state before running the skill:

```bash
gh pr view 14 --repo leesanghyeok/subtitle_translator_web --json number,title,headRefName,baseRefName,reviewDecision,isDraft,comments,reviews
gh api graphql -f query='query { repository(owner: "leesanghyeok", name: "subtitle_translator_web") { pullRequest(number: 14) { reviewThreads(first: 100) { nodes { id isResolved isOutdated comments(first: 20) { nodes { id body author { login } url createdAt replyTo { id } } } } } } } }'
```

Do not use stale thread state from a previous run.

### Seeded Verification Review Set

The PR now has an explicit verification review set. Reconfirm these comments still exist before every live run.

- `question`
  - comment id: `3028564881`
  - url: `https://github.com/leesanghyeok/subtitle_translator_web/pull/14#discussion_r3028564881`
  - marker: `[VERIFY_SET][question]`
  - expected behavior: immediate direct reply, no integration loop
- `not-apply`
  - comment id: `3028564878`
  - url: `https://github.com/leesanghyeok/subtitle_translator_web/pull/14#discussion_r3028564878`
  - marker: `[VERIFY_SET][not-apply]`
  - expected behavior: immediate direct reply with `이유`
- `clarification`
  - comment id: `3028564874`
  - url: `https://github.com/leesanghyeok/subtitle_translator_web/pull/14#discussion_r3028564874`
  - marker: `[VERIFY_SET][clarification]`
  - expected behavior: immediate direct reply with conflict, 3 options, and recommendation
- `apply-green`
  - comment id: `3028568820`
  - url: `https://github.com/leesanghyeok/subtitle_translator_web/pull/14#discussion_r3028568820`
  - marker: `[VERIFY_SET][apply-green]`
  - expected behavior: code change, local validation, integration verification, final reply only after green
- `apply-repair`
  - comment id: `3028568823`
  - url: `https://github.com/leesanghyeok/subtitle_translator_web/pull/14#discussion_r3028568823`
  - marker: `[VERIFY_SET][apply-repair]`
  - expected behavior: code change spanning multiple test files, integration loop if needed, final reply only after green
- `cross-cutting`
  - comment id: `3028568832`
  - url: `https://github.com/leesanghyeok/subtitle_translator_web/pull/14#discussion_r3028568832`
  - marker: `[VERIFY_SET][cross-cutting]`
  - expected behavior: related multi-file test cleanup with single-owner repair if integration verification reveals overlapping impact
- `top-level fallback`
  - existing evidence comment: `4174326433`
  - url: `https://github.com/leesanghyeok/subtitle_translator_web/pull/14#issuecomment-4174326433`
  - expected behavior: if direct reply is impossible, use top-level PR comment and name the covered thread ids or combined judgment

### Live Categories Present In PR #14

At the time this runbook was written, PR `#14` already showed examples of:

- direct inline replies already posted on resolved threads
- `question` style follow-ups in thread `PRRT_kwDOPPH0TM54ZgYu`
- top-level fallback behavior documented in PR comment `4174326433`
- a complaint about leaving a failed build/test state in thread `PRRT_kwDOPPH0TM54ZgYu`

Reconfirm the exact live set before every run. Do not assume these thread ids remain actionable.

### Live Verification Checklist

For every active thread in PR `#14`, verify:

1. Which category applies:
   - `question`
   - `clarification`
   - `not-apply`
   - `apply`
2. Whether the thread should reply immediately or defer
3. Whether the thread can accept direct reply
4. Whether fallback must be top-level PR comment
5. Whether the current state requires integration verification
6. Whether failure-context package must be created
7. Whether ownership should stay with the original review worker or move to a fixer

### Live Assertions

The live run must confirm the following when the corresponding case exists:

- non-apply items reply immediately
- `apply` items do not post the final reply before green
- integration failure keeps the run active
- fixer tasks are created after integration failure
- failure-context package is passed forward with enough detail
- `cross_cutting` failures use a single owner
- final reply is posted by the current owner after green
- direct reply failure uses top-level PR comment fallback
- no `gh pr review` command or pending-review flow is used

### Forbidden Behavior Checks

Explicitly inspect for:

- `gh pr review`
- `repos/{owner}/{repo}/pulls/{pull_number}/reviews`
- pending review creation
- final `apply` reply before green
- terminal summary after integration failure

## Acceptance Gate

The harness is ready only when:

- all 10 simulation scenarios have prompts and judgment points
- at least one successful simulation run exists for each major branch:
  - immediate reply
  - deferred apply reply
  - fixer loop
  - top-level fallback
  - owner transfer
  - cross-cutting single owner
- the live PR `#14` checklist is executable without inventing missing decisions
- evidence can be captured with the template below

The skill is validated only when:

- simulation sweep passes
- live PR run passes
- any loopholes found are patched in `SKILL.md`
- affected scenarios are rerun after the patch

## Evidence Template

```text
Verification Run:
- Time:
- Target:
- Scenario ID / Thread ID:
- Prompt / Thread Summary:

Observed Decisions:
- Category:
- Reply Timing:
- Integration Verification Started:
- Integration Result:
- Failure Context:
- Fixer Created:
- Owner Transfer:
- Final Reply Timing:

Raw Evidence:
- Command Output / Agent Output:

Result:
- Pass / Fail:
- Notes:
```
