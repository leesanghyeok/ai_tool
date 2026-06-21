# Session-finalize hook automation pattern

Use this reference when the user wants feedback logs harvested automatically at the end of Hermes sessions.

## Recommended integration

Prefer a Hermes user plugin that listens to the plugin lifecycle hook `on_session_finalize`, not a gateway-only hook.

Rationale:
- `on_session_finalize` is a plugin hook used across CLI and gateway session boundaries such as shutdown, `/new`, `/reset`, and gateway session expiry.
- Gateway `session:end` hooks are useful for messaging-platform automation but provide thinner context and are not the most portable surface for CLI + gateway feedback harvesting.
- The feedback logger should remain responsible for raw markdown creation, idempotency, hashing, taxonomy, and wiki paths. The hook plugin should only decide whether and when to invoke it.

## Plugin shape

Create a user plugin under:

```text
~/.hermes/plugins/feedback-session-harvester/
```

with:

```text
plugin.yaml
__init__.py
```

`plugin.yaml` should declare a plugin name and the `on_session_finalize` hook.

`__init__.py` should:
1. Register `ctx.register_hook("on_session_finalize", callback)` in `register(ctx)`.
2. In the callback, read `session_id`, `platform`, and `reason` from kwargs.
3. Skip when `session_id` is missing.
4. Skip when a recursion guard env var such as `HERMES_FEEDBACK_AUTOLOG_CHILD=1` is set.
5. Spawn a child process rather than doing long work inside the hook callback.
6. Capture stdout/stderr to a log file such as `~/.hermes/logs/feedback-session-harvester.log`.

## Child invocation

Use a one-shot Hermes child process that resumes the ending session and preloads this skill:

```bash
HERMES_FEEDBACK_AUTOLOG_CHILD=1 \
hermes --resume "$SESSION_ID" --skills feedback-ai-logging chat -q \
'Use the feedback-ai-logging skill to harvest dissatisfaction/correction/rework incidents from this resumed session. Follow the skill rules: write one immutable raw/feedback Markdown file per incident, skip duplicates, and create nothing if no qualifying incident exists. Report created/skipped/excluded counts.'
```

Keep the child prompt self-contained because it runs in a new agent process.

## Safety gates

Recommended defaults:
- Start in dry-run mode or behind `HERMES_FEEDBACK_AUTOLOG_ENABLED=1`.
- Add an allowlist for reasons such as `shutdown`, `new_session`, `reset`, and `session_expired`.
- Add a lightweight seen ledger keyed by `session_id + reason` to avoid repeated child spawns. This is only an optimization; raw log idempotency still belongs to the skill workflow.
- Never let hook failure block session shutdown. Log and return.

## Verification

Before enabling real writes:
1. Confirm the plugin appears in `hermes plugins list` after `hermes plugins enable feedback-session-harvester` and a restart/reset as needed.
2. Trigger a session boundary and verify the hook log records the session id, platform, reason, and child command or dry-run decision.
3. Run a test session with a clear correction/rework incident and verify a file appears under `raw/feedback/YYYY-MM-DD/`.
4. Trigger the same session again and verify no duplicate raw feedback file is created.
5. Check generated files for required frontmatter, controlled taxonomy values, body-only `sha256`, and one incident per file.
