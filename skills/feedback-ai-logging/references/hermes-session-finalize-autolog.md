# Hermes session-finalize feedback autolog pattern

Use this reference when the user wants feedback logs harvested automatically at the end of Hermes sessions.

## Recommended architecture

Do not make a session-end hook write `raw/feedback/` Markdown directly. Instead:

1. Create a user plugin under `~/.hermes/plugins/<name>/`.
2. Register `ctx.register_hook("on_session_finalize", callback)`.
3. In the callback, quickly spawn a child Hermes one-shot and return.
4. Run the child with `--resume <session_id>` and `--skills feedback-ai-logging`.
5. Let the `feedback-ai-logging` skill perform incident detection, deduplication, frontmatter generation, body hashing, and wiki writes.

Canonical command shape:

```bash
HERMES_FEEDBACK_AUTOLOG_CHILD=1 \
hermes --resume "$SESSION_ID" \
  --skills feedback-ai-logging \
  chat --source feedback-autolog \
  -q 'feedback-ai-logging 스킬을 사용해 resume된 현재 Hermes 세션의 feedback 사건을 수확하세요. 중복이면 새 파일을 만들지 말고, 근거 부족/비실패이면 기록하지 마세요.'
```

## Why this is safer than direct file writes

- The hook remains a small trigger and does not duplicate the skill's rules.
- Feedback classification stays LLM-assisted and uses the resumed session context.
- Idempotency, controlled taxonomy, frontmatter, and body-only `sha256` stay in one place.
- A slow or failing child process does not block core session finalization.
- Future improvements to this skill automatically improve autolog behavior.

## Required guards

- Recursion guard: child env `HERMES_FEEDBACK_AUTOLOG_CHILD=1`; callback returns immediately if set.
- Missing-session guard: skip empty/`None`/`unknown-session` ids.
- Duplicate guard: maintain a small state file keyed by `session_id` so multiple finalize surfaces do not spawn duplicate child runs.
- Reason allowlist: default to Hermes lifecycle reasons such as `shutdown`, `new_session`, `session_expired`, `reset`, `manual_reset`; allow env override only when needed.
- Logging: append JSONL records to `~/.hermes/logs/<plugin>.log` for `dry_run`, `spawn_start`, `spawned`, and `skip` events.
- Dry-run mode: support an env such as `HERMES_FEEDBACK_AUTOLOG_DRY_RUN=1` for validation before real wiki writes.

## Discord thread lifecycle caveat

`on_session_finalize` is a Hermes session lifecycle hook, not a Discord native thread-close hook.

It fires when Hermes finalizes the session because of events such as `/new`, `/reset`, idle/daily expiry, or gateway shutdown. A Discord thread archive/close/delete does not necessarily finalize the Hermes session immediately unless the Discord adapter explicitly maps that platform event to session finalization.

If the user asks for "on Discord thread close immediately", add a separate Discord adapter/platform event path:

1. Listen for Discord thread archive/delete/update events.
2. Map the Discord `thread_id` plus parent channel/chat id to the Hermes session key/session_id.
3. Invoke the same finalize/autolog path idempotently.
4. Keep this distinct from generic `on_session_finalize` so non-Discord session lifecycle remains stable.

## Verification checklist

- Plugin appears in `hermes plugins list --plain --no-bundled` as enabled.
- Plugin manager loads it with `hooks=1` and `error=None`.
- Dry-run hook invocation logs the exact child command without writing wiki files.
- Child guard invocation logs `reason=child_guard` and does not spawn.
- Duplicate finalize calls for the same `session_id` log `already_seen` after the first run.
- If gateway is already running, restart is required before Discord/gateway sessions see the new plugin.
