---
name: pr-review-apply
description: Use when applying GitHub PR review feedback to the current branch's open PR, or when the PR number must be resolved before starting review resolution work.
---

# PR Review Apply

Use this skill when turning review feedback into code changes and PR replies.

## Operating Rules

- Resolve the target PR from the current branch first.
- If no open PR exists for the current branch, ask for the PR number.
- Reconstruct state on every run by re-reading GitHub open threads, existing replies, and review history.
- Use `gh` / `gh api` first for PR discovery and review-state collection.
- Use a GitHub collection agent for PR threads, review context, and reply capture.
- Do not use local state files.
- A human-submitted pull request review event may trigger this skill. Treat that event as input only.
- This skill is for existing review feedback only. It replies to existing review threads and does not create new inline review comments.
- Never create, extend, or submit the agent's own pull request review.
- Never use `gh pr review` for this skill.
- Never call pull-request review creation or submission endpoints such as `repos/{owner}/{repo}/pulls/{pull_number}/reviews`.
- Existing review-thread replies must be posted immediately as standalone comments, not staged in a pending review.
- Do not create or extend a pending review when replying to an existing review thread.
- Do not use review-draft flows such as `pulls/{pull_number}/reviews` for review-thread replies.
- Use the GitHub review-comment reply path for existing thread replies so the reply is published immediately without creating a pull request review.
- Never resolve review threads by default.
- Keep review threads visible so the user can inspect the original comment and the reply in GitHub.
- Resolve a review thread only when the user explicitly asks for resolution.
- Use a top-level PR comment only when an existing inline thread cannot accept a direct reply or when one combined judgment intentionally covers multiple inline comments.
- Allowed outbound comment paths are limited to:
  - direct replies to existing review comments
  - top-level PR comments when direct thread reply is impossible or intentionally bundled
- Top-level comments are also allowed when one combined judgment intentionally covers multiple inline comments.
- When a top-level comment is used, name the inline reviews or combined judgment it covers.
- Default execution is collision-free parallel dispatch for initial review workers, followed by a dedicated integration-verification agent.
- The main agent orchestrates only. It does not run integration verification itself.
- After all initial review workers finish, the main agent must launch a dedicated integration-verification agent.
- The integration-verification agent must run the integration-level tests required for the repository state after review application.
- The integration-verification agent must include repo-local required validation in the verification set.
- The integration-verification agent must report failure facts and a reusable failure-context package for each failing item.
- The integration-verification agent does not decide the code change. It provides failure evidence and context for follow-up fixer workers.
- If integration verification fails, the run is not complete. The main agent must create follow-up fixer tasks and continue the loop.
- The main agent must repeat fixer dispatch and integration verification until the repository reaches green.
- The repository is green only when integration verification is green and repo-local required validation has passed.
- Review-thread reply ownership depends on the review category:
  - `question`, `clarification`, `not-apply`, `proposal-required`: the review worker replies immediately.
  - `approved-apply`: the final current owner replies only after the final green state is reached.
- Code-changing review items default to `proposal-required` on first pass.
- `proposal-required` means inspect first, reply with execution options and a recommended implementation plan, and wait for the user's explicit implementation command.
- Do not edit code, run implementation validation, commit, or push while an item is still `proposal-required`.
- Transition an item from `proposal-required` to `approved-apply` only after the user explicitly instructs implementation.

## Task Split

- Default to individual handling.
- Bundle only small reviews when per-thread explanation quality is preserved.
- Split review items into grouped tasks when they share one code path or one fix.
- Split them into individual tasks when they touch different files, behaviors, or risk areas.
- Use these response categories for each item: `proposal-required`, `approved-apply`, `not-apply`, `question`, `clarification`.
- `proposal-required` means the review needs a code change, but implementation is blocked until the user explicitly approves a proposed direction.
- `approved-apply` means the user has explicitly instructed implementation and the change should be applied.
- `not-apply` means reject the request with a reason.
- `question` means answer with a direct clarification.
- `clarification` means the item conflicts with code, tests, or another review note.
- Initial review comments are handled by review workers.
- Code-changing review comments begin as `proposal-required` unless the user message that triggered the run already includes explicit implementation approval.
- Integration failures discovered after `approved-apply` implementation are handled as separate fixer tasks.
- Fixer tasks are grouped by failure scope:
  - `localized`
  - `multi_area`
  - `cross_cutting`
- `localized` failures may be fixed in parallel when write scopes do not collide.
- `multi_area` failures may be fixed in parallel only when the affected areas are clearly disjoint.
- `cross_cutting` failures require a single owner and must not run concurrently with overlapping write tasks.

## Collision Rules

- Check collisions in order: file path, then line or hunk range, then semantic conflict.
- If two tasks touch the same file path, merge or serialize them before any write.
- If they touch overlapping line or hunk ranges, merge or serialize them before any write.
- If they still conflict semantically, escalate to a single owner for the explanation.
- If a task depends on another task's output, do not start it early.
- If a review thread conflicts with another thread, one worker must own the conflict and post the explanation.
- Clarification replies must include the conflict description, 3 options, and a recommendation.

## Failure Context Package

- For each failing integration item, the integration-verification agent must provide:
  - executed command
  - failing test identifier or scenario name
  - phase such as `vitest`, `integration`, or `e2e`
  - primary error message
  - relevant raw excerpt such as stack trace, locator failure, or assertion excerpt
  - related file candidates
  - scope classification: `localized`, `multi_area`, or `cross_cutting`
- The failure-context package must be detailed enough for a fixer worker to begin repair work without reconstructing the failing scenario from scratch.
- The failure-context package must be passed to the follow-up fixer worker with minimal loss of raw error detail.

## Worker Contract

- Each review worker handles one assigned review task end to end.
- A review worker may inspect code and prepare reply content for any category.
- If a review changes the implementation contract, product behavior, event semantics, API expectation, or other documented spec-level decision, the responsible worker must update the relevant spec or design document in the same run.
- Spec updates are part of the same review-application task, not optional follow-up cleanup.
- When multiple overlapping spec documents exist, prefer updating the latest source-of-truth spec and remove or consolidate stale duplicates when that can be done safely.
- Do not leave repo docs in a state where the merged code and the latest spec disagree on the applied review outcome.
- A review worker handling `question`, `clarification`, `not-apply`, or `proposal-required` must post the thread reply immediately.
- A `proposal-required` review worker must not edit code, update specs, run implementation validation, commit, or push.
- A `proposal-required` review worker must reply with:
  - the current understanding of the request
  - impact scope
  - 2-3 implementation options when meaningful
  - a recommendation
  - the specific implementation plan it would apply after approval
  - a statement that execution waits for the user's explicit instruction
- A review worker handling `approved-apply` may edit code, update required specs, run local validation, and prepare final reply content.
- A review worker handling `approved-apply` must not post the final thread reply immediately after the first edit.
- An `approved-apply` review worker returns its result and relevant context to the main agent for the integration-verification loop.
- Each fixer worker handles one integration-failure task end to end.
- A fixer worker receives:
  - the failure-context package from the integration-verification agent
  - related prior review context when relevant
  - repository-local skills based on touched file type
- A fixer worker determines how to repair the failure from the supplied failure context and repository state.
- The main agent tracks the current owner for each `approved-apply` review item.
- The initial current owner of an `approved-apply` item is the original review worker that executed the approved change.
- If follow-up repair work materially changes the final implementation, the main agent may transfer current ownership to the responsible fixer worker.
- The final current owner of an `approved-apply` item posts the thread reply only after the repository reaches green.
- Each worker commits its own task with a Korean commit message.
- Commit steps are serialized by the main agent, one slot at a time.

## Repo-Local Skills

- If a repository has local editing-rule skills, workers must load them with the same source/test split pattern.
- Any source-code edit requires the repo's layer- or source-structure skill.
- Any test edit requires the repo's test-writing skill.
- Any spec, design, or plan document edit required by a review must follow the repo's local documentation conventions when such conventions exist.
- If both source and tests are edited, use both skills.
- Follow those skills before editing anything in those areas.

## Reply Rules

- For an existing review thread, post a direct reply. Do not create a new review comment, and do not convert the reply into a pending review.
- If a reply cannot be posted into an existing thread, fall back to a top-level PR comment. Do not submit a new pull request review as a fallback.
- Do not hide a review by resolving it after replying unless the user explicitly requested that action.
- If no existing thread reply is possible, use a top-level PR comment instead of creating a new inline review comment.
- "Publish immediately" means posting a visible reply or PR comment without any pending-review or submitted-review flow owned by the agent.
- Reply immediately in the same existing review thread for `question`, `clarification`, `not-apply`, and `proposal-required` items.
- Do not post the final thread reply immediately for `approved-apply` items.
- For an `approved-apply` item, the final thread reply must be posted only after the repository reaches green through the integration-verification loop.
- The final reply for an `approved-apply` item must be posted by the current owner of that item.
- If ownership changes during follow-up repair work, the final reply responsibility moves to the new current owner.
- Before the final green state, do not use wording that implies the `approved-apply` item is fully completed.
- If an intermediate status message is absolutely necessary, it must distinguish between:
  - review comment application status
  - integration verification status
- Prefer a single final reply for each `approved-apply` item after the final green state.
- The first line of every automated review-thread reply must be `[REVIEW_AGENT]`.
- The first line of every automated top-level PR comment must be `[REVIEW_AGENT]`.
- Insert one blank line after `[REVIEW_AGENT]` before the body.
- Keep replies short, technical, and free of emotional agreement or gratitude.
- Default to itemized formatting for readability.
- Split different kinds of information across lines instead of compressing them into one sentence.
- Use short bullet lists when describing multiple changes, checks, or reasons.
- Use short paragraphs only for background, rationale, or constraint explanation that does not fit cleanly into bullets.
- If the reply includes `수정 방향 제안`, `반영 예정안`, `진행 조건`, `반영 내용`, `이유`, `검증`, `질문 답변`, or `추천`, place each section on its own line or block.
- `proposal-required` replies must include the current understanding, impact scope, options, recommendation, implementation plan, and the explicit-approval gate.
- `approved-apply` replies should say what changed, how far it was applied, and verification when relevant, but only after the final green state is reached.
- `not-apply` replies should say why the request was rejected.
- `question` replies should give a direct answer, state implementation intent, and include relevant history or constraints.
- `clarification` replies should include the conflict, 3 options, and a recommendation in the same reply.

Reply format examples:

```text
[REVIEW_AGENT]

수정 방향 제안:
- 현재 이해한 요청: <리뷰 의도 요약>
- 영향 범위: <파일/동작/테스트 범위>

선택지:
1. <옵션 A>
2. <옵션 B>
3. <옵션 C>

추천:
- <권장안과 이유>

반영 예정안:
- <승인되면 적용할 변경 1>
- <승인되면 적용할 변경 2>

진행 조건:
- 명시적으로 반영 요청을 주시면 그때 코드 수정과 검증을 진행합니다.
```

```text
[REVIEW_AGENT]

반영했습니다.
- <변경 1>
- <변경 2>

검증:
- <실행한 체크 1>
- <실행한 체크 2>
```

```text
[REVIEW_AGENT]

이번 항목은 비적용으로 유지했습니다.

이유:
- <기술적 근거 1>
- <기술적 근거 2>
```

```text
[REVIEW_AGENT]

질문 답변:
- <직접 답변>

구현 의도:
<계획 또는 제약 설명>
```

```text
[REVIEW_AGENT]

현재 다른 리뷰 항목과 충돌합니다.

선택지:
1. <옵션 A>
2. <옵션 B>
3. <옵션 C>

추천:
- <권장안>
```

## Commit and Push

- Serialize commit slots in the main agent.
- Each worker commits only its assigned task.
- Do not create implementation commits for `proposal-required` items.
- Do not push after the initial review-worker phase if integration verification is still failing.
- Fixer commits are serialized by the main agent between verification rounds.
- Before the single final push, the main agent re-checks remaining open reviews and local branch state.
- After all completed tasks finish, push once.
- Do not push per worker.

## Failure Handling

- If commit succeeds but reply fails, the task is not complete.
- Retry the reply or report it for the next run.
- A `proposal-required` item that has been replied to and is waiting for explicit approval is in a waiting state, not a failure state.
- If integration verification fails, the task set remains active.
- Integration verification failure is not a terminal outcome. It must create follow-up fixer tasks.
- After each repair round, the main agent must rerun the integration-verification agent.
- The run completes only when:
  - required immediate replies for `question`, `clarification`, `not-apply`, and `proposal-required` items are posted
  - no `proposal-required` item is implemented before explicit approval
  - no required fixer task remains open
  - the final integration-verification result is green for all `approved-apply` items
  - repo-local required validation has passed for all `approved-apply` items
  - final replies for `approved-apply` items are posted by their current owners
  - the final green state is pushed once for completed `approved-apply` work
- If a thread was resolved accidentally, unresolve it before completion unless the user explicitly asked to keep it resolved.
