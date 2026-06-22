# Feedback Default Wiki Routing Pitfall

## Context

A feedback logging run occurred while the runtime had project wiki routing set:

```text
WIKI_PATHS=marketing=/Users/stark/Documents/marketing-wiki
WIKI_DEFAULT=marketing
```

The feedback logs were initially written under the marketing wiki:

```text
/Users/stark/Documents/marketing-wiki/raw/feedback/...
```

The user clarified that feedback logs should live in the general feedback wiki root:

```text
/Users/stark/wiki/raw/feedback
```

## Durable lesson

`WIKI_PATHS` and `WIKI_DEFAULT` can route normal wiki tasks to a domain/project wiki. Feedback incident logs are cross-project quality data and should not silently follow a domain wiki default.

Default routing for this skill should be:

1. Use an explicit user-provided feedback wiki path if provided.
2. Else use `FEEDBACK_WIKI_PATH` if set.
3. Else use `WIKI_PATH` if it is explicitly set for feedback/general wiki use.
4. Else use `$HOME/wiki`.
5. Do not use `WIKI_PATHS`/`WIKI_DEFAULT` as the feedback default unless the user explicitly names that wiki as the feedback destination.

## Recovery pattern

If logs were written to the wrong domain wiki:

1. Identify the created files under `<domain-wiki>/raw/feedback/YYYY-MM-DD/`.
2. Move each incident file to `$HOME/wiki/raw/feedback/YYYY-MM-DD/` without modifying body content.
3. Preserve filenames and frontmatter unless `session_id` was genuinely wrong.
4. Recompute/check body-only `sha256` after the move.
5. Remove the now-empty wrong feedback directory if safe.
6. Report both old and new paths.

## Verification checklist

- [ ] Destination is `$HOME/wiki/raw/feedback` or an explicitly requested feedback wiki.
- [ ] No residual feedback files remain in the mistaken domain wiki path.
- [ ] Each moved file still has a valid body-only `sha256`.
- [ ] The final report names the actual destination paths.
