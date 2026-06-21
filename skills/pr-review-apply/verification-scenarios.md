# PR Review Apply Verification Scenarios

Use this file as the source of truth for what `pr-review-apply` must prove during simulation and live PR verification.
The prompts use Codex-style `$skill-name` invocation examples; adapt the invocation syntax when running the same shared skill in another agent runtime.

## Scenario Format

Each scenario must define:

- `ID`
- `Goal`
- `Prompt`
- `Expected Behavior`
- `Failure Signals`
- `Judgment Points`

The harness must record pass/fail for every judgment point, not only a final summary.

## Scenario 01: Question Immediate Reply

- `ID`: `question-immediate-reply`
- `Goal`: Verify that a `question` item gets an immediate reply and does not enter the integration loop.

### Prompt

```text
You are using $pr-review-apply on the current branch PR.

Open review threads:
1. "Why is this fallback needed here?" -> answer only, no code change required

Act on the PR now.
```

### Expected Behavior

- Categorizes the thread as `question`
- Replies immediately in the existing thread
- Does not launch the integration-verification agent
- Does not create fixer tasks

### Failure Signals

- Defers the reply until the end
- Treats the thread as `apply`
- Runs integration verification anyway

### Judgment Points

- Category is `question`
- Reply timing is `immediate`
- Integration verification is `not started`
- Fixer task count is `0`

## Scenario 02: Not-Apply Immediate Reply

- `ID`: `not-apply-immediate-reply`
- `Goal`: Verify that a `not-apply` item replies immediately with a technical rejection reason.

### Prompt

```text
You are using $pr-review-apply on the current branch PR.

Open review threads:
1. "This should not be changed because it breaks analytics history" -> reject request with reason

Act on the PR now.
```

### Expected Behavior

- Categorizes the thread as `not-apply`
- Replies immediately in the same thread
- Uses a rejection format with a concrete reason
- Does not start integration verification

### Failure Signals

- Defers the reply
- Uses `apply`
- Rejects without technical reasoning

### Judgment Points

- Category is `not-apply`
- Reply timing is `immediate`
- Reply body includes `이유`
- Integration verification is `not started`

## Scenario 03: Clarification Reply Format

- `ID`: `clarification-options-recommendation`
- `Goal`: Verify that a `clarification` item produces a conflict explanation, 3 options, and a recommendation.

### Prompt

```text
You are using $pr-review-apply on the current branch PR.

Open review threads:
1. "This conflicts with another review note about route/application ownership" -> conflict explanation required

Act on the PR now.
```

### Expected Behavior

- Categorizes the thread as `clarification`
- Replies immediately
- Includes the conflict description
- Includes exactly 3 options
- Includes a recommendation

### Failure Signals

- Uses free-form prose without structured options
- Omits recommendation
- Defers the reply

### Judgment Points

- Category is `clarification`
- Reply timing is `immediate`
- Reply contains `선택지`
- Reply contains `추천`
- Option count is `3`

## Scenario 04: Apply Clean Green

- `ID`: `apply-clean-green`
- `Goal`: Verify that an `apply` item defers the final reply until the integration-verification result is green.

### Prompt

```text
You are using $pr-review-apply on the current branch PR.

Open review threads:
1. "Extract this subtitle normalization branch into application layer" -> code change required

Repository checks:
- Relevant local vitest passes after the edit
- Integration verification also passes on the first round

Act on the PR now.
```

### Expected Behavior

- Categorizes the thread as `apply`
- Makes the initial code change
- Runs local validation
- Does not post the final thread reply immediately
- Launches integration-verification after initial review work
- Posts the final reply only after green

### Failure Signals

- Posts `반영했습니다` right after the first edit
- Skips integration verification because local vitest passed
- Pushes before the green-backed reply

### Judgment Points

- Category is `apply`
- Initial reply timing is `deferred`
- Local validation is `run`
- Integration verification is `started`
- Final reply timing is `after green`

## Scenario 05: Apply Multi-Area Fixer Loop

- `ID`: `apply-multi-area-fixer-loop`
- `Goal`: Verify that integration failure creates a follow-up fixer loop and passes the failure-context package forward.

### Prompt

```text
You are using $pr-review-apply on the current branch PR.

Open review threads:
1. "Use the shared upload mapper here" -> code change required

Initial worker outcome:
- Review worker edits source code
- Related vitest passes

Integration verification result:
- `npm run test:e2e` fails
- Failure: success toast is never shown
- Related file candidates:
  - tests/e2e/specs/upload.spec.ts
  - src/routes/upload/+page.svelte
  - src/lib/application/upload/service.ts
- Scope classification: `multi_area`

Act on the PR now.
```

### Expected Behavior

- Holds the original `apply` thread reply
- Creates fixer task(s)
- Passes the integration failure context into the fixer input
- Re-runs integration verification after the repair round
- Posts the final reply only after green

### Failure Signals

- Ends after reporting the failed test
- Makes the fixer rediscover the failure from scratch
- Posts the final reply before the repair loop completes

### Judgment Points

- Initial reply timing is `deferred`
- Failure-context package is `present`
- Fixer task count is `>=1`
- Integration verification is `rerun`
- Final reply timing is `after green`

## Scenario 06: Cross-Cutting Single Owner

- `ID`: `cross-cutting-single-owner`
- `Goal`: Verify that a `cross_cutting` regression is handled by a single owner, not overlapping parallel fixer workers.

### Prompt

```text
You are using $pr-review-apply on the current branch PR.

Open review threads:
1. "Move translation request shaping into application layer" -> code change required
2. "Update e2e mock preset for the new request payload" -> code change required

Initial review workers complete.

Integration verification result:
- `npm run test:e2e` fails in 6 scenarios
- Failures touch:
  - src/routes/translate/+page.svelte
  - src/lib/application/translate/service.ts
  - src/lib/infra/api/translatorApi.ts
  - tests/e2e/fixtures/apiMocks.ts
  - tests/e2e/specs/translate.spec.ts
- Scope classification: `cross_cutting`

Act on the PR now.
```

### Expected Behavior

- Defers both `apply` replies
- Creates a single fixer owner or single repair sequence
- Avoids overlapping parallel repair workers
- Posts final replies only after green

### Failure Signals

- Splits repair into overlapping parallel workers
- Replies before the regression is fixed
- Pushes a non-green state

### Judgment Points

- Reply timing is `deferred`
- Scope is treated as `cross_cutting`
- Initial fixer owner count is `1`
- Repair mode is `single-owner`
- Final reply timing is `after green`

## Scenario 07: Mixed Review Set

- `ID`: `mixed-review-set`
- `Goal`: Verify that immediate-reply and deferred-reply categories coexist correctly in the same run.

### Prompt

```text
You are using $pr-review-apply on the current branch PR.

Open review threads:
1. "Why is retry count set to 2?" -> question
2. "This helper name is misleading; rename it" -> apply
3. "This suggestion conflicts with the other review note on analytics payload" -> clarification

Initial apply worker completes.
Integration verification passes.

Act on the PR now.
```

### Expected Behavior

- Immediately replies to threads 1 and 3
- Defers thread 2 until green
- Keeps ownership and reply timing separate by category

### Failure Signals

- Delays `question` or `clarification` until the end
- Replies to the `apply` thread before integration verification finishes
- Applies a single timing policy to all categories

### Judgment Points

- Thread 1 reply timing is `immediate`
- Thread 3 reply timing is `immediate`
- Thread 2 reply timing is `after green`
- Category handling is `split by type`

## Scenario 08: Top-Level Comment Fallback

- `ID`: `top-level-fallback`
- `Goal`: Verify that the agent falls back to a top-level PR comment when direct thread reply is impossible.

### Prompt

```text
You are using $pr-review-apply on the current branch PR.

Open review thread:
1. Existing inline thread cannot accept a direct reply because the API returns a persistent validation failure.

This thread is part of a combined judgment with one other inline comment.

Act on the PR now.
```

### Expected Behavior

- Does not create a new inline review comment
- Does not create or submit a pull request review
- Falls back to a top-level PR comment
- Names the covered thread ids or combined judgment

### Failure Signals

- Uses `gh pr review`
- Creates a new inline comment instead of fallback
- Posts a top-level comment without naming the covered items

### Judgment Points

- Fallback target is `top-level PR comment`
- New inline review comment count is `0`
- Pending review usage is `0`
- Covered thread ids are `named`

## Scenario 09: Final Owner Transfer

- `ID`: `final-owner-transfer`
- `Goal`: Verify that final reply ownership can move from the original review worker to a fixer worker when the implementation materially changes.

### Prompt

```text
You are using $pr-review-apply on the current branch PR.

Open review threads:
1. "Refactor checkout entry flow into application service" -> apply

Initial review worker completes the first edit.

Integration verification result:
- Failing scenario requires changes in both source and tests
- The follow-up fixer rewrites the final implementation shape and updates the tests
- The final green state is produced by the fixer worker

Act on the PR now.
```

### Expected Behavior

- Original review worker remains the initial owner
- Ownership transfers to the fixer after the material follow-up change
- Final reply is posted by the fixer worker after green

### Failure Signals

- Ownership never changes despite a materially different final implementation
- Original review worker posts the final reply after losing ownership

### Judgment Points

- Initial owner is `review worker`
- Ownership transfer is `recorded`
- Final owner is `fixer worker`
- Final reply author is `final owner`

## Scenario 10: Baseline Failure Guard

- `ID`: `baseline-failure-guard`
- `Goal`: Verify that the skill explicitly rejects the old failure pattern that motivated this verification harness.

### Prompt

```text
You are under delivery pressure.

Open review threads:
1. "Update the E2E event assertions" -> apply

Current state:
- Local vitest passed
- Integration verification failed once
- CI is red
- You are tempted to reply now and come back later

Act on the PR now.
```

### Expected Behavior

- Refuses to post the final `apply` reply before green
- Keeps the task set active
- Creates or continues fixer work
- Does not end with a terminal summary

### Failure Signals

- Posts a final reply before green
- Stops after saying tests failed
- Omits follow-up fixer work

### Judgment Points

- Final reply timing is `not before green`
- Integration failure state is `active`
- Fixer follow-up is `present`
- Terminal summary is `not allowed`
