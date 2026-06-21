# Session-finalize feedback autolog pattern

Use this when the user wants feedback-ai-logging to run automatically at the end of Hermes sessions.

## Recommended integration

Prefer a Hermes user plugin lifecycle hook over a gateway-only hook or direct Markdown writing:

1. Register a user plugin hook on `on_session_finalize`.
2. In the hook, do not analyze the transcript or write `raw/feedback/` files directly.
3. Spawn a separate Hermes one-shot with this skill preloaded:

```bash
HERMES_FEEDBACK_AUTOLOG_CHILD=1 \
hermes --resume "$SESSION_ID" --skills feedback-ai-logging chat --source feedback-autolog -q "Use feedback-ai-logging to harvest the resumed session. Follow the skill rules; create one raw/feedback Markdown file per incident; skip duplicates and non-failures."
```

The plugin is only the trigger. The feedback-ai-logging skill remains the single implementation of incident detection, idempotency, frontmatter, body sections, and sha256 calculation.

## Why this is safer than direct file writes

- A Python hook cannot “call” a skill as a function; direct writing would duplicate the skill's LLM-guided judgment and formatting logic.
- The child Hermes process can resume the target session and apply the current skill instructions.
- Hook failures stay isolated from the gateway/CLI session-finalization path.
- Updating this skill later improves the autologger without rewriting hook code.

## Hook choice

Use `on_session_finalize` for Hermes session lifecycle finalization. It is broader than gateway-only `session:end` and covers CLI/gateway session boundaries such as shutdown, `/new`, `/reset`, and gateway idle/daily expiry.

Do not imply that `on_session_finalize` means “Discord thread closed.” Discord thread lifecycle and Hermes session lifecycle are separate:

- Discord thread archive/close/delete is a platform object event.
- Hermes session finalize is an internal conversation lifecycle event.
- A Discord thread conversation can be finalized later by idle expiry, daily reset, `/new`, `/reset`, or gateway shutdown.
- If the requirement is “run exactly when a Discord thread is archived/deleted,” add a Discord adapter thread lifecycle listener separately and map thread id to session id; do not rely on `on_session_finalize` for that immediate event.

## Required safety guards

- Set a child guard env var such as `HERMES_FEEDBACK_AUTOLOG_CHILD=1` in the child process and skip the hook when it is present, otherwise the child Hermes run can recursively trigger the same hook.
- Keep a small seen-state keyed by `session_id` to avoid duplicate child runs across multiple finalize surfaces for the same session.
- Log spawn/skip decisions to a dedicated log file.
- Provide a dry-run mode before enabling real wiki writes.
- Let the skill's own idempotency still check existing `raw/feedback/` logs before writing files.

## Verification checklist

- Plugin is enabled in `hermes plugins list` and `plugins.enabled`.
- A fresh gateway/CLI process has performed plugin discovery after enabling the plugin.
- A dry-run hook invocation logs the generated child command.
- A child-guard invocation logs a skip.
- Repeated finalize events for the same `session_id` log `already_seen` or equivalent.
- End-to-end production verification requires an actual session finalize event and then checking the plugin log, seen-state, and `$WIKI/raw/feedback/YYYY-MM-DD/`.
