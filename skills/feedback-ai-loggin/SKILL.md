---
name: feedback-ai-loggin
description: Use when recording dissatisfaction with AI or agent outputs as immutable Markdown feedback logs under an LLM Wiki raw/feedback tree, preserving raw history while capturing candidate improvement rules.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feedback, llm-wiki, evals, quality, logging]
    related_skills: [llm-wiki, rubric-design]
---

# AI Feedback Logging

## Overview

Use this skill to record a user's dissatisfaction with an AI/agent output as a structured Markdown raw source inside an LLM Wiki. The goal is not to immediately rewrite the wiki's concepts or rubrics. The goal is to preserve a clean, analyzable historical record that can later be batch-analyzed into failure taxonomies, agent rules, rubrics, and quality guides.

The feedback log is **raw data**. It belongs under `raw/feedback/`, not directly under `concepts/`, `comparisons/`, or `queries/`. Each dissatisfaction event gets one Markdown file.

The log should capture both:

1. The historical incident: what happened, why it was unsatisfactory, and what was expected.
2. Candidate learning material: a candidate agent rule and checklist items that could later be promoted during a separate analysis step.

## When to Use

Use this skill when:

- The user says an AI/agent answer was unsatisfactory and wants to record it.
- The user says “log this”, “record this failure”, “save this feedback”, or similar.
- A task result missed an explicit user requirement and the user wants the pattern remembered as feedback data.
- The user is building a feedback loop for improving future AI/agent output quality.
- The user wants a consistent Markdown format for dissatisfaction logs in an LLM Wiki.

Do not use this skill when:

- The user is merely venting and has not asked to record the incident.
- The feedback is not about an AI/agent output or workflow quality.
- The user asks to update a distilled guide, rubric, taxonomy, or concept page directly; use `llm-wiki` and/or `rubric-design` instead.
- The user asks to store a stable personal preference globally; use memory only if it is durable and appropriate.

## Storage Path

Store each log as one Markdown file at:

```text
$WIKI/raw/feedback/YYYY-MM-DD/{session_id}-{HHMMSS}-{short-slug}.md
```

Where:

- `$WIKI` is `${WIKI_PATH:-$HOME/wiki}` unless the user specifies another wiki path.
- `YYYY-MM-DD` is the local date of log creation.
- `session_id` is the best available conversation/session/thread identifier.
- `HHMMSS` is local 24-hour time.
- `short-slug` is a short English lowercase summary of the failure, using hyphens.

## Session Identifier Discovery

Keep the identifier rule runtime-agnostic: `session_id` should be the best available conversation, session, or thread identifier for the environment currently running the skill. Do not assume a specific agent runtime such as Hermes, Codex, Claude CLI, or another tool. Discover the identifier first, then fall back to `unknown-session` only after the discovery procedure finds no usable candidate.

Use this priority order:

1. **Explicit platform or user-provided identifier.** Prefer a concrete source identifier when the feedback comes from a platform or linked artifact, such as a Discord thread id, Telegram topic id, GitHub issue/PR/comment thread id, browser URL, chat permalink, or an id the user explicitly provides.
2. **Runtime-provided session variables.** Inspect the current execution environment for session-like variables. Look for known names when available, such as `HERMES_SESSION_ID`, `CODEX_SESSION_ID`, or `CLAUDE_SESSION_ID`, and also for generic patterns like `*_SESSION_ID`, `*_CONVERSATION_ID`, `*_THREAD_ID`, or `*_CHAT_ID`. Use only values actually present in the current environment; do not invent or assume them.
3. **Runtime metadata or status commands.** If the active CLI/runtime exposes a safe status command or non-secret metadata file containing the current session/conversation id, use it. Avoid reading secrets, credentials, tokens, or unrelated private state just to find an id.
4. **Fallback.** Use `unknown-session` only when no explicit platform id, runtime environment value, or safe runtime metadata value is available.

When an id is discovered, record its source in `source_ref` when useful, for example `discord-thread:<id>`, `github-pr:<owner>/<repo>#<number>`, `cli-session:hermes:<id>`, `cli-session:codex:<id>`, `cli-session:claude:<id>`, or `cli-session:env:<variable-name>`. If no id is discoverable, use a source reference such as `cli:no-session-id-discovered` rather than leaving the reason ambiguous.

Examples:

```text
raw/feedback/2026-06-01/1517194335987306506-143210-missing-published-dates.md
raw/feedback/2026-06-01/1517194335987306506-151002-no-test-verification.md
raw/feedback/2026-06-02/unknown-session-092015-missing-decision-criteria.md
```

## Raw Data Principles

Feedback logs under `raw/feedback/` are raw source material. Follow these rules:

1. **One incident, one file.** Do not append unrelated feedback events into a single file.
2. **Preserve history.** The file records what happened at the time of logging.
3. **Do not store processing state in the raw file.** Do not add `status`, `triage_status`, `derived_pages`, `converted_to_rule`, `converted_to_rubric`, or similar processing fields.
4. **Do not record promotion decisions in the raw file.** Later analysis, triage, or promotion into `concepts/`, `queries/`, or rubrics belongs in a separate management or analysis document.
5. **Candidate rules are allowed.** `Candidate Agent Rule` and `Candidate Checklist Items` are part of the incident interpretation at capture time, not processing state. Include them when useful.
6. **Do not create concept pages for individual incidents.** Individual incidents stay in `raw/feedback/`; repeated patterns may later be promoted.

## Required Frontmatter

Every feedback log must start with YAML frontmatter:

```yaml
---
type: feedback-log
source_type: ai-dissatisfaction
source_platform: discord
source_ref: ""
session_id: ""
ingested: YYYY-MM-DD
created_at: YYYY-MM-DDTHH:MM:SS+09:00
task_type: research
agent_or_model: ""
severity: high
categories: [evidence, freshness]
sha256: "<body-sha256>"
---
```

### Field Rules

| Field | Required | Meaning |
|---|---:|---|
| `type` | yes | Always `feedback-log` |
| `source_type` | yes | Always `ai-dissatisfaction` for this skill |
| `source_platform` | yes | Source surface such as `discord`, `cli`, `github`, `web`, `local`, or `unknown` |
| `source_ref` | no | Link, thread id, message reference, file path, runtime session source, or other source pointer if available |
| `session_id` | yes | Best available session/thread/conversation id; run Session Identifier Discovery before using `unknown-session` |
| `ingested` | yes | Date the log is written into the wiki |
| `created_at` | yes | Precise local timestamp for the log |
| `task_type` | yes | Controlled task type; see below |
| `agent_or_model` | no | Agent, model, or tool involved, if known |
| `severity` | yes | `low`, `medium`, `high`, or `critical` |
| `categories` | yes | One or more failure categories from the taxonomy |
| `sha256` | yes | SHA-256 hash of the Markdown body after the closing frontmatter |

## Task Type Taxonomy

Use one of these values for `task_type`:

```text
research
coding
recommendation
summarization
planning
automation
review
translation
conversation
other
```

If none fits, use `other` and describe the task in the `Situation` section.

## Failure Category Taxonomy

Use one or more of these values for `categories`:

```text
requirement-miss       Explicit user requirement was missed
evidence               Sources, citations, or evidence were absent or weak
freshness              Publication date, update date, or currentness was missing or weak
verification           Execution, testing, validation, or tool-backed checking was missing
specificity            Output was too generic for the user's context
decision-criteria      Recommendation lacked explicit decision criteria
format                 Requested structure or output format was not followed
tone                   Tone, style, or language did not match the user's expectation
context-misread        User intent, context, or constraints were misunderstood
overconfidence         Uncertain information was stated too confidently
hallucination          Output contained false, fabricated, or unsupported claims
actionability          Output lacked concrete next steps or operational guidance
verbosity              Output was too long or buried the answer
insufficient-detail    Output was too short, shallow, or under-explained
```

If a new category is needed repeatedly, add it deliberately in a later taxonomy update rather than inventing many one-off labels.

## Severity Rules

Use the lowest severity that honestly describes the incident.

```text
low:
- Mostly preference, tone, wording, or minor structure issue.
- Output was usable but disappointing.

medium:
- Some important requirement was missing.
- Output needed revision but was not fundamentally unreliable.
- Decision criteria, specificity, or actionability were weak.

high:
- A core requirement was missed.
- Important evidence, freshness, or verification was absent.
- Output could not be trusted for the intended decision without substantial rework.
- The same failure type is likely to recur if not captured.

critical:
- Fabricated source, fabricated tool result, or serious hallucination.
- Dangerous execution, unauthorized change, data loss, security, privacy, or cost risk.
- Error could plausibly cause real user harm if followed.
```

## Markdown Body Template

Use this body after frontmatter. Keep the sections stable so later analysis can parse them.

````markdown
# Feedback Log: {Title}

## Situation

- Task type: {task_type}
- User wanted: {what the user expected or requested}
- Agent actually did: {what the AI/agent output or workflow did}

## Dissatisfaction

{Describe what was unsatisfactory. Be concrete.}

## Expected Behavior

{Describe what should have happened instead.}

## Evidence

{Quote or summarize the relevant user request, agent response, command result, or artifact. Use short excerpts rather than whole transcripts unless necessary.}

```text
{optional excerpt}
```

## Failure Categories

- {category-1}
- {category-2}

## Severity

{low | medium | high | critical}

Reason:
- {Why this severity is appropriate.}

## Candidate Agent Rule

{A concise candidate rule that could prevent this failure in future. This is not a processing status and does not mean the rule has been promoted.}

> {one-sentence rule}

## Candidate Checklist Items

- [ ] {Observable check item 1}
- [ ] {Observable check item 2}
````

## Filename Slug Rules

Generate `short-slug` as follows:

1. Use English lowercase words.
2. Use 3-6 words when possible.
3. Separate words with hyphens.
4. Prefer the failure pattern over the domain.
5. Avoid personally identifying details.

Good slugs:

```text
missing-published-dates
no-test-verification
missing-decision-criteria
overconfident-unsupported-claim
ignored-output-format
```

Bad slugs:

```text
bad-answer
user-was-annoyed
that-discord-thing
failure
```

## Hashing Rule

The `sha256` field should be computed over the Markdown body only: everything after the closing frontmatter delimiter.

Recommended procedure:

1. Draft the body first.
2. Compute SHA-256 over the exact body string.
3. Insert the hash into frontmatter.
4. Write the file.

This follows the LLM Wiki raw-source pattern: frontmatter describes the source, while the hash verifies the raw body content.

## Language Policy

- In Korean-language conversations, write the human-readable feedback log body in Korean by default.
- Keep machine/tool-facing frontmatter keys, controlled enum values, category labels, slugs, file paths, and hashes in their required English formats.
- Section headings in the body may be Korean when the user is Korean; preserve the same semantic sections so later analysis can still parse the incident.

## Workflow

1. **Identify the wiki path.** Use `${WIKI_PATH:-$HOME/wiki}` unless the user specifies a path.
2. **Create date directory.** Ensure `raw/feedback/YYYY-MM-DD/` exists.
3. **Discover identifiers.** Determine `session_id`, `HHMMSS`, and `short-slug`. For `session_id`, run the runtime-agnostic Session Identifier Discovery procedure before falling back to `unknown-session`.
4. **Classify lightly.** Pick `task_type`, `severity`, and `categories` from the controlled taxonomies.
5. **Write the incident body.** Focus on situation, dissatisfaction, expected behavior, and evidence.
6. **Add candidate learning.** Include a candidate agent rule and checklist items when there is a clear preventable pattern.
7. **Compute `sha256`.** Hash body only.
8. **Write one Markdown file.** Do not update concept/rubric pages unless the user separately asks for promotion or analysis.
9. **Report the created path.** Tell the user where the log was saved and summarize the captured categories/severity.

## Example

Path:

```text
raw/feedback/2026-06-01/1517194335987306506-143210-missing-published-dates.md
```

Content:

````markdown
---
type: feedback-log
source_type: ai-dissatisfaction
source_platform: discord
source_ref: "discord-thread"
session_id: "1517194335987306506"
ingested: 2026-06-01
created_at: 2026-06-01T14:32:10+09:00
task_type: research
agent_or_model: "hermes"
severity: high
categories: [evidence, freshness]
sha256: "8f1f0f2adf3b6d4f0bbf6e9c35d2d4a4100d1dcf3c39d7d8752f0a2a00000000"
---
# Feedback Log: Research Answer Missing Published Dates

## Situation

- Task type: research
- User wanted: A research summary about AI quality feedback loops with evidence links and publication times.
- Agent actually did: Provided a methodology summary with links, but publication dates were not consistently attached to every key source.

## Dissatisfaction

The answer did not consistently satisfy the explicit requirement to include publication times with the evidence links.

## Expected Behavior

Each key source should include title, link, publication or update date, and a short note explaining which claim it supports.

## Evidence

```text
User request included: "근거 링크와, 해당 내용의 발행시간들도 같이 적어주고"
```

## Failure Categories

- evidence
- freshness

## Severity

high

Reason:
- The missing publication dates were an explicit requirement and directly affected research trustworthiness.

## Candidate Agent Rule

> In research answers where the user requests evidence links and publication times, every key source should include both the link and the publication/update date.

## Candidate Checklist Items

- [ ] Every key source has a URL.
- [ ] Every key source has a publication or update date, or the absence is explicitly noted.
- [ ] Each source is tied to the claim it supports.
````

## Common Pitfalls

1. **Putting raw incidents into `concepts/`.** Individual dissatisfaction events belong under `raw/feedback/`; only repeated patterns should later become concept pages or rubrics.
2. **Adding processing state to the raw file.** Do not add status, triage, derived-page, or promotion fields to frontmatter.
3. **Using only `session_id.md`.** This collides when multiple feedback logs are recorded in one session. Include time and slug.
4. **Using vague categories.** Prefer controlled category labels so later analysis can aggregate logs.
5. **Skipping expected behavior.** A complaint without the desired behavior is much harder to convert into a useful rule.
6. **Skipping candidate rule/checklist.** When the preventable pattern is clear, capture it while context is fresh.
7. **Hashing the whole file.** Hash only the body, not the frontmatter.
8. **Promoting immediately by default.** Logging and promotion are separate workflows; only promote when the user asks for analysis or guide/rubric updates.
9. **Hard-coding one agent runtime for session ids.** This skill is shared across Hermes, Codex, Claude CLI, and other environments. Do not fix missing `session_id` by assuming one runtime-specific variable. Preserve the generic `session_id` rule and add/execute a discovery procedure that checks platform ids, runtime env vars, and safe metadata before using `unknown-session`.

## Verification Checklist

Before reporting completion, verify:

- [ ] File path matches `raw/feedback/YYYY-MM-DD/{session_id}-{HHMMSS}-{short-slug}.md`.
- [ ] Frontmatter starts at byte 0 and contains all required fields.
- [ ] No processing-status or promotion fields are present.
- [ ] `task_type` is from the task type taxonomy.
- [ ] `severity` is one of `low`, `medium`, `high`, `critical`.
- [ ] `categories` are from the failure category taxonomy.
- [ ] Body includes `Situation`, `Dissatisfaction`, `Expected Behavior`, `Evidence`, `Failure Categories`, `Severity`, `Candidate Agent Rule`, and `Candidate Checklist Items`.
- [ ] `sha256` was computed over the body only.
- [ ] `session_id` was chosen through the Session Identifier Discovery procedure, without assuming a specific runtime.
- [ ] If `unknown-session` is used, explicit platform ids, runtime environment variables, and safe runtime metadata/status sources were checked first.
- [ ] `source_ref` records the id source when an id is discovered, or records that no session id was discoverable.
- [ ] The final response gives the user the created path and a one-line summary of severity/categories.
