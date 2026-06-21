---
name: pr-review
description: Reuse the requesting-code-review review workflow and post the resulting findings directly to a GitHub PR. Use when the user wants review results on the PR itself, not only in the terminal, especially for requests like "PR에 리뷰 남겨줘", "현재 브랜치 PR에 코멘트 달아줘", or "인라인 리뷰까지 올려줘". Prefer inline PR review comments, fall back to general PR comments when inline placement is not possible, and always add an overall summary comment.
---

# PR Review

Use this skill to turn a self-review into real GitHub PR feedback.

This skill owns:
- finding the target open PR for the current branch
- reusing the existing `requesting-code-review` review flow as the review baseline
- forcing structured review output
- delegating GitHub posting to a separate agent
- posting inline comments first, with general comment fallback
- posting an overall summary comment

This skill does not own:
- fixing the findings
- creating a PR when no PR exists
- guessing inline positions from incomplete review output

## Workflow

1. Verify repository and `gh` auth state.
2. Resolve the target PR from the current branch.
3. If no open PR exists for the current branch, ask the user for a branch name.
4. If the user does not provide a branch name, stop.
5. Resolve PR metadata, including PR number, URL, base branch, and head SHA.
6. Dispatch a review agent that follows the `requesting-code-review` quality bar but returns JSON only.
7. Validate the JSON review payload before posting anything.
8. Dispatch a separate posting agent that uses `gh` to post findings to the PR.
9. Return a concise posting summary to the user with counts and the PR URL.

## PR Resolution

Resolve the current branch first:

```bash
git branch --show-current
gh pr list --head "<branch>" --state open --json number,url,baseRefName,headRefName
```

If the result is empty:
- ask the user for the branch name to inspect
- rerun `gh pr list --head "<user-branch>" --state open ...`
- if still empty, stop and report that no open PR was found

Do not guess the target PR from unrelated open PRs.

After the PR is found, gather the metadata needed for posting:

```bash
gh repo view --json nameWithOwner --jq .nameWithOwner
gh pr view <pr-number> --json number,url,baseRefName,headRefName,headRefOid
```

## Review Agent Contract

Dispatch a dedicated review agent. Do not ask the posting agent to infer review findings from free-form prose.

Tell the review agent to:
- use the current branch diff against the PR base as the review scope
- follow the same review intent as `requesting-code-review`
- focus on bugs, risks, regressions, and missing tests
- return valid JSON only
- avoid markdown fences
- omit findings that are not concrete enough to explain

Use this JSON shape:

```json
{
  "summary": {
    "verdict": "changes_requested",
    "overview": "전반 요약",
    "strengths": [
      "좋았던 점 1",
      "좋았던 점 2"
    ]
  },
  "findings": [
    {
      "severity": "critical",
      "path": "web/src/main/kotlin/org/forhack/Example.kt",
      "line": 123,
      "title": "문제 제목",
      "body": "구체적인 리뷰 내용",
      "suggestion": "가능하면 수정 방향",
      "inline_required": true
    }
  ]
}
```

Validation rules:
- require `summary`
- allow `findings` to be empty
- allow only `critical`, `important`, `minor` severities
- treat a finding as inline-eligible only when `path`, `line`, `title`, and `body` are all present
- reject malformed JSON and ask the review agent to regenerate it before posting

## Posting Agent Contract

Dispatch a second agent whose only job is GitHub posting.

Pass only:
- repository `nameWithOwner`
- PR number and URL
- PR head SHA
- structured review JSON

Do not pass your own interpretation of which findings matter most. Let the posting agent act on the provided payload only.

The posting agent must:
- re-check `gh auth status`
- re-check the PR metadata before posting
- attempt inline comments first for inline-eligible findings
- fall back to general PR comments when inline posting is not possible
- post one overall summary comment after all findings are processed
- report counts for inline success, fallback success, and final failures

## Posting Rules

### Inline comments

Use inline comments only when the finding has complete location data and GitHub accepts the target line.

Preferred API shape:

```bash
gh api repos/<owner>/<repo>/pulls/<pr-number>/comments \
  -X POST \
  -f body='<comment body>' \
  -f commit_id='<head sha>' \
  -f path='<path>' \
  -F line='<line>' \
  -f side='RIGHT'
```

Build the comment body from:
- first line: `[REVIEW_AGENT]`
- severity
- title
- body
- optional suggestion

The marker must be the first line of every automated review comment, and the original content must start on the next line.

### General comment fallback

Use a general PR comment when:
- `path` is missing
- `line` is missing
- inline posting returns a line or diff error
- the finding is intentionally non-inline

Use:

```bash
gh pr comment <pr-number> --body '<comment body>'
```

### Summary comment

Always post one overall summary comment after the findings loop.

Include:
- first line: `[REVIEW_AGENT]`
- verdict
- overview
- strengths
- counts by severity

The marker must be the first line of the summary comment, and the summary body must start on the next line.

Use:

```bash
gh pr comment <pr-number> --body '<summary body>'
```

## Failure Policy

Stop immediately when:
- the directory is not a git repository
- `gh auth status` fails
- no open PR is found for the current branch and the user does not provide a branch
- the review agent cannot produce valid JSON after a retry

Continue with partial success when:
- one inline comment fails and can be posted as a general comment instead
- one general comment fails but other findings can still be posted
- the summary comment fails after findings were already posted

Return the final status in this shape:
- target PR number and URL
- inline comments posted
- fallback general comments posted
- failed comments
- summary comment posted or failed

## Output to User

Keep the final answer concise and operational.

Include:
- PR target
- review verdict
- inline count
- fallback count
- failure count
- notable posting failures if any

If there are no findings, still post the summary comment and say that no concrete review findings were found.
