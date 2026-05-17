# AI Tool

Codex plugin containing PR workflow skills.

## Contents

- `pr-review`: review current branch PR and post structured GitHub review comments.
- `pr-review-apply`: inspect existing PR review feedback, apply approved changes, verify, and reply to review threads.

## Plugin Manifest

This repository is a Codex plugin root.

- Manifest: `.codex-plugin/plugin.json`
- Skills path: `./codex/skills/`

## Install

Use this repository as a local or Git-backed Codex plugin source:

```text
git@github.com:leesanghyeok/ai_tool.git
```

After installation, invoke skills by name:

```text
Use $pr-review to review the current branch PR.
Use $pr-review-apply to apply current PR review feedback.
```

## Legacy Symlink Install

For environments that use `CODEX_HOME/skills` directly:

```bash
./codex/scripts/link_codex_skills.sh
```
